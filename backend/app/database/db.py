import os
from threading import Lock
from typing import Any, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure


class MongoDBManager:
    """Unified MongoDB connection manager providing both sync and async access."""

    def __init__(self):
        self._sync_client: Optional[MongoClient] = None
        self._async_client: Optional[AsyncIOMotorClient] = None
        self._mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
        self._db_name = "cephalon_onni"
        self._lock = Lock()
        self._initialized = False

    def initialize(self):
        """Initialize both sync and async clients."""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            # Initialize sync client
            try:
                self._sync_client = MongoClient(
                    self._mongo_url, serverSelectionTimeoutMS=5000
                )
                self._sync_client.admin.command("ping")
                print(f"Successfully connected to MongoDB at {self._mongo_url}")
            except ConnectionFailure as e:
                print(f"Failed to connect to MongoDB: {e}")
                raise

            # Initialize async client
            try:
                self._async_client = AsyncIOMotorClient(self._mongo_url)
            except Exception as e:
                print(f"Failed to connect to MongoDB (async): {e}")
                raise

            self._initialized = True

    @property
    def sync_client(self) -> MongoClient:
        """Get synchronous MongoDB client."""
        if not self._initialized:
            self.initialize()
        if self._sync_client is None:
            raise RuntimeError("Failed to initialize sync client")
        return self._sync_client

    @property
    def async_client(self) -> AsyncIOMotorClient:
        """Get asynchronous MongoDB client."""
        if not self._initialized:
            self.initialize()
        if self._async_client is None:
            raise RuntimeError("Failed to initialize async client")
        return self._async_client

    @property
    def sync_db(self):
        """Get synchronous database instance."""
        return self.sync_client[self._db_name]

    @property
    def async_db(self):
        """Get asynchronous database instance."""
        return self.async_client[self._db_name]

    # Sync collections
    @property
    def sync_users(self):
        return self.sync_db["users"]

    @property
    def sync_inventories(self):
        return self.sync_db["inventories"]

    @property
    def sync_builds(self):
        return self.sync_db["builds"]

    # Async collections
    @property
    def users(self):
        return self.async_db["users"]

    @property
    def inventories(self):
        return self.async_db["inventories"]

    @property
    def builds(self):
        return self.async_db["builds"]

    def get_sync_collection(self, name: str):
        """Get a synchronous collection by name."""
        return self.sync_db[name]

    def get_async_collection(self, name: str):
        """Get an asynchronous collection by name."""
        return self.async_db[name]

    def close_all(self):
        """Close all connections."""
        if self._sync_client:
            self._sync_client.close()
        if self._async_client:
            self._async_client.close()
        self._initialized = False


# Global instance
db_manager = MongoDBManager()

# Compatibility exports for existing code
client = db_manager.sync_client
db = db_manager.sync_db
users_collection = db_manager.sync_users
inventories_collection = db_manager.sync_inventories
builds_collection = db_manager.sync_builds


# Sync helper functions (from db_helpers.py)
def connect_to_mongodb(mongo_uri: Optional[str] = None) -> Optional[MongoClient]:
    """Connect to MongoDB using the unified manager."""
    if mongo_uri:
        db_manager._mongo_url = mongo_uri
        db_manager._initialized = False
    try:
        return db_manager.sync_client
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None


def list_databases(client: Optional[MongoClient] = None) -> List[str]:
    """List all databases in the MongoDB instance."""
    if client is None:
        client = db_manager.sync_client
    databases = client.list_database_names()
    print(f"\nAvailable databases: {', '.join(databases)}")
    return databases


def list_collections(
    client: Optional[MongoClient] = None, db_name: Optional[str] = None
) -> List[str]:
    """List all collections in a specific database."""
    if client is None:
        client = db_manager.sync_client
    if db_name is None:
        db_name = db_manager._db_name

    if db_name not in client.list_database_names():
        print(f"Database '{db_name}' does not exist")
        return []

    db_instance = client[db_name]
    collections = db_instance.list_collection_names()
    print(f"\nCollections in '{db_name}': {', '.join(collections)}")
    return collections


def get_collection_stats(
    client: Optional[MongoClient] = None,
    db_name: Optional[str] = None,
    collection_name: Optional[str] = None,
) -> dict:
    """Get statistics for a specific collection."""
    if client is None:
        client = db_manager.sync_client
    if db_name is None:
        db_name = db_manager._db_name
    if collection_name is None:
        return {}

    try:
        db_instance = client[db_name]
        collection = db_instance[collection_name]

        stats = {"count": collection.count_documents({}), "size": 0, "avg_obj_size": 0}

        # Get detailed stats if available
        try:
            coll_stats = db_instance.command("collStats", collection_name)
            stats.update(
                {
                    "size": coll_stats.get("size", 0),
                    "avg_obj_size": coll_stats.get("avgObjSize", 0),
                }
            )
        except Exception as e:
            print(f"[Error] Error getting collection stats: {e}")

        return stats
    except Exception as e:
        print(f"Error getting collection stats: {e}")
        return {}


def describe_collection(
    client: Optional[MongoClient] = None,
    db_name: Optional[str] = None,
    collection_name: Optional[str] = None,
) -> None:
    """Describe a MongoDB collection with statistics and sample schema."""
    if client is None:
        client = db_manager.sync_client
    if db_name is None:
        db_name = db_manager._db_name
    if collection_name is None:
        return

    stats = get_collection_stats(client, db_name, collection_name)

    print(f"\n--- {collection_name} ({stats.get('count', 0)} documents) ---")
    if stats.get("size", 0) > 0:
        print(f"  Size: {stats['size'] / 1024:.2f} KB")
        print(f"  Avg document size: {stats.get('avg_obj_size', 0)} bytes")

    # Get sample document to show schema
    try:
        db_instance = client[db_name]
        collection = db_instance[collection_name]
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


def preview_collection(
    client: Optional[MongoClient] = None,
    db_name: Optional[str] = None,
    collection_name: Optional[str] = None,
    limit: int = 10,
) -> None:
    """Preview documents from a MongoDB collection."""
    if client is None:
        client = db_manager.sync_client
    if db_name is None:
        db_name = db_manager._db_name
    if collection_name is None:
        return

    try:
        db_instance = client[db_name]
        collection = db_instance[collection_name]

        documents = list(collection.find().limit(limit))

        if not documents:
            print("  [EMPTY]")
            return

        print(f"  Preview (showing {len(documents)} documents):")
        for i, doc in enumerate(documents, 1):
            print(f"    Document {i}: {doc}")

    except Exception as e:
        print(f"Error previewing collection: {e}")


def does_value_exists(
    client: Optional[MongoClient] = None,
    db_name: Optional[str] = None,
    collection_name: Optional[str] = None,
    field: Optional[str] = None,
    value: Optional[Any] = None,
) -> bool:
    """Check if a value exists in a MongoDB collection field."""
    if client is None:
        client = db_manager.sync_client
    if db_name is None:
        db_name = db_manager._db_name
    if collection_name is None or field is None or value is None:
        return False

    try:
        db_instance = client[db_name]
        collection = db_instance[collection_name]
        count = collection.count_documents({field: value})
        return count > 0
    except Exception as e:
        print(f"Error checking value existence: {e}")
        return False


def get_value_by_field(
    client: Optional[MongoClient] = None,
    db_name: Optional[str] = None,
    collection_name: Optional[str] = None,
    lookup_field: Optional[str] = None,
    lookup_value: Optional[Any] = None,
    return_field: str = "_id",
) -> Optional[Any]:
    """Get a specific field value from a MongoDB document by lookup field."""
    if client is None:
        client = db_manager.sync_client
    if db_name is None:
        db_name = db_manager._db_name
    if collection_name is None or lookup_field is None or lookup_value is None:
        return None

    try:
        db_instance = client[db_name]
        collection = db_instance[collection_name]

        doc = collection.find_one(
            {lookup_field: lookup_value}, {return_field: 1, "_id": 0}
        )
        return doc.get(return_field) if doc else None
    except Exception as e:
        print(f"Error getting value by field: {e}")
        return None


def drop_collections(
    client: Optional[MongoClient] = None,
    db_name: Optional[str] = None,
    collections: Optional[List[str]] = None,
    confirm: bool = True,
) -> None:
    """Drop MongoDB collections with optional confirmation."""
    if client is None:
        client = db_manager.sync_client
    if db_name is None:
        db_name = db_manager._db_name
    if collections is None:
        return

    try:
        db_instance = client[db_name]

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

            db_instance[collection_name].drop()
            print(f"[DROPPED] {collection_name}")

    except Exception as e:
        print(f"[ERROR] While dropping collections: {e}")


def get_server_status(client: Optional[MongoClient] = None) -> dict:
    """Get MongoDB server status information."""
    if client is None:
        client = db_manager.sync_client
    try:
        return client.admin.command("serverStatus")
    except Exception as e:
        print(f"Error getting server status: {e}")
        return {}


def describe_table(
    client: Optional[MongoClient] = None,
    table_name: Optional[str] = None,
    db_name: str = "cephalon_onni",
) -> None:
    """Legacy compatibility function for describe_collection."""
    if table_name is None:
        return
    describe_collection(client, db_name, table_name)


def preview_table(
    client: Optional[MongoClient] = None,
    table_name: Optional[str] = None,
    limit: int = 10,
    db_name: str = "cephalon_onni",
) -> None:
    """Legacy compatibility function for preview_collection."""
    if table_name is None:
        return
    preview_collection(client, db_name, table_name, limit)


def list_tables(
    client: Optional[MongoClient] = None, db_name: str = "cephalon_onni"
) -> List[str]:
    """Legacy compatibility function for list_collections."""
    return list_collections(client, db_name)


def drop_tables(
    client: Optional[MongoClient] = None,
    tables: Optional[List[str]] = None,
    confirm: bool = True,
    db_name: str = "cephalon_onni",
) -> None:
    """Legacy compatibility function for drop_collections."""
    drop_collections(client, db_name, tables, confirm)
