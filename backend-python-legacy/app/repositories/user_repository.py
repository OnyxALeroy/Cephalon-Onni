from typing import List, Optional

from bson import ObjectId
from database.db import db_manager


class UserRepository:
    @staticmethod
    async def find_by_id(user_id: str) -> Optional[dict]:
        return await db_manager.users.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    async def find_by_email(email: str) -> Optional[dict]:
        return await db_manager.users.find_one({"email": email})

    @staticmethod
    async def create(user_data: dict) -> dict:
        result = await db_manager.users.insert_one(user_data)
        user_data["_id"] = result.inserted_id
        return user_data

    @staticmethod
    async def update_role(user_id: str, role: str) -> bool:
        result = await db_manager.users.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"role": role}}
        )
        return result.modified_count > 0

    @staticmethod
    async def delete(user_id: str) -> bool:
        result = await db_manager.users.delete_one({"_id": ObjectId(user_id)})
        return result.deleted_count > 0

    @staticmethod
    async def find_all() -> List[dict]:
        cursor = db_manager.users.find({})
        return [user async for user in cursor]
