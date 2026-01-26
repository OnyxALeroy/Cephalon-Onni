from models.static_models import Mod
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError


def create_mods_database(client: MongoClient, db_name: str = "cephalon_onni") -> bool:
    """Create mods collection in MongoDB."""
    try:
        db = client[db_name]

        # Create collection with index
        collection = db["mods"]

        # Create unique index on uniqueName
        collection.create_index("uniqueName", unique=True)

        print("Created mods collection")
        return True
    except PyMongoError as e:
        print(f"[ERROR] While creating mods database: {e}")
        return False


def fill_mods_db(
    client: MongoClient, mods: list[Mod], db_name: str = "cephalon_onni"
) -> bool:
    """Fill mods collection with data."""
    try:
        db = client[db_name]
        collection = db["mods"]

        ops = []
        for mod in mods:
            if "upgradeEntries" in mod or "availableChallenges" in mod:
                print(f"Mod {mod['uniqueName']} (true name: {mod['name']}) is Riven")
                continue

            # Create document
            doc = {
                "uniqueName": mod["uniqueName"],
                "name": mod["name"],
                "polarity": mod["polarity"],
                "rarity": mod["rarity"],
                "type": mod.get("type"),
                "subtype": mod.get("subtype"),
                "codexSecret": mod["codexSecret"],
                "baseDrain": mod["baseDrain"],
                "fusionLimit": mod["fusionLimit"],
                "compatName": mod.get("compatName"),
                "modSet": mod.get("modSet"),
                "modSetValues": mod.get("modSetValues"),
                "isUtility": mod.get("isUtility", False),
                "description": mod.get("description"),
                "levelStats": mod.get("levelStats", []),
                "upgradeEntries": mod.get("upgradeEntries"),
                "availableChallenges": mod.get("availableChallenges"),
            }

            ops.append(
                UpdateOne(
                    {"uniqueName": doc["uniqueName"]},
                    {"$set": doc},
                    upsert=True,
                )
            )

        if ops:
            collection.bulk_write(ops, ordered=False)
            print(f"Upserted {len(ops)} mods")

        return True
    except PyMongoError as e:
        print(f"[ERROR] While loading mods database: {e}")
        return False
