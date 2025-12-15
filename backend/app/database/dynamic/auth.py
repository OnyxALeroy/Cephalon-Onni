from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "looking cool joker"
ALGORITHM = "HS256"
EXP_MINUTES = 60

def create_token(data: dict):
    expiry = datetime.now() + timedelta(minutes=EXP_MINUTES)
    data["exp"] = expiry
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])