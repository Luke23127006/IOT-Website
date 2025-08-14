from typing import Sequence, Optional
import math, random

def predict_ppm_interval(
    ppm: Sequence[float],
    horizon: int = 10,
    window: int = 30,
    k: float = 2.0,
    *,
    yellow_threshold: float = 400.0,
    red_threshold: float = 500.0,
    # --- NEW: điều khiển độ “khác nhau” giữa các bước ---
    jitter_mode: str = "deterministic",  # "none" | "deterministic" | "random"
    jitter_scale: float = 0.25,          # biên độ jitter trung tâm ~ jitter_scale * s
    width_wobble: float = 0.10,          # biên độ dao động độ rộng (tỷ lệ)
    period: Optional[int] = None,        # chu kỳ jitter cho "deterministic" (mặc định theo horizon)
    random_state: Optional[int] = None   # seed cho "random"
) -> list:
    if red_threshold < yellow_threshold:
        raise ValueError("red_threshold phải ≥ yellow_threshold.")

    arr = [float(x) for x in ppm]
    n = len(arr)
    if n == 0:
        raise ValueError("ppm trống.")

    ws = int(min(window, n))
    t = list(range(n))
    tw = t[-ws:]
    yw = arr[-ws:]

    def is_finite(x):
        return x == x and x != float('inf') and x != float('-inf')

    def all_finite(seq):
        return all(is_finite(x) for x in seq)

    # Linear fit (least squares) + ước lượng nhiễu robust
    if ws >= 3 and all_finite(yw):
        mean_tw = sum(tw) / ws
        mean_yw = sum(yw) / ws
        num = sum((tw[i] - mean_tw) * (yw[i] - mean_yw) for i in range(ws))
        den = sum((tw[i] - mean_tw) ** 2 for i in range(ws))
        m = num / den if den != 0 else 0.0
        b = mean_yw - m * mean_tw
        yhat = [m * tw[i] + b for i in range(ws)]
        resid = [yw[i] - yhat[i] for i in range(ws)]
        med = sorted(resid)[ws // 2] if ws % 2 == 1 else \
            0.5 * (sorted(resid)[ws // 2 - 1] + sorted(resid)[ws // 2])
        mad_list = [abs(r - med) for r in resid]
        mad = sorted(mad_list)[ws // 2] if ws % 2 == 1 else \
            0.5 * (sorted(mad_list)[ws // 2 - 1] + sorted(mad_list)[ws // 2])
        s = 1.4826 * mad
        if not is_finite(s) or s == 0.0:
            mean_resid = sum(resid) / ws
            s = (sum((r - mean_resid) ** 2 for r in resid) / (ws - 1)) ** 0.5 if ws > 1 else (0.1 * abs(yw[-1]) + 1e-6)
    else:
        m, b = 0.0, arr[-1]
        mean_arr = sum(arr) / n
        s = (sum((x - mean_arr) ** 2 for x in arr) / (n - 1)) ** 0.5 if n > 1 else (0.1 * abs(arr[-1]) + 1e-6)

    # Helpers
    def frac_above(thresh: float, lo: float, hi: float) -> float:
        if hi <= lo:
            return 1.0 if lo > thresh else 0.0
        if lo > thresh:
            return 1.0
        if hi < thresh:
            return 0.0
        return (hi - thresh) / (hi - lo)

    # NEW: setup jitter
    if jitter_mode not in ("none", "deterministic", "random"):
        raise ValueError("jitter_mode phải là 'none' | 'deterministic' | 'random'.")

    P = period or max(6, min(12, horizon))  # chu kỳ mặc định
    rng = random.Random(random_state) if jitter_mode == "random" else None

    out = []
    for h in range(1, horizon + 1):
        t_h = (n - 1) + h
        f = m * t_h + b

        # độ rộng cơ bản (tăng dần theo h)
        widen = (1.0 + (h / max(ws, 1))) ** 0.5
        base_width = k * s * widen

        # --- NEW: áp jitter ---
        if jitter_mode == "deterministic":
            # dao động “nhẹ nhàng”, lặp lại theo chu kỳ
            delta_center = jitter_scale * s * math.sin(2 * math.pi * h / P)
            width_scale = 1.0 + width_wobble * math.cos(2 * math.pi * h / P)
        elif jitter_mode == "random":
            # dao động ngẫu nhiên có seed (nếu cung cấp)
            delta_center = jitter_scale * s * (rng.gauss(0, 1))
            width_scale = max(0.6, 1.0 + width_wobble * rng.uniform(-1, 1))
        else:
            delta_center = 0.0
            width_scale = 1.0

        f_j = f + delta_center
        width = max(1e-9, base_width * width_scale)

        lo = max(0.0, f_j - width)
        hi = f_j + width

        p_y = frac_above(yellow_threshold, lo, hi)
        p_r = frac_above(red_threshold, lo, hi)
        out.append([lo, hi, p_y, p_r])

    return out


