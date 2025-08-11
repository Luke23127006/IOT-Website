# app/models/mq2_data.py
from pymongo import DESCENDING
from app.services.mongo_service import mongo

def _coll():
    return mongo.db.mq2_data

def create_mq2_data(raw: int, ppm: float, level: str, date: str, time: str, ts: int, device_id: str = "ESP32-001"):
    last_doc = _coll().find_one(
        {"device_id": device_id},
        sort=[("ts", DESCENDING)]
    )
    # Nếu đã có và ts trùng -> bỏ qua
    if last_doc and last_doc.get("ts") == ts:
        return None  # hoặc return {"status": "duplicate"}
    
    print("Creating MQ2 data:", {
        "device_id": device_id,
        "raw": raw,
        "ppm": ppm,
        "level": level,
        "date": date,
        "time": time,
        "ts": ts,
    })

    doc = {
        "device_id": device_id,
        "raw": raw,
        "ppm": ppm,
        "level": level,
        "date": date,
        "time": time,
        "ts": ts,  # epoch ms từ ESP32/NTP
    }
    return _coll().insert_one(doc)


def get_latest_mq2_data(device_id: str = "ESP32-001", limit: int = 10):
    if limit == 1:
        return get_latest_point(device_id)
    
    cur = (_coll()
           .find({"device_id": device_id}, {"_id": 0})  # loại _id cho sạch JSON
           .sort("ts", DESCENDING)
           .limit(limit))
    # trả về theo thứ tự thời gian tăng dần để vẽ line chart
    return list(cur)[::-1]

def get_latest_point(device_id: str = "ESP32-001"):
    doc = (_coll()
           .find_one({"device_id": device_id}, {"_id": 0}, sort=[("ts", DESCENDING)]))
    return doc