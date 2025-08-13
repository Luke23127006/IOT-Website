# app/routes/mq2_api.py
import datetime
from flask import Blueprint, request, jsonify
from app.models.mq2_data import get_latest_mq2_data, get_latest_point, get_latest_ppm
from app.services.predict import predict_ppm_interval

mq2_api = Blueprint("mq2_api", __name__, url_prefix="/api/mq2")

@mq2_api.route("/history")
def mq2_history():
    device_id = request.args.get("device_id", "ESP32-001")
    try:
        limit = int(request.args.get("limit", "20"))
    except ValueError:
        limit = 20
    docs = get_latest_mq2_data(device_id=device_id, limit=limit)
    # trả về gọn gàng cho chart
    return jsonify({
        "labels": [f"{d.get('time','')} {d.get('date','')}" for d in docs],
        "ppm":    [d.get("ppm", 0) for d in docs],
        "lastTs": docs[-1]["ts"] if docs else None
    })

@mq2_api.route("/latest")
def mq2_latest():
    device_id = request.args.get("device_id", "ESP32-001")
    doc = get_latest_point(device_id=device_id) or {}
    return jsonify(doc)

@mq2_api.route("/predict")
def mq2_predict():
    try:
        horizon = int(request.args.get("horizon", 10))  # số điểm dự đoán
        window = int(request.args.get("window", 30))
        k = float(request.args.get("k", 2.0))
        yellow = float(request.args.get("yellow", 400.0))
        red = float(request.args.get("red", 500.0))

        # Lấy ppm mới nhất
        ppm = get_latest_ppm(limit=max(window, 30))
        if not ppm:
            return jsonify({"labels": [], "mid": []})

        # Giá trị hiện tại (ppm cuối cùng)
        current_ppm = ppm[-1]

        # Gọi hàm dự đoán cho horizon điểm
        preds = predict_ppm_interval(
            ppm,
            horizon=horizon,
            window=window,
            k=k,
            yellow_threshold=yellow,
            red_threshold=red
        )

        # Nhãn trục X: Now + các mốc mỗi 10s
        labels = ["Now"] + [f"+{i*10}s" for i in range(1, horizon + 1)]

        # mid: điểm đầu là giá trị hiện tại, tiếp theo là dự đoán
        mid_values = [round(current_ppm, 2)] + [
            round((lo + hi) / 2.0, 2) for lo, hi, _, _ in preds
        ]

        return jsonify({"labels": labels, "mid": mid_values})
    except Exception as e:
        return jsonify({"error": str(e)}), 500