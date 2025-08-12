# app/__init__.py
import json
import os
from flask import Flask
from dotenv import load_dotenv

from app.services.mongo_service import mongo
from app.services.mqtt_service import mqtt

from app.models.mq2_data import create_mq2_data
from app.models.off_all_request import create_off_all_request_data

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
    app.config["MQTT_TOPIC_CONFIG"]  = os.getenv("MQTT_TOPIC", "/23127006_23127179_23127189/config")

    # ===== Init services =====
    mongo.init_app(app)
    mqtt.init_app(app)

    TOPIC_BUZZER = "/23127006_23127179_23127189/buzzer"
    TOPIC_YELLOWLED = "/23127006_23127179_23127189/yellowled"
    TOPIC_REDLED = "/23127006_23127179_23127189/redled"
    TOPIC_MQ2 = "/23127006_23127179_23127189/mq2"
    TOPIC_BUTTON = "/23127006_23127179_23127189/button"

    def on_mq2(topic, payload: str):
        data = json.loads(payload)
        create_mq2_data(**data)

    def on_button(topic, pyaload: str):
        data = json.loads(pyaload)
        create_off_all_request_data(**data)
        
    # def on_buzzer(topic, payload: str):
    #     s = payload.strip().upper()
    #     if s not in ("ON", "OFF"):
    #         return

    #     # cache để debug (tuỳ thích)
    #     mqtt.buzzer_state = s

    #     # --- cập nhật MongoDB ---
    #     # Cách 1: nếu bạn có device_id cố định (khuyên dùng)
    #     mongo.db.devices.update_one({"device_id": "ESP32-001"},
    #                                 {"$set": {"sound": (s == "ON"),
    #                                         }})

    mqtt.subscribe(TOPIC_MQ2, on_mq2)
    mqtt.subscribe(TOPIC_BUTTON, on_button)
    # mqtt.subscribe(TOPIC_BUZZER, on_buzzer)
    # mqtt.subscribe(TOPIC_YELLOWLED, on_buzzer)
    # mqtt.subscribe(TOPIC_REDLED, on_buzzer)
    
    # from app.models.device import create_device
    # from app.models.user import get_user_id_by_email
    # create_device("ESP32-001", "006_179_189", get_user_id_by_email("trannguyenkhailuanqng02@gmail.com"))
    
    # ===== Register blueprints =====
    from app.routes.routes import main
    from app.routes.auth_route import auth
    from app.routes.chatbot_route import chatbot_bp
    from app.routes.dashboard_route import mq2_api
    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(mq2_api)
    
    return app
