from models.static_models import ImgItem
from pymongo import MongoClient
from pymongo.errors import PyMongoError


def create_images_database(client: MongoClient, db_name: str = "cephalon_onni") -> bool:
    """Create images collection in MongoDB."""
    try:
        db = client[db_name]

        # Create collection with index
        collection = db["images"]

        # Create unique index on uniqueName
        collection.create_index("uniqueName", unique=True)

        print("✅ Created images collection")
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

        documents = []
        for item in items:
            doc = {
                "uniqueName": item.get("uniqueName"),
                "imageURL": item.get("textureLocation"),
            }
            documents.append(doc)

        if documents:
            collection.insert_many(documents)
            print(f"✅ Inserted {len(documents)} images")

        return True
    except KeyError as ke:
        print(f"[ERROR] While loading image database: {ke}")
        return False
    except PyMongoError as e:
        print(f"[ERROR] While loading image database: {e}")
        return False
