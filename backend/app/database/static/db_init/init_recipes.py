from models.static_models import Recipe
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError

from database.db import get_value_by_field


def create_recipe_database(client: MongoClient, db_name: str = "cephalon_onni") -> bool:
    """Create recipes collection in MongoDB."""
    try:
        db = client[db_name]

        collection = db["recipes"]
        collection.create_index("uniqueName", unique=True)

        print("Created recipes collection")
        return True
    except PyMongoError as e:
        print(f"[ERROR] While creating recipe database: {e}")
        return False


def fill_recipes_db(
    client: MongoClient, recipes: list[Recipe], db_name: str = "cephalon_onni"
) -> bool:
    """Fill recipes collection with data."""
    try:
        db = client[db_name]
        collection = db["recipes"]

        ops = []
        for recipe in recipes:
            # Ingredients
            ingredients = recipe.get("ingredients", [])
            ingredient_data = []

            for i, ingredient in enumerate(ingredients):
                ingredient_data.append(
                    {
                        "item_type": ingredient.get("ItemType"),
                        "item_count": ingredient.get("ItemCount", 0),
                        "item_id": get_value_by_field(
                            client,
                            db_name,
                            "items",
                            "uniqueName",
                            ingredient.get("uniqueName"),
                            "_id",
                        ),
                    }
                )

            # Create document
            doc = {
                "uniqueName": recipe.get("uniqueName"),
                "build_price": recipe.get("buildPrice", 0),
                "build_time": recipe.get("buildTime", 0),
                "skip_build_time_price": recipe.get("skipBuildTimePrice", 0),
                "consume_on_use": recipe.get("consumeOnUse", True),
                "produced_amount": recipe.get("num", 1),
                "codex_secret": recipe.get("codexSecret", False),
                "result_type": recipe.get("resultType"),
                "result_id": get_value_by_field(
                    client,
                    db_name,
                    "items",
                    "uniqueName",
                    recipe.get("resultType"),
                    "_id",
                ),
                "ingredients": ingredient_data,
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
            print(f"Upserted {len(ops)} recipes")

        return True
    except PyMongoError as e:
        print(f"[ERROR] While loading recipe database: {e}")
        return False
