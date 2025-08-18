from flask import Blueprint, jsonify
from app import mongo

from ..models.device import get_device_by_device_id
from ..utils.decorators import api_login_required
from app.services.mqtt_service import mqtt
from ..config import MQTT_TOPIC

alert_bp = Blueprint("alert", __name__, url_prefix="/api/alert")

@alert_bp.route("/off_all_alert/confirm", methods=["POST"])
@api_login_required
def off_all_alert_confirm():
    device = get_device_by_device_id("ESP32-001")
    if not device:
        return jsonify({"ok": False, "error": "No device"}), 400

    # 1) Cập nhật DB
    mongo.db.devices.update_one(
        {"_id": device["_id"]},
        {"$set": {"sound": False, "yellowled": False, "redled": False}}
    )
    
    mqtt.publish(MQTT_TOPIC + "/buzzer", "OFF")
    mqtt.publish(MQTT_TOPIC + "/yellowled", "OFF")
    mqtt.publish(MQTT_TOPIC + "/redled", "OFF")

    return jsonify({"ok": True})

@alert_bp.route("/off_all_alert/cancel", methods=["POST"])
@api_login_required
def off_all_alert_cancel():
    # Không làm gì, chỉ để client biết là đã hủy
    return jsonify({"ok": True})