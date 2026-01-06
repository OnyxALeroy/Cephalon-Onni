from sqlalchemy import text
from sqlalchemy.orm import Session

from database.static.db_helpers import get_value_by_column
from database.static.db_init.db_init_models import Recipe


def create_recipe_database(session: Session) -> bool:
    try:
        session.execute(
            text("""
        CREATE TABLE IF NOT EXISTS recipes (
            recipe_name TEXT PRIMARY KEY NOT NULL,

            build_price INTEGER NOT NULL,
            build_time INTEGER NOT NULL,
            skip_build_time_price INTEGER NOT NULL,
            consume_on_use BOOLEAN NOT NULL DEFAULT TRUE,
            produced_amount INTEGER NOT NULL DEFAULT 1,
            codex_secret BOOLEAN NOT NULL DEFAULT FALSE,

            result_id INTEGER,
            ingredient_1_id INTEGER,
            ingredient_1_quantity INTEGER NOT NULL DEFAULT 1,
            ingredient_2_id INTEGER,
            ingredient_2_quantity INTEGER NOT NULL DEFAULT 1,
            ingredient_3_id INTEGER,
            ingredient_3_quantity INTEGER NOT NULL DEFAULT 1,
            ingredient_4_id INTEGER,
            ingredient_4_quantity INTEGER NOT NULL DEFAULT 1,

            FOREIGN KEY (ingredient_1_id) REFERENCES items(id),
            FOREIGN KEY (ingredient_2_id) REFERENCES items(id),
            FOREIGN KEY (ingredient_3_id) REFERENCES items(id),
            FOREIGN KEY (ingredient_4_id) REFERENCES items(id),
            FOREIGN KEY (result_id) REFERENCES items(id)
        )""")
        )
        session.commit()
        return True
    except Exception as e:
        print(f"[ERROR] While creating recipe database: {e}")
        session.rollback()
        return False


def fill_recipes_db(session: Session, arg2: list[Recipe]) -> bool:
    try:
        recipes = arg2
        for recipe in recipes:
            # Ingredients
            ingredients = recipe.get("ingredients")
            if len(ingredients) >= 1:
                ingredient1 = get_value_by_column(
                    session, "items", "uniqueName", ingredients[0].get("ItemType"), "id"
                )
                ingredient1_q = ingredients[0].get("ItemCount")
            else:
                ingredient1 = None
                ingredient1_q = 0
            if len(ingredients) >= 2:
                ingredient2 = get_value_by_column(
                    session, "items", "uniqueName", ingredients[1].get("ItemType"), "id"
                )
                ingredient2_q = ingredients[1].get("ItemCount")
            else:
                ingredient2 = None
                ingredient2_q = 0
            if len(ingredients) >= 3:
                ingredient3 = get_value_by_column(
                    session, "items", "uniqueName", ingredients[2].get("ItemType"), "id"
                )
                ingredient3_q = ingredients[2].get("ItemCount")
            else:
                ingredient3 = None
                ingredient3_q = 0
            if len(ingredients) >= 4:
                ingredient4 = get_value_by_column(
                    session, "items", "uniqueName", ingredients[3].get("ItemType"), "id"
                )
                ingredient4_q = ingredients[3].get("ItemCount")
            else:
                ingredient4 = None
                ingredient4_q = 0

            # Insertion
            session.execute(
                text("""
               INSERT INTO recipes
               (recipe_name, build_price, build_time, skip_build_time_price, consume_on_use,
               produced_amount, codex_secret, result_id, ingredient_1_id, ingredient_1_quantity, ingredient_2_id,
               ingredient_2_quantity, ingredient_3_id, ingredient_3_quantity, ingredient_4_id, ingredient_4_quantity)
               VALUES(:recipe_name, :build_price, :build_time, :skip_build_time_price, :consume_on_use,
               :produced_amount, :codex_secret, :result_id, :ingredient_1_id, :ingredient_1_quantity, :ingredient_2_id,
               :ingredient_2_quantity, :ingredient_3_id, :ingredient_3_quantity, :ingredient_4_id, :ingredient_4_quantity)
               """),
                {
                    "recipe_name": recipe.get("uniqueName"),
                    "build_price": recipe.get("buildPrice"),
                    "build_time": recipe.get("buildTime"),
                    "skip_build_time_price": recipe.get("skipBuildTimePrice"),
                    "consume_on_use": recipe.get("consumeOnUse"),
                    "produced_amount": recipe.get("num"),
                    "codex_secret": recipe.get("codexSecret"),
                    "result_id": get_value_by_column(
                        session, "items", "uniqueName", recipe.get("resultType"), "id"
                    ),
                    "ingredient_1_id": ingredient1,
                    "ingredient_1_quantity": ingredient1_q,
                    "ingredient_2_id": ingredient2,
                    "ingredient_2_quantity": ingredient2_q,
                    "ingredient_3_id": ingredient3,
                    "ingredient_3_quantity": ingredient3_q,
                    "ingredient_4_id": ingredient4,
                    "ingredient_4_quantity": ingredient4_q,
                },
            )
        session.commit()
        return True
    except KeyError as ke:
        print(f"[ERROR] While loading recipe database: {ke}")
        session.rollback()
        return False
    except Exception as e:
        print(f"[ERROR] While loading recipe database: {e}")
        session.rollback()
        return False
