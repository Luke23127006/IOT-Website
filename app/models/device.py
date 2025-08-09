from bson import ObjectId
from ..extensions import mongo

def _coll():
    return mongo.db.devices

def create_device(device_id: str, device_name: str, user_id: str):
    return _coll().insert_one({
        "_id": ObjectId(device_id),
        "device_name": device_name,
        "user_id": ObjectId(user_id),
        "warning_threshold": 180,              # keep as int or float consistently
        "danger_threshold": 200,
        "sound": True,
        "yellow_led": True,
        "red_led": True
    })

# If you want to fetch by Mongo _id
def get_device_by_mongo_id(mongo_id: str | None):
    if not mongo_id:
        return None
    return _coll().find_one({"_id": ObjectId(mongo_id)})

# If you want to fetch by your hardware/device_id
def get_device_by_device_id(device_id: str | None):
    if not device_id:
        return None
    return _coll().find_one({"device_id": device_id})

def set_device_owner(device_id: str, user_id: str):
    return _coll().update_one(
        {"device_id": device_id},
        {"$set": {"user_id": ObjectId(user_id)}}
    )

def get_device_by_user_id(user_id: str):
    if not user_id:
        return None
    return _coll().find_one({"user_id": ObjectId(user_id)})

# Provide an update with a proper filter (choose one of these)

def update_device_by_device_id(device_id: str, *,
                               device_name: str | None = None,
                               warning_threshold: float | None = None,
                               danger_threshold: float | None = None,
                               sound: bool | None = None,
                               yellow_led: bool | None = None,
                               red_led: bool | None = None):
    updates = {}
    if device_name is not None: updates["device_name"] = device_name
    if warning_threshold is not None: updates["warning_threshold"] = warning_threshold
    if danger_threshold is not None: updates["danger_threshold"] = danger_threshold
    if sound is not None: updates["sound"] = sound
    if yellow_led is not None: updates["yellow_led"] = yellow_led
    if red_led is not None: updates["red_led"] = red_led
    if not updates:
        return None
    return _coll().update_one({"device_id": device_id}, {"$set": updates})

def update_device_by_mongo_id(mongo_id: str, updates: dict):
    if not updates:
        return None
    return _coll().update_one({"_id": ObjectId(mongo_id)}, {"$set": updates})