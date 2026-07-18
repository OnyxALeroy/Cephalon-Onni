from database.db import connect_to_mongodb, does_value_exists


class WeaponRepository:
    """Queries MongoDB static collections for build validation."""

    @staticmethod
    async def exists(unique_name: str) -> bool:
        client = connect_to_mongodb()
        if not client:
            return False
        return does_value_exists(client, "cephalon_onni", "weapons", "uniqueName", unique_name)

    @staticmethod
    def find_by_unique_name_sync(unique_name: str):
        client = connect_to_mongodb()
        if not client:
            return None
        db = client["cephalon_onni"]
        return db["weapons"].find_one({"uniqueName": unique_name})

    @staticmethod
    def find_all_basic() -> list:
        client = connect_to_mongodb()
        if not client:
            return []
        db = client["cephalon_onni"]
        return list(
            db["weapons"].find(
                {},
                {"_id": 0, "uniqueName": 1, "name": 1, "masteryReq": 1, "productCategory": 1},
            )
        )
