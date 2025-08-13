# app/models/device.py
from datetime import datetime
from bson import ObjectId
from ..services.mongo_service import mongo

def _coll():
    return mongo.db.devices

def ensure_indexes():
    _coll().create_index("device_id", unique=True)
    _coll().create_index("user_id")

def create_device(device_id: str, device_name: str, user_id: str | ObjectId):
    doc = {
        "device_id": device_id,                  # <- lưu uid ở field này
        "device_name": device_name,
        "user_id": ObjectId(user_id) if isinstance(user_id, str) else user_id,
        "ppm_value": 0,
        "warning_threshold": 400,
        "danger_threshold": 500,
        "sound": True,
        "yellowled": True,
        "redled": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    # chỉ tạo nếu chưa có
    return _coll().update_one(
        {"device_id": device_id},
        {"$setOnInsert": doc},
        upsert=True
    )

def get_device_by_user_id(user_id):
    uid = ObjectId(user_id) if isinstance(user_id, str) else user_id
    return _coll().find_one({"user_id": uid})

def get_device_by_device_id(device_id: str):
    return _coll().find_one({"device_id": device_id})

def update_device_by_mongo_id(mongo_id: str | ObjectId, updates: dict):
    _id = ObjectId(mongo_id) if isinstance(mongo_id, str) else mongo_id
    if not updates: return None
    updates["updated_at"] = datetime.utcnow()
    return _coll().update_one({"_id": _id}, {"$set": updates})

def get_ppm_value_by_device_id(device_id: str):
    device = get_device_by_device_id(device_id)
    if not device:
        return None
    return device.get("ppm_value", 0)