from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from database.db import db_manager


class BuildRepository:
    @staticmethod
    async def find_by_id(build_id: str, user_id: str) -> Optional[dict]:
        return await db_manager.builds.find_one(
            {"_id": ObjectId(build_id), "user_id": user_id}
        )

    @staticmethod
    async def find_by_user(
        user_id: str, skip: int = 0, limit: int = 30
    ) -> List[dict]:
        cursor = (
            db_manager.builds.find({"user_id": user_id})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        return [build async for build in cursor]

    @staticmethod
    async def count_by_user(user_id: str) -> int:
        return await db_manager.builds.count_documents({"user_id": user_id})

    @staticmethod
    async def count_all() -> int:
        return await db_manager.builds.count_documents({})

    @staticmethod
    async def create(build_doc: dict) -> dict:
        result = await db_manager.builds.insert_one(build_doc)
        build_doc["_id"] = result.inserted_id
        return build_doc

    @staticmethod
    async def update(
        build_id: str, user_id: str, update_data: dict
    ) -> Optional[dict]:
        update_data["updated_at"] = datetime.now()
        await db_manager.builds.update_one(
            {"_id": ObjectId(build_id), "user_id": user_id},
            {"$set": update_data},
        )

    @staticmethod
    async def delete(build_id: str, user_id: str) -> bool:
        try:
            result = await db_manager.builds.delete_one(
                {"_id": ObjectId(build_id), "user_id": user_id}
            )
            return result.deleted_count > 0
        except Exception:
            return False
