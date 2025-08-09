from bson import ObjectId
from ..extensions import mongo

def _coll():
    return mongo.db.users

def get_user_by_username(username: str):
    return _coll().find_one({"username": username})

def get_user_by_id(user_id: str | None):
    if not user_id:
        return None
    return _coll().find_one({"_id": ObjectId(user_id)})

def create_user(username: str, email: str, password_hash: str):
    return _coll().insert_one({
        "username": username,
        "email": email,
        "password": password_hash
    })

def update_username(user_id, new_username):
    return _coll().update_one({"_id": ObjectId(user_id)}, {"$set": {"username": new_username}})

def update_email(user_id, new_email):
    return _coll().update_one({"_id": ObjectId(user_id)}, {"$set": {"email": new_email}})
