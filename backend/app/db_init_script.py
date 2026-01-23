import sys
from typing import List, cast

from database.db import (
    connect_to_mongodb,
    describe_table,
    drop_tables,
    list_collections,
    list_databases,
    list_tables,
    preview_table,
)
from database.static.db_init.init_images import create_images_database, fill_img_db
from database.static.db_init.init_items import create_item_database
from database.static.db_init.init_mods import create_mods_database, fill_mods_db
from database.static.db_init.init_recipes import create_recipe_database, fill_recipes_db
from database.static.db_init.init_translations import create_translation_database
from database.static.db_init.init_warframes import (
    create_warframe_database,
    fill_warframe_db,
)
from database.static.db_init.json_collector import JsonCollector
from models.static_models import ImgItem, Mod, Recipe, Warframe


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

    # Connect to MongoDB
    client = connect_to_mongodb()
    if not client:
        return

    # JSONs collector
    jsons_collector = JsonCollector()

    # Actual operations
    try:
        drop_tables(
            client,
            [
                "translations",
                "items",
                "recipes",
                "warframes",
                "warframe_abilities",
                "mods",
            ],
            confirm=not skip_confirmation,
        )

        if (
            not create_translation_database(client)
            or not create_item_database(client)
            or not create_recipe_database(client)
            or not create_warframe_database(client)
            or not create_images_database(client)
            or not create_mods_database(client)
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
            "ExportRegions",
            "ExportRelicArcane",
            # "ExportResources",
            # "ExportSentinels",
            # "ExportSortieRewards",
            "ExportUpgrades",
            "ExportWarframes",
            "ExportWeapons",
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
        fill_recipes_db(client, recipes)

        warframes: List[Warframe] = cast(
            List[Warframe], raw_data.get("ExportWarframes", [])
        )
        fill_warframe_db(client, warframes)

        imgs: List[ImgItem] = cast(List[ImgItem], raw_data.get("ExportManifest", []))
        fill_img_db(client, imgs)

        mods: List[Mod] = cast(List[Mod], raw_data.get("ExportUpgrades", []))
        fill_mods_db(client, mods)

        tables = list_tables(client)
        if not tables:
            print("No tables found.")
            return

        for table in tables:
            describe_table(client, table)
            preview_table(client, table, limit)

    except Exception as e:
        print(f"[ERROR] While reading DB: {e}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
