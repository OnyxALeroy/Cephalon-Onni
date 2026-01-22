from typing import Any, List, Optional

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# ----------------------------------------------------------------------------------------------------------------------
# MongoDB DB Inspection
# ----------------------------------------------------------------------------------------------------------------------


def connect_to_mongodb(
    mongo_uri: str = "mongodb://cephalon-onni-mongo:27017",
) -> Optional[MongoClient]:
    """Connect to MongoDB using environment variables or default Docker setup."""
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # Test the connection
        client.admin.command("ping")
        print(f"✅ Successfully connected to MongoDB at {mongo_uri}")
        return client
    except ConnectionFailure as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None


def list_mongodb_databases(client: MongoClient) -> List[str]:
    """List all databases in the MongoDB instance."""
    databases = client.list_database_names()
    print(f"\n📋 Available databases: {', '.join(databases)}")
    return databases


def list_mongodb_collections(client: MongoClient, db_name: str) -> List[str]:
    """List all collections in a specific database."""
    if db_name not in client.list_database_names():
        print(f"❌ Database '{db_name}' does not exist")
        return []

    db = client[db_name]
    collections = db.list_collection_names()
    print(f"\n📁 Collections in '{db_name}': {', '.join(collections)}")
    return collections


def get_collection_stats(
    client: MongoClient, db_name: str, collection_name: str
) -> dict:
    """Get statistics for a specific collection."""
    try:
        db = client[db_name]
        collection = db[collection_name]

        stats = {"count": collection.count_documents({}), "size": 0, "avg_obj_size": 0}

        # Get detailed stats if available
        try:
            coll_stats = db.command("collStats", collection_name)
            stats.update(
                {
                    "size": coll_stats.get("size", 0),
                    "avg_obj_size": coll_stats.get("avgObjSize", 0),
                }
            )
        except:
            pass

        return stats
    except Exception as e:
        print(f"❌ Error getting collection stats: {e}")
        return {}


def describe_mongodb_collection(
    client: MongoClient, db_name: str, collection_name: str
) -> None:
    """Describe a MongoDB collection with statistics and sample schema."""
    stats = get_collection_stats(client, db_name, collection_name)

    print(f"\n--- {collection_name} ({stats.get('count', 0)} documents) ---")
    if stats.get("size", 0) > 0:
        print(f"  Size: {stats['size'] / 1024:.2f} KB")
        print(f"  Avg document size: {stats.get('avg_obj_size', 0)} bytes")

    # Get sample document to show schema
    try:
        db = client[db_name]
        collection = db[collection_name]
        sample_doc = collection.find_one()

        if sample_doc:
            print("  Schema fields:")
            for key, value in sample_doc.items():
                value_type = type(value).__name__
                sample_value = (
                    str(value)[:30] + "..." if len(str(value)) > 30 else value
                )
                print(f"    {key}: {value_type} (example: {sample_value})")
        else:
            print("  [EMPTY COLLECTION]")
    except Exception as e:
        print(f"  Error getting sample document: {e}")


def preview_mongodb_collection(
    client: MongoClient, db_name: str, collection_name: str, limit: int = 10
) -> None:
    """Preview documents from a MongoDB collection."""
    try:
        db = client[db_name]
        collection = db[collection_name]

        documents = list(collection.find().limit(limit))

        if not documents:
            print("  [EMPTY]")
            return

        print(f"  Preview (showing {len(documents)} documents):")
        for i, doc in enumerate(documents, 1):
            print(f"    Document {i}: {doc}")

    except Exception as e:
        print(f"❌ Error previewing collection: {e}")


def mongodb_value_exists(
    client: MongoClient, db_name: str, collection_name: str, field: str, value: Any
) -> bool:
    """Check if a value exists in a MongoDB collection field."""
    try:
        db = client[db_name]
        collection = db[collection_name]
        count = collection.count_documents({field: value})
        return count > 0
    except Exception as e:
        print(f"❌ Error checking value existence: {e}")
        return False


def get_mongodb_value_by_field(
    client: MongoClient,
    db_name: str,
    collection_name: str,
    lookup_field: str,
    lookup_value: Any,
    return_field: str = "_id",
) -> Optional[Any]:
    """Get a specific field value from a MongoDB document by lookup field."""
    try:
        db = client[db_name]
        collection = db[collection_name]

        doc = collection.find_one(
            {lookup_field: lookup_value}, {return_field: 1, "_id": 0}
        )
        return doc.get(return_field) if doc else None
    except Exception as e:
        print(f"❌ Error getting value by field: {e}")
        return None


def drop_mongodb_collections(
    client: MongoClient, db_name: str, collections: List[str], confirm: bool = True
) -> None:
    """Drop MongoDB collections with optional confirmation."""
    try:
        db = client[db_name]

        for collection_name in collections:
            if confirm:
                answer = (
                    input(
                        f"Drop collection '{collection_name}' from '{db_name}'? [y/N]: "
                    )
                    .strip()
                    .lower()
                )
                if answer != "y":
                    print(f"[SKIPPED] {collection_name}")
                    continue

            db[collection_name].drop()
            print(f"[DROPPED] {collection_name}")

    except Exception as e:
        print(f"[ERROR] While dropping collections: {e}")


def get_mongodb_server_status(client: MongoClient) -> dict:
    """Get MongoDB server status information."""
    try:
        return client.admin.command("serverStatus")
    except Exception as e:
        print(f"❌ Error getting server status: {e}")
        return {}
