from typing import List, Optional

from database.db import connect_to_mongodb


class WarframeRepository:
    """Queries MongoDB static collections for build validation and enrichment."""

    @staticmethod
    def _get_collection():
        client = connect_to_mongodb()
        if not client:
            return None, None
        db = client["cephalon_onni"]
        return db["warframes"], db["warframe_abilities"]

    @staticmethod
    async def exists(unique_name: str) -> bool:
        from database.db import does_value_exists

        client = connect_to_mongodb()
        if not client:
            return False
        return does_value_exists(client, "cephalon_onni", "warframes", "uniqueName", unique_name)

    @staticmethod
    def find_by_unique_name_sync(unique_name: str) -> Optional[dict]:
        warframes, _ = WarframeRepository._get_collection()
        if warframes is None:
            return None
        return warframes.find_one({"uniqueName": unique_name})

    @staticmethod
    def find_abilities_sync(warframe_unique_name: str) -> list:
        _, abilities = WarframeRepository._get_collection()
        if abilities is None:
            return []
        return list(
            abilities.find(
                {"warframe_uniqueName": warframe_unique_name},
                {"_id": 0, "abilityUniqueName": 1, "abilityName": 1, "description": 1},
            )
        )

    @staticmethod
    def find_all_basic() -> List[dict]:
        warframes, _ = WarframeRepository._get_collection()
        if warframes is None:
            return []
        return list(
            warframes.find({}, {"_id": 0, "uniqueName": 1, "name": 1, "masteryReq": 1})
        )
