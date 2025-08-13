import numpy as np
from typing import Sequence

def predict_ppm_interval(
    ppm: Sequence[float],
    horizon: int = 10,
    window: int = 30,
    k: float = 2.0,
    *,
    yellow_threshold: float,
    red_threshold: float
) -> np.ndarray:
    """
    Dự đoán khoảng (min, max) cho 'horizon' ngày tiếp theo từ chuỗi ppm quá khứ,
    đồng thời ước lượng tỉ lệ phần khoảng (giả định phân bố đều trong [min, max])
    nằm trên các ngưỡng yellow/red.

    Trả về
    ------
    np.ndarray, shape = (horizon, 4)
        Mỗi hàng: [min, max, p_gt_yellow, p_gt_red],
        trong đó p_gt_* là tỉ lệ phần đoạn của [min,max] nằm trên ngưỡng (0..1).
        *Không* phải xác suất thống kê; chỉ là giả định uniform trên khoảng dự báo.
    """
    if red_threshold < yellow_threshold:
        raise ValueError("red_threshold phải ≥ yellow_threshold.")

    arr = np.asarray(ppm, dtype=float)
    n = arr.size
    if n == 0:
        raise ValueError("ppm trống.")

    # Cửa sổ gần nhất
    ws = int(min(window, n))
    t = np.arange(n)
    tw = t[-ws:]
    yw = arr[-ws:]

    # Ước lượng xu hướng tuyến tính + độ lệch
    if ws >= 3 and np.all(np.isfinite(yw)):
        m, b = np.polyfit(tw, yw, 1)  # y ≈ m*t + b
        yhat = m * tw + b
        resid = yw - yhat
        med = np.median(resid)
        mad = np.median(np.abs(resid - med))
        s = 1.4826 * mad
        if not np.isfinite(s) or s == 0.0:
            s = resid.std(ddof=1) if ws > 1 else (0.1 * abs(yw[-1]) + 1e-6)
    else:
        m, b = 0.0, arr[-1]
        s = arr.std(ddof=1) if n > 1 else (0.1 * abs(arr[-1]) + 1e-6)

    def frac_above(thresh: float, lo: float, hi: float) -> float:
        # Tỉ lệ phần đoạn của [lo, hi] lớn hơn thresh (giả định uniform)
        if hi <= lo:  # khoảng suy biến
            return 1.0 if lo > thresh else 0.0
        if lo > thresh:
            return 1.0
        if hi < thresh:
            return 0.0
        return (hi - thresh) / (hi - lo)

    # Dự báo + tạo khoảng
    out = np.empty((horizon, 4), dtype=float)
    for h in range(1, horizon + 1):
        t_h = (n - 1) + h
        f = m * t_h + b
        widen = np.sqrt(1.0 + (h / max(ws, 1)))   # bất định tăng nhẹ theo h
        width = k * s * widen
        lo = max(0.0, f - width)
        hi = f + width
        p_y = frac_above(yellow_threshold, lo, hi)
        p_r = frac_above(red_threshold, lo, hi)
        out[h - 1] = [lo, hi, p_y, p_r]

    return out

# # Ví dụ :
# ppm = [110, 120, 125, 130, 129, 140, 138, 142, 145, 150]
# intervals = predict_ppm_interval(
#     ppm, horizon=10, window=7, k=2.0,
#     yellow_threshold=100.0, red_threshold=150.0
# )
# print(intervals)  # mỗi dòng: [min, max, p_gt_yellow, p_gt_red]
