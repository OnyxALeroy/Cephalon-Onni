import os
from typing import Dict, List, Optional, Union
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

from backend.database.static.db_helpers import drop_tables, list_tables, describe_table, preview_table, \
    get_value_by_column

# PostgreSQL connection setup
POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "cephalon_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# URL encode the password for special characters
encoded_password = quote_plus(POSTGRES_PASSWORD)
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{encoded_password}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_json_index(language_code: str)-> Optional[List[str]]:
    url: str = "https://origin.warframe.com/PublicExport/index_" + language_code.lower() + ".txt.lzma"
    try:
        import requests
        response: requests.Response = requests.get(url, stream=True)
    except Exception as e:
        print(f"[ERROR] While getting index lzma from the Public Export API: {e}")
        return None
    try:
        import lzma
        index_file:bytes = lzma.decompress(response.content)
        index_content: str = index_file.decode('utf-8')
        return index_content.splitlines()
    except Exception as e:
        print(f"[ERROR] While decompressing index lzma: {e}")
        return None

def get_export_json(index_content: List[str], json_name: str)-> Optional[Union[Dict, List]]:
    file_match: str = "Export" + json_name + "_"
    file_name: str = ""
    for line in index_content:
        if line.startswith(file_match):
            file_name = line
            break
    if len(file_name) == 0:
        print(f"[ERROR] No matching json for the name {json_name} in the given index")
        return None
    try:
        import requests
        url: str = "http://content.warframe.com/PublicExport/Manifest/" + file_name
        response: requests.Response = requests.get(url, stream=True)
    except Exception as e:
        print(f"[ERROR] While getting json {file_name} from the Public Export API: {e}")
        return None
    try:
       return response.json()
    except Exception as e:
        print(f"[ERROR] While loading json {file_name} from the Public Export API as a json: {e}")
        return None 


def get_jsons(language_code: str, json_names: List[str])->Optional[Dict[str, Union[Dict, List]]]:
    language_code_list: List[str] = [
        "de", "en", "es",
        "fr", "it", "ja",
        "ko", "pl", "pt",
        "ru", "tc", "th",
        "tr", "uk", "zh"
    ]
    if not language_code.lower() in language_code_list:
        print(f"[ERROR] {language_code} is not an accepted language code")
        return None
    available_json_names: List[str] = [
        "Customs",
        "Drones",
        "Flavour",
        "FusionBundles",
        "Gear",
        "Keys",
        "Recipes",
        "Regions",
        "RelicArcane",
        "Resources",
        "Sentinels",
        "SortieRewards",
        "Upgrades",
        "Warframes",
        "Weapons",
        "Manifest",
    ]

    for name in json_names:
        if not name in available_json_names:
            json_names.remove(name)
            print(f"[WARNING] {name} is not an existing json in the Public Export API")
    if len(json_names) == 0:
        print(f"[ERROR] There no json available in the Public Export API were given")
        return None
    

    index_content = get_json_index(language_code)
    if index_content is None:
        return None
    results: dict[str, Union[Dict, List]] = {}
    from concurrent. futures import ThreadPoolExecutor, as_completed, Future
    with ThreadPoolExecutor(max_workers=min(len(json_names), 16)) as executor:
        future_to_index: Dict[Future, str] = {
            executor.submit(get_export_json, index_content, json_name): json_name
            for json_name in json_names
        }
        
        for future in as_completed(future_to_index):
            name:  str = future_to_index[future]
            try:
                results[name] = future.result()
            except Exception as e: 
                print(f"Error downloading {name}:  {e}")
    
    return results

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

def create_translation_database(session) -> bool:
    try:
        session.execute(text("""
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER NOT NULL,            
            language TEXT NOT NULL,
            value TEXT NOT NULL,
            PRIMARY KEY (id, language)
        )"""))
        session.commit()
        return True
    except Exception as e:
        print(f"[ERROR] While creating translation database: {e}")
        session.rollback()
        return False

def create_item_database(session) -> bool:
    try:
        session.execute(text("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            uniqueName TEXT NOT NULL UNIQUE,
            imageURL TEXT NOT NULL
        )"""))
        session.commit()
        return True
    except Exception as e:
        print(f"[ERROR] While creating item database: {e}")
        session.rollback()
        return False

def create_recipe_database(session) -> bool:
    try:
        session.execute(text("""
        CREATE TABLE IF NOT EXISTS recipes (
            recipe_name TEXT PRIMARY KEY NOT NULL,
            
            build_price INTEGER NOT NULL,
            build_time INTEGER NOT NULL,
            skip_build_time_price INTEGER NOT NULL,
            consume_on_use BOOLEAN NOT NULL DEFAULT TRUE,
            produced_amount INTEGER NOT NULL DEFAULT 1,
            codex_secret BOOLEAN NOT NULL DEFAULT FALSE,
            
            result_id INTEGER NOT NULL,
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
        )"""))
        session.commit()
        return True
    except Exception as e:
        print(f"[ERROR] While creating recipe database: {e}")
        session.rollback()
        return False

# ----------------------------
# DB FILLER
# ----------------------------

def fill_img_db(session, json_path: str) -> bool:
    try:
        json_content = load_json(json_path)
        if not json_content: return False
        if type(json_content) != dict:
            print(f"[Error] Json Content was no dict, but {type(json_content)}")
            return False

        items = json_content["Manifest"]
        for item in items:
            session.execute(text("""
                INSERT INTO items (uniqueName, imageURL) 
                VALUES(:uniqueName, :imageURL)
                ON CONFLICT (uniqueName) DO NOTHING
            """), {
                   "uniqueName": item.get("uniqueName"), 
                   "imageURL": item.get("textureLocation")
            })
        session.commit()
        return True
    except KeyError as ke:
        print(f"[ERROR] While loading image database: {ke}")
        session.rollback()
        return False
    except Exception as e:
        print(f"[ERROR] While loading image database: {e}")
        session.rollback()
        return False

def fill_recipes_db(session, json_path: str) -> bool:
    try:
        json_content = load_json(json_path)
        if not json_content: return False
        if type(json_content) != dict:
            print(f"[Error] Json Content was no dict, but {type(json_content)}")
            return False

        recipes = json_content["ExportRecipes"]
        for recipe in recipes:
            # Ingredients
            ingredients = recipe.get("ingredients")
            if len(ingredients) >= 1:
                ingredient1 = get_value_by_column(session, "items", "uniqueName", ingredients[0].get("ItemType"), "id")
                ingredient1_q = ingredients[0].get("ItemCount")
            else:
                ingredient1 = None
                ingredient1_q = 0
            if len(ingredients) >= 2:
                ingredient2 = get_value_by_column(session, "items", "uniqueName", ingredients[1].get("ItemType"), "id")
                ingredient2_q = ingredients[1].get("ItemCount")
            else:
                ingredient2 = None
                ingredient2_q = 0
            if len(ingredients) >= 3:
                ingredient3 = get_value_by_column(session, "items", "uniqueName", ingredients[2].get("ItemType"), "id")
                ingredient3_q = ingredients[2].get("ItemCount")
            else:
                ingredient3 = None
                ingredient3_q = 0
            if len(ingredients) >= 4:
                ingredient4 = get_value_by_column(session, "items", "uniqueName", ingredients[3].get("ItemType"), "id")
                ingredient4_q = ingredients[3].get("ItemCount")
            else:
                ingredient4 = None
                ingredient4_q = 0

            # Insertion
            session.execute(text("""
               INSERT INTO recipes
               (recipe_name, build_price, build_time, skip_build_time_price, consume_on_use,
               produced_amount, codex_secret, result_id, ingredient_1_id, ingredient_1_quantity, ingredient_2_id,
               ingredient_2_quantity, ingredient_3_id, ingredient_3_quantity, ingredient_4_id, ingredient_4_quantity)
               VALUES(:recipe_name, :build_price, :build_time, :skip_build_time_price, :consume_on_use,
               :produced_amount, :codex_secret, :result_id, :ingredient_1_id, :ingredient_1_quantity, :ingredient_2_id,
               :ingredient_2_quantity, :ingredient_3_id, :ingredient_3_quantity, :ingredient_4_id, :ingredient_4_quantity)
               """), {
                   "recipe_name": recipe.get("uniqueName"), 
                   "build_price": recipe.get("buildPrice"), 
                   "build_time": recipe.get("buildTime"), 
                   "skip_build_time_price": recipe.get("skipBuildTimePrice"),
                   "consume_on_use": recipe.get("consumeOnUse"), 
                   "produced_amount": recipe.get("num"), 
                   "codex_secret": recipe.get("codexSecret"), 
                   "result_id": get_value_by_column(session, "items", "uniqueName", recipe.get("resultType"), "id"),
                   "ingredient_1_id": ingredient1, 
                   "ingredient_1_quantity": ingredient1_q, 
                   "ingredient_2_id": ingredient2, 
                   "ingredient_2_quantity": ingredient2_q, 
                   "ingredient_3_id": ingredient3, 
                   "ingredient_3_quantity": ingredient3_q, 
                   "ingredient_4_id": ingredient4, 
                   "ingredient_4_quantity": ingredient4_q
            })
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

# ----------------------------
# MAIN
# ----------------------------

def main() -> None:
    print(f"Connecting to PostgreSQL database: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
    session = SessionLocal()

    try:
        drop_tables(session, ["translations", "items", "recipes"])

        if not create_translation_database(session) or not create_item_database(session) or not create_recipe_database(session):
            return

        fill_img_db(session, "ExportManifest.json")
        fill_recipes_db(session, "ExportRecipes_en.json")

        tables = list_tables(session)
        if not tables:
            print("No tables found.")
            return

        for table in tables:
            describe_table(session, table)
            preview_table(session, table)

    except Exception as e:
        print(f"[ERROR] While reading DB: {e}")

    finally:
        print("\nDone.")
        session.close()

if __name__ == "__main__": main()