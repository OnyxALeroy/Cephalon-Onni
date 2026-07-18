from database.db import connect_to_mongodb, does_value_exists


class ModRepository:
    """Queries MongoDB static collections for build validation."""

    @staticmethod
    async def exists(unique_name: str) -> bool:
        client = connect_to_mongodb()
        if not client:
            return False
        return does_value_exists(client, "cephalon_onni", "mods", "uniqueName", unique_name)

    @staticmethod
    def find_all_basic() -> list:
        client = connect_to_mongodb()
        if not client:
            return []
        db = client["cephalon_onni"]
        return list(
            db["mods"].find(
                {},
                {"_id": 0, "uniqueName": 1, "name": 1, "type": 1, "rarity": 1, "polarity": 1},
            )
        )


class ArcaneRepository:
    """Queries MongoDB static collections for build validation."""

    @staticmethod
    async def exists(unique_name: str) -> bool:
        client = connect_to_mongodb()
        if not client:
            return False
        return does_value_exists(client, "cephalon_onni", "arcanes", "uniqueName", unique_name)

    @staticmethod
    def find_by_unique_name_sync(unique_name: str):
        client = connect_to_mongodb()
        if not client:
            return None
        db = client["cephalon_onni"]
        return db["arcanes"].find_one({"uniqueName": unique_name})

    @staticmethod
    def find_all_basic() -> list:
        client = connect_to_mongodb()
        if not client:
            return []
        db = client["cephalon_onni"]
        return list(
            db["arcanes"].find({}, {"_id": 0, "uniqueName": 1, "name": 1, "rarity": 1})
        )
