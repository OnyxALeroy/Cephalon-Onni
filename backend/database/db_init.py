import sqlite3
from typing import Dict, List, Optional, Union

from backend.database.db_helpers import drop_tables, list_tables, describe_table, preview_table, value_exists, \
    get_value_by_column

DB_FILE = "test.db"

def load_json(path: str) -> Optional[Union[Dict, List]]:
    import json
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {path}")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON: {e}")
        return None

# ----------------------------------------------------------------------------------------------------------------------
# DB Creation
# ----------------------------------------------------------------------------------------------------------------------

def create_translation_database(conn: sqlite3.Connection) -> bool:
    try:
        conn.cursor().execute("""
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER NOT NULL,            
            language TEXT NOT NULL,
            value TEXT NOT NULL,
            PRIMARY KEY (id, language)
        )""")
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] While creating translation database: {e}")
        return False

def create_item_database(conn: sqlite3.Connection) -> bool:
    try:
        conn.cursor().execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uniqueName TEXT NOT NULL,
            imageURL TEXT NOT NULL
        )""")
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] While creating item database: {e}")
        return False

def create_recipe_database(conn: sqlite3.Connection) -> bool:
    try:
        conn.cursor().execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            recipe_name TEXT PRIMARY KEY NOT NULL,
            
            build_price INTEGER NOT NULL,
            build_time INTEGER NOT NULL,
            skip_build_time_price INTEGER NOT NULL,
            consume_on_use BOOLEAN NOT NULL DEFAULT TRUE,
            produced_amount INTEGER NOT NULL DEFAULT 1,
            codex_secret BOOLEAN NOT NULL DEFAULT FALSE,
            
            result_id INTEGER NOT NULL,
            ingredient_1_id INTEGER NOT NULL,
            ingredient_1_quantity INTEGER NOT NULL DEFAULT 1,
            ingredient_2_id INTEGER NOT NULL,
            ingredient_2_quantity INTEGER NOT NULL DEFAULT 1,
            ingredient_3_id INTEGER NOT NULL,
            ingredient_3_quantity INTEGER NOT NULL DEFAULT 1,
            ingredient_4_id INTEGER NOT NULL,
            ingredient_4_quantity INTEGER NOT NULL DEFAULT 1,

            FOREIGN KEY (ingredient_1_id) REFERENCES items(id),
            FOREIGN KEY (ingredient_2_id) REFERENCES items(id),
            FOREIGN KEY (ingredient_3_id) REFERENCES items(id),
            FOREIGN KEY (ingredient_4_id) REFERENCES items(id),
            FOREIGN KEY (result_id) REFERENCES items(id)
        )""")
        conn.commit()
        return True
    except Exception as e:
        print(f"[ERROR] While creating recipe database: {e}")
        return False

# ----------------------------
# DB FILLER
# ----------------------------

def fill_img_db(conn: sqlite3.Connection, json_path: str) -> bool:
    try:
        json_content = load_json(json_path)
        if not json_content: return False
        if type(json_content) != dict:
            print(f"[Error] Json Content was no dict, but {type(json_content)}")
            return False

        items = json_content["Manifest"]
        cursor = conn.cursor()
        for item in items:
            cursor.execute("INSERT INTO items (uniqueName, imageURL) VALUES(?, ?)", (
                   item.get("uniqueName"), item.get("textureLocation")))
        return True
    except KeyError as ke:
        print(f"[ERROR] While loading image database: {ke}")
        return False
    except Exception as e:
        print(f"[ERROR] While loading image database: {e}")
        return False

def fill_recipes_db(conn: sqlite3.Connection, json_path: str) -> bool:
    try:
        json_content = load_json(json_path)
        if not json_content: return False
        if type(json_content) != dict:
            print(f"[Error] Json Content was no dict, but {type(json_content)}")
            return False

        recipes = json_content["ExportRecipes"]
        cursor = conn.cursor()
        for recipe in recipes:
            # Ingredients
            ingredients = recipe.get("ingredients")
            if len(ingredients) >= 1:
                ingredient1 = get_value_by_column(cursor, "items", "uniqueName", ingredients[0].get("ItemType"), "id")
                ingredient1_q = ingredients[0].get("ItemCount")
            else:
                ingredient1 = -1
                ingredient1_q = 0
            if len(ingredients) >= 2:
                ingredient2 = get_value_by_column(cursor, "items", "uniqueName", ingredients[1].get("ItemType"), "id")
                ingredient2_q = ingredients[0].get("ItemCount")
            else:
                ingredient2 = -1
                ingredient2_q = 0
            if len(ingredients) >= 3:
                ingredient3 = get_value_by_column(cursor, "items", "uniqueName", ingredients[2].get("ItemType"), "id")
                ingredient3_q = ingredients[0].get("ItemCount")
            else:
                ingredient3 = -1
                ingredient3_q = 0
            if len(ingredients) >= 4:
                ingredient4 = get_value_by_column(cursor, "items", "uniqueName", ingredients[3].get("ItemType"), "id")
                ingredient4_q = ingredients[0].get("ItemCount")
            else:
                ingredient4 = -1
                ingredient4_q = 0

            # Insertion
            cursor.execute("""
               INSERT INTO recipes
               (recipe_name, build_price, build_time, skip_build_time_price, consume_on_use,
               produced_amount, codex_secret, result_id, ingredient_1_id, ingredient_1_quantity, ingredient_2_id,
               ingredient_2_quantity, ingredient_3_id, ingredient_3_quantity, ingredient_4_id, ingredient_4_quantity)
               VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               """, (
                   recipe.get("uniqueName"), recipe.get("buildPrice"), recipe.get("buildTime"), recipe.get("skipBuildTimePrice"),
                   recipe.get("consumeOnUse"), recipe.get("num"), recipe.get("codexSecret"), get_value_by_column(cursor, "items", "uniqueName", recipe.get("resultType"), "id"),
                   ingredient1, ingredient1_q, ingredient2, ingredient2_q, ingredient3, ingredient3_q, ingredient4, ingredient4_q))
        return True
    except KeyError as ke:
        print(f"[ERROR] While loading recipe database: {ke}")
        return False
    except Exception as e:
        print(f"[ERROR] While loading recipe database: {e}")
        return False

# ----------------------------
# MAIN
# ----------------------------

def main() -> None:
    print(f"Opening database: {DB_FILE}")
    conn = sqlite3.connect(DB_FILE)

    try:
        drop_tables(conn, ["translations", "items", "recipes"])

        if not create_translation_database(conn) or not create_item_database(conn) or not create_recipe_database(conn):
            return

        fill_img_db(conn, "./ExportManifest.json")
        fill_recipes_db(conn, "./ExportRecipes_en.json")

        tables = list_tables(conn)
        if not tables:
            print("No tables found.")
            return

        for table in tables:
            describe_table(conn, table)
            preview_table(conn, table)

    except Exception as e:
        print(f"[ERROR] While reading DB: {e}")

    finally:
        print("\nDone.")
        conn.close()

if __name__ == "__main__": main()
