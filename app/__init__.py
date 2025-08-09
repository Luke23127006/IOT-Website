# app/__init__.py
import os
from flask import Flask
from dotenv import load_dotenv
from app.extensions import mongo

def create_app():
    # Load biến môi trường từ .env
    load_dotenv()

    base_dir = os.path.abspath(os.path.dirname(__file__))

    app = Flask(__name__,
                template_folder=os.path.join(base_dir, "templates"),
                static_folder=os.path.join(base_dir, "static"))
    
    app.secret_key = os.getenv("SECRET_KEY")

    # Cấu hình MongoDB URI từ file .env
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")

    # Khởi tạo kết nối MongoDB
    mongo.init_app(app)

    # Import và đăng ký blueprint
    from app.routes.routes import main
    from app.routes.auth_route import auth
    app.register_blueprint(main)
    app.register_blueprint(auth)

    return app
