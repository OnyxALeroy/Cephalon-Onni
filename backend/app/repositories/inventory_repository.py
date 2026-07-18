from typing import List, Optional

from bson import ObjectId
from database.db import db_manager


class InventoryRepository:
    @staticmethod
    async def find_by_user(user_id: str) -> List[dict]:
        cursor = db_manager.inventories.find({"user_id": ObjectId(user_id)})
        return [item async for item in cursor]

    @staticmethod
    async def find_by_id_and_user(item_id: str, user_id: str) -> Optional[dict]:
        return await db_manager.inventories.find_one(
            {"_id": ObjectId(item_id), "user_id": ObjectId(user_id)}
        )
