from pymongo import MongoClient
from pymongo.errors import PyMongoError


def create_translation_database(
    client: MongoClient, db_name: str = "cephalon_onni"
) -> bool:
    """Create translations collection in MongoDB."""
    try:
        db = client[db_name]

        # Create collection with index
        collection = db["translations"]

        # Create compound index for id and language
        collection.create_index([("id", 1), ("language", 1)], unique=True)

        print("Created translations collection")
        return True
    except PyMongoError as e:
        print(f"[ERROR] While creating translation database: {e}")
        return False
