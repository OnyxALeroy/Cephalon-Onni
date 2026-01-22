from models.static_models import Warframe
from pymongo import MongoClient
from pymongo.errors import PyMongoError


def create_warframe_database(
    client: MongoClient, db_name: str = "cephalon_onni"
) -> bool:
    """Create warframes and warframe_abilities collections in MongoDB."""
    try:
        db = client[db_name]

        # Create warframes collection with index
        warframes_collection = db["warframes"]
        warframes_collection.create_index("uniqueName", unique=True)

        # Create warframe_abilities collection with compound index
        abilities_collection = db["warframe_abilities"]
        abilities_collection.create_index(
            [("warframe_uniqueName", 1), ("abilityUniqueName", 1)], unique=True
        )

        print("✅ Created warframes and warframe_abilities collections")
        return True
    except PyMongoError as e:
        print(f"[ERROR] While creating warframe database: {e}")
        return False


def fill_warframe_db(
    client: MongoClient, warframes: list[Warframe], db_name: str = "cephalon_onni"
) -> bool:
    """Fill warframes and warframe_abilities collections with data."""
    try:
        db = client[db_name]
        warframes_collection = db["warframes"]
        abilities_collection = db["warframe_abilities"]

        warframe_docs = []
        ability_docs = []

        for warframe in warframes:
            # Warframe document
            warframe_doc = {
                "uniqueName": warframe["uniqueName"],
                "name": warframe["name"],
                "parentName": warframe.get("parentName"),
                "description": warframe["description"],
                "health": warframe["health"],
                "shield": warframe["shield"],
                "armor": warframe["armor"],
                "stamina": warframe["stamina"],
                "power": warframe["power"],
                "codexSecret": warframe["codexSecret"],
                "masteryReq": warframe["masteryReq"],
                "sprintSpeed": warframe["sprintSpeed"],
                "passiveDescription": warframe.get("passiveDescription"),
                "exalted": warframe.get("exalted", []),
                "productCategory": warframe["productCategory"],
            }
            warframe_docs.append(warframe_doc)

            # Abilities documents
            abilities = warframe.get("abilities", [])
            if not isinstance(abilities, list):
                print(
                    f"[ERROR] abilities is not a list: {type(abilities)} for warframe {warframe.get('uniqueName', 'unknown')}"
                )
                continue

            for ability in abilities:
                ability_doc = {
                    "warframe_uniqueName": warframe["uniqueName"],
                    "abilityUniqueName": ability.get("abilityUniqueName", ""),
                    "abilityName": ability.get("abilityName", ""),
                    "description": ability.get("description", ""),
                }
                ability_docs.append(ability_doc)

        # Insert warframes
        if warframe_docs:
            warframes_collection.insert_many(warframe_docs)
            print(f"✅ Inserted {len(warframe_docs)} warframes")

        # Insert abilities
        if ability_docs:
            abilities_collection.insert_many(ability_docs)
            print(f"✅ Inserted {len(ability_docs)} warframe abilities")

        return True
    except KeyError as ke:
        print(f"[ERROR] While loading warframe database: key error {ke}")
        return False
    except PyMongoError as e:
        print(f"[ERROR] While loading warframe database: {e}")
        return False
