from pymongo import MongoClient
from pymongo.errors import PyMongoError


def create_item_database(client: MongoClient, db_name: str = "cephalon_onni") -> bool:
    """Create items collection in MongoDB."""
    try:
        db = client[db_name]

        # Create collection with index
        collection = db["items"]

        # Create unique index on uniqueName
        collection.create_index("uniqueName", unique=True)

        print("✅ Created items collection")
        return True
    except PyMongoError as e:
        print(f"[ERROR] While creating item database: {e}")
        return False
