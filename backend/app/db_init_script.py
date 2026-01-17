import os
import sys
from typing import List, cast
from urllib.parse import quote_plus

from database.static.db_helpers import (
    describe_table,
    drop_tables,
    list_tables,
    preview_table,
)
from database.static.db_init.db_init_models import ImgItem, Recipe, Warframe
from database.static.db_init.images import create_images_database, fill_img_db
from database.static.db_init.items import create_item_database
from database.static.db_init.json_collector import JsonCollector
from database.static.db_init.recipes import create_recipe_database, fill_recipes_db
from database.static.db_init.translations import create_translation_database
from database.static.db_init.warframes import create_warframe_database, fill_warframe_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def main() -> None:
    # Check for help flag
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python db_init_script.py [options]")
        print("Options:")
        print("  -y                    Skip confirmation prompts")
        print("  --limit=<number>      Number of lines to show per table (default: 10)")
        print("  --limit <number>      Same as above")
        print("  -h, --help            Show this help message")
        sys.exit(0)
    
    # Check for -y flag to skip confirmation
    skip_confirmation = "-y" in sys.argv
    
    # Parse limit parameter (default 10)
    limit = 10
    for i, arg in enumerate(sys.argv):
        if arg.startswith("--limit="):
            try:
                limit = int(arg.split("=")[1])
                if limit < 1:
                    print("[ERROR] Limit must be a positive integer")
                    sys.exit(1)
            except (ValueError, IndexError):
                print("[ERROR] Invalid limit format. Use --limit=<number>")
                sys.exit(1)
        elif arg == "--limit" and i + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[i + 1])
                if limit < 1:
                    print("[ERROR] Limit must be a positive integer")
                    sys.exit(1)
            except ValueError:
                print("[ERROR] Invalid limit value. Must be an integer.")
                sys.exit(1)

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
        f"Connecting to PostgreSQL database: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB} (showing {limit} rows per table)"
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
        raw_data = jsons_collector.get_jsons("en", jsons)
        if raw_data is None:
            return

        # Save JSONs to disk before database operations
        if not jsons_collector.save_to_disk(raw_data):
            print("[ERROR] Failed to save JSONs to disk")

        # All database fills
        recipes: List[Recipe] = cast(List[Recipe], raw_data.get("ExportRecipes", []))
        fill_recipes_db(session, recipes)

        warframes: List[Warframe] = cast(
            List[Warframe], raw_data.get("ExportWarframes", [])
        )
        fill_warframe_db(session, warframes)

        imgs: List[ImgItem] = cast(List[ImgItem], raw_data.get("ExportManifest", []))
        fill_img_db(session, imgs)

        tables = list_tables(session)
        if not tables:
            print("No tables found.")
            return

        for table in tables:
            describe_table(session, table)
            preview_table(session, table, limit)

    except Exception as e:
        print(f"[ERROR] While reading DB: {e}")

    finally:
        session.close()


if __name__ == "__main__":
    main()