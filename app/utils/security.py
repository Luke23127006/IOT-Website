from werkzeug.security import check_password_hash, generate_password_hash

def hash_password(pw: str) -> str:
    return generate_password_hash(pw)

def verify_password(hashed: str, pw: str) -> bool:
    return check_password_hash(hashed, pw)
