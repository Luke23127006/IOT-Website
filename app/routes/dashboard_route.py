# app/routes/mq2_api.py
from flask import Blueprint, request, jsonify
from app.models.mq2_data import get_latest_mq2_data, get_latest_point

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
