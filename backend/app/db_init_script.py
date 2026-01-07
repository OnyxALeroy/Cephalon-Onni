import os
import sys
from typing import List
from urllib.parse import quote_plus

from database.static.db_helpers import (
    describe_table,
    drop_tables,
    list_tables,
    preview_table,
)
from database.static.db_init.images import create_images_database, fill_img_db
from database.static.db_init.items import create_item_database
from database.static.db_init.json_collector import JsonCollector
from database.static.db_init.recipes import create_recipe_database, fill_recipes_db
from database.static.db_init.translations import create_translation_database
from database.static.db_init.warframes import create_warframe_database, fill_warframe_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def main() -> None:
    # Check for -y flag to skip confirmation
    skip_confirmation = "-y" in sys.argv
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
    print(
        f"Connecting to PostgreSQL database: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    session = SessionLocal()

    # JSONs collector
    jsons_collector = JsonCollector()

    try:
        drop_tables(
            session,
            ["translations", "items", "recipes", "warframes", "warframe_abilities"],
            confirm=not skip_confirmation,
        )

        if (
            not create_translation_database(session)
            or not create_item_database(session)
            or not create_recipe_database(session)
            or not create_warframe_database(session)
            or not create_images_database(session)
        ):
            return

        jsons: List[str] = [
            # "ExportCustoms",
            # "ExportDrones",
            # "ExportFlavour",
            # "ExportFusionBundles",
            # "ExportGear",
            # "ExportKeys",
            "ExportRecipes",
            # "ExportRegions",
            # "ExportRelicArcane",
            # "ExportResources",
            # "ExportSentinels",
            # "ExportSortieRewards",
            # "ExportUpgrades",
            "ExportWarframes",
            # "ExportWeapons",
            "ExportManifest",
        ]
        json_dict = jsons_collector.get_jsons("en", jsons)
        if json_dict is None:
            return

        # Save JSONs to disk before database operations
        if not jsons_collector.save_jsons_to_disk(json_dict):
            print("[ERROR] Failed to save JSONs to disk")

        if "ExportManifest" in json_dict:
            fill_img_db(session, json_dict["ExportManifest"])
        else:
            print("[ERROR] Could not get ExportManifest")
        if "ExportRecipes" in json_dict:
            fill_recipes_db(session, json_dict["ExportRecipes"])
        else:
            print("[ERROR] Could not get ExportRecipes")
        if "ExportWarframes" in json_dict:
            fill_warframe_db(session, json_dict["ExportWarframes"])
        else:
            print("[ERROR] Could not get ExportWarframes")

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


if __name__ == "__main__":
    main()
