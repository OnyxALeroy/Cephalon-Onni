from database.dynamic.db import users_collection
from models.users import UserCreate
from database.dynamic.security import hash_password

async def create_user(user: UserCreate):
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise ValueError("Email already registered")

    doc = {
        "email": user.email,
        "username": user.username,
        "hashed_password": hash_password(user.password),
        "role": user.role.value if hasattr(user.role, 'value') else user.role
    }

    res = await users_collection.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc

async def get_user_by_email(email: str):
    return await users_collection.find_one({"email": email})
