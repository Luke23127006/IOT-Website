# app/__init__.py
import json
import os
from flask import Flask
from dotenv import load_dotenv

from app.services.mongo_service import mongo
from app.services.mqtt_service import mqtt

mqtt.last_cmd = None   

def create_app():
    load_dotenv()

    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), "templates"),
                static_folder=os.path.join(os.path.dirname(__file__), "static"))

    app.secret_key = os.getenv("SECRET_KEY")

    # ===== Config từ .env =====
    app.config["MONGO_URI"]          = os.getenv("MONGO_URI")
    app.config["MQTT_BROKER_URL"]    = os.getenv("MQTT_BROKER_URL", "localhost")
    app.config["MQTT_BROKER_PORT"]   = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    app.config["MQTT_TOPIC_CONFIG"]  = os.getenv("MQTT_TOPIC", "/unique/config")

    # ===== Init services =====
    mongo.init_app(app)
    mqtt.init_app(app)

    TOPIC_BUZZER_ST = "/unique/buzzer"

    def on_buzzer(topic, payload: str):
        s = payload.strip().upper()
        if s not in ("ON", "OFF"):
            return

        # cache để debug (tuỳ thích)
        mqtt.buzzer_state = s

        # --- cập nhật MongoDB ---
        # Cách 1: nếu bạn có device_id cố định (khuyên dùng)
        mongo.db.devices.update_one({"device_id": "ESP32-001"},
                                    {"$set": {"sound": (s == "ON"),
                                            }})

    mqtt.subscribe(TOPIC_BUZZER_ST, on_buzzer)
    
    # ===== Register blueprints =====
    from app.routes.routes import main
    from app.routes.auth_route import auth
    app.register_blueprint(main)
    app.register_blueprint(auth)
    
    return app
