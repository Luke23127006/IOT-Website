# app/__init__.py
import json
import os
import time
from flask import Flask
from dotenv import load_dotenv

from app.services.mongo_service import mongo
from app.services.mqtt_service import mqtt
from app.services.mail_service import mail
from app.services.mail_service import send_alert

from app.models.mq2_data import create_mq2_data, _coll as mq2_coll
from app.models.off_all_request import create_off_all_request_data
from app.models.user import get_all_emails

mqtt.last_cmd = None
_last_email_sent: dict[str, int] = {}  

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
    
    def asbool(x):  # tiny helper
        return str(x).lower() in ("1","true","yes","on")

    app.config["MAIL_SERVER"]=os.getenv("MAIL_SERVER", "smtp.gmail.com")
    app.config["MAIL_PORT"]=int(os.getenv("MAIL_PORT", "465"))
    app.config["MAIL_USE_SSL"]=asbool(os.getenv("MAIL_USE_SSL", "true"))
    app.config["MAIL_USERNAME"]=os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"]=os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"]=os.getenv("MAIL_DEFAULT_SENDER", "Me <no-reply@example.com>")
    app.config["ALERT_TO"] = os.getenv("ALERT_TO", "")
    app.config["ALERT_COOLDOWN_MIN"] = int(os.getenv("ALERT_COOLDOWN_MIN", "5"))

    # ===== Init services =====
    mongo.init_app(app)
    mail.init_app(app)

    TOPIC_BUZZER = "/23127006_23127179_23127189/buzzer"
    TOPIC_YELLOWLED = "/23127006_23127179_23127189/yellowled"
    TOPIC_REDLED = "/23127006_23127179_23127189/redled"
    TOPIC_MQ2 = "/23127006_23127179_23127189/mq2"
    TOPIC_BUTTON = "/23127006_23127179_23127189/button"

    def on_mq2(topic, payload: str):
        with app.app_context():
            try:
                data = json.loads(payload)
            except Exception:
                return
            
            create_mq2_data(**data)

            device_id = data.get("device_id", "ESP32-001")
            ts = int(data.get("ts", 0))
            level = (data.get("level") or "").upper()

            if level == "DANGER":
                # Rising-edge: previous record not DANGER
                prev = mq2_coll().find_one(
                    {"device_id": device_id, "ts": {"$lt": ts}},
                    sort=[("ts", -1)]
                )
                entering_danger = (not prev) or (prev.get("level") != "DANGER")

                # Cooldown
                now = int(time.time())
                cooldown = int(app.config.get("ALERT_COOLDOWN_MIN", 5)) * 60
                last = _last_email_sent.get(device_id, 0)
                cool_ok = (now - last) >= cooldown

                if entering_danger and cool_ok:
                    _last_email_sent[device_id] = now
                    try:
                        emails = get_all_emails()
                    except Exception as e:
                        app.logger.error(f"get_all_emails() failed: {e}")
                        emails = []

                    subject = f"[ALERT] GAS DANGER — {data.get('ppm')} ppm"
                    html = f"""
                        <h2>GAS DANGER detected</h2>
                        <ul>
                        <li>PPM: {data.get('ppm')}</li>
                        <li>Level: {level}</li>
                        <li>Time: {data.get('date')} {data.get('time')}</li>
                        <li>TS: {ts}</li>
                        </ul>
                    """
                    for email in emails:
                        try:
                            send_alert(subject, html, [email])
                        except Exception as e:
                            app.logger.error(f"Send mail to {email} failed: {e}")

    def on_button(topic, payload: str):
        with app.app_context():
            try:
                data = json.loads(payload)
            except Exception as e:
                return
        
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

    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
        mqtt.init_app(app)
        mqtt.subscribe(TOPIC_MQ2, on_mq2)
        mqtt.subscribe(TOPIC_BUTTON, on_button)
    
    return app
