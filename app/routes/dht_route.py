# app/routes/dht_route.py
from flask import Blueprint, request, jsonify
from app.models.dht import get_latest_point

dht_api = Blueprint("dht_api", __name__, url_prefix="/api/dht")

@dht_api.route("/latest")
def dht_latest():
    device_id = request.args.get("device_id", "ESP32-001")
    doc = get_latest_point(device_id=device_id)
    if not doc:
        return jsonify({"temp": None, "ts": None})
    # chỉ trả về những field cần thiết
    return jsonify({
        "temp": doc.get("temp"),
        "ts": doc.get("ts"),
        "date": doc.get("date"),
        "time": doc.get("time"),
        "device_id": doc.get("device_id"),
    })
