# app/services/mongo_service.py
import os
from flask_pymongo import PyMongo

class MongoService:
    def __init__(self):
        self._mongo: PyMongo | None = None

    def init_app(self, app):
        # Lấy URI từ config (đã load .env trong create_app)
        uri = app.config.get("MONGO_URI")
        if not uri:
            raise RuntimeError("MONGO_URI is missing")
        self._mongo = PyMongo(app)

    @property
    def db(self):
        if not self._mongo:
            raise RuntimeError("MongoService not initialized")
        return self._mongo.db

# singleton
mongo = MongoService()
