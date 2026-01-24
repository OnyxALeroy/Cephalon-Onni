from models.static_models import ImgItem
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError


def create_images_database(client: MongoClient, db_name: str = "cephalon_onni") -> bool:
    """Create images collection in MongoDB."""
    try:
        db = client[db_name]

        # Create collection with index
        collection = db["images"]

        # Create unique index on uniqueName
        collection.create_index("uniqueName", unique=True)

        print("Created images collection")
        return True
    except PyMongoError as e:
        print(f"[ERROR] While creating image database: {e}")
        return False


def fill_img_db(
    client: MongoClient, items: list[ImgItem], db_name: str = "cephalon_onni"
) -> bool:
    """Fill images collection with data."""
    try:
        db = client[db_name]
        collection = db["images"]

        ops = []

        for item in items:
            doc = {
                "uniqueName": item.get("uniqueName"),
                "imageURL": item.get("textureLocation"),
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
            print(f"Upserted {len(ops)} images")

        return True
    except PyMongoError as e:
        print(f"[ERROR] While loading image database: {e}")
        return False
