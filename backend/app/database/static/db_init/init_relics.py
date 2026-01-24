from typing import List, Union

from models.static_models import Arcana, Relic
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError


def create_relic_database(client: MongoClient, db_name: str = "cephalon_onni") -> bool:
    """Create relics and arcane collections in MongoDB."""
    try:
        db = client[db_name]

        collection = db["relics"]
        collection.create_index("uniqueName", unique=True)

        collection = db["arcanes"]
        collection.create_index("uniqueName", unique=True)

        print("Created recipes and arcane collections")
        return True
    except PyMongoError as e:
        print(f"[ERROR] While creating relics / arcane collections: {e}")
        return False


def fill_relic_db(
    client: MongoClient,
    content: List[Union[Relic, Arcana]],
    db_name: str = "cephalon_onni",
) -> bool:
    """Fill relics and arcane collection with data."""
    try:
        relics_ops = []
        arcana_ops = []
        for element in content:
            if "relicRewards" in element:  # Then it's a Relic
                doc = {
                    "uniqueName": element.get("uniqueName"),
                    "name": element.get("name", ""),
                    "codexSecret": element.get("codexSecret", False),
                    "description": element.get("description", ""),
                    "relicRewards": element.get("relicRewards", []),
                }
                relics_ops.append(
                    UpdateOne(
                        {"uniqueName": doc["uniqueName"]},
                        {"$set": doc},
                        upsert=True,
                    )
                )
            elif "rarity" in element or "levelStats" in element:  # Then it's an Arcane
                doc = {
                    "uniqueName": element.get("uniqueName"),
                    "name": element.get("name", ""),
                    "codexSecret": element.get("codexSecret", False),
                    "rarity": element.get("rarity", None),
                    "levelStats": element.get("levelStats", []),
                }
                arcana_ops.append(
                    UpdateOne(
                        {"uniqueName": doc["uniqueName"]},
                        {"$set": doc},
                        upsert=True,
                    )
                )
            else:
                print(f"[WARN] Invalid element: {element}")
                continue

        db = client[db_name]
        if relics_ops:
            db["relics"].bulk_write(relics_ops, ordered=False)
        if arcana_ops:
            db["arcanes"].bulk_write(arcana_ops, ordered=False)

        return True
    except PyMongoError as e:
        print(f"[ERROR] While loading recipe database: {e}")
        return False
