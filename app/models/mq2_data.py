# app/models/device.py
from datetime import datetime
from bson import ObjectId
from ..services.mongo_service import mongo
from pymongo import DESCENDING

def _coll():
    return mongo.db.mq2_data

def create_mq2_data(raw: int, ppm: float, level: str, date: str, time: str, ts: int, device_id: str = "ESP32-001"):
    doc = {
        "device_id": device_id,
        "raw": raw,
        "ppm": ppm,
        "level": level,
        "date": date,
        "time": time,
        "ts": ts,
    }
    return _coll().insert_one(doc)

def get_latest_mq2_data(device_id: str = "ESP32-001", limit: int = 10):
    cursor = (_coll().find({"device_id": device_id}).sort("ts", DESCENDING).limit(limit))
    return list(cursor)[::-1]