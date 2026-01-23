from models.static_models import Mission
from pymongo import MongoClient
from pymongo.errors import PyMongoError


def create_mission_database(
    client: MongoClient, db_name: str = "cephalon_onni"
) -> bool:
    """Create missions collection in MongoDB."""
    try:
        db = client[db_name]

        # Create collection with index
        collection = db["missions"]

        # Create unique index on mission_name
        collection.create_index("mission_name", unique=True)

        print("Created missions collection")
        return True
    except PyMongoError as e:
        print(f"[ERROR] While creating mission database: {e}")
        return False


def fill_missions_db(
    client: MongoClient, missions: list[Mission], db_name: str = "cephalon_onni"
) -> bool:
    """Fill missions collection with data."""
    try:
        db = client[db_name]
        collection = db["missions"]

        documents = []
        for mission in missions:
            # Create document
            doc = {
                "mission_name": mission.get("uniqueName"),
                "faction_index": mission.get("factionIndex"),
                "mastery_req": mission.get("masteryReq"),
                "max_enemy_level": mission.get("maxEnemyLevel"),
                "min_enemy_level": mission.get("minEnemyLevel"),
                "mission_index": mission.get("missionIndex"),
                "name": mission.get("name"),
                "node_type": mission.get("nodeType"),
                "system_index": mission.get("systemIndex"),
                "system_name": mission.get("systemName"),
            }

            documents.append(doc)

        if documents:
            collection.insert_many(documents)
            print(f"Inserted {len(documents)} missions")

        return True
    except KeyError as ke:
        print(f"[ERROR] While loading mission database: {ke}")
        return False
    except PyMongoError as e:
        print(f"[ERROR] While loading mission database: {e}")
        return False
