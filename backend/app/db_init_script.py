import asyncio
import json
import logging
import sys
import os
import requests
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

from database.postgres_db import postgres_db
from database.static.db_init.json_collector import JsonCollector
from database.static.db_init.postgres.init_warframes import (
    create_warframe_tables,
    fill_warframe_db,
)
from database.static.db_init.postgres.init_weapons import (
    create_weapon_tables,
    fill_weapons_db,
)
from database.static.db_init.postgres.init_mods import (
    create_mods_tables,
    fill_mods_db,
)
from database.static.db_init.postgres.init_missions import (
    create_mission_tables,
    fill_missions_db,
)
from database.static.db_init.postgres.init_relics import (
    create_relic_tables,
    fill_relic_db,
)
from database.static.db_init.postgres.init_recipes import (
    create_recipe_tables,
    fill_recipes_db,
)
from database.static.db_init.postgres.init_images import (
    create_images_tables,
    fill_img_db,
)
from database.static.db_init.postgres.init_loot_tables import (
    create_drop_source_tables,
    fill_drop_sources_db,
)
from database.static.db_init.postgres.init_companions import (
    create_companion_tables,
    fill_companion_db,
)
from database.static.db_init.postgres.init_resources import (
    create_resource_tables,
    fill_resource_db,
)
from database.static.db_init.postgres.init_amp_parts import (
    create_amp_tables,
    fill_amp_db,
)


def parse_loot_tables_sync(loot_table_url: str) -> List[Dict[str, Any]]:
    drop_sources = []
    
    resp = requests.get(loot_table_url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    tables = soup.find_all("table")

    last_header = None
    reading_list = []
    
    def handle_missions(row_list: List[List[str]], drop_sources: List[Dict]):
        items = dict()
        current_planet = ""
        current_mission_name = ""
        current_mission_type = ""
        current_rotation = ""
        cursor = 0
        while cursor < len(row_list):
            row = row_list[cursor]
            cursor += 1
            if len(row) == 1:
                if "Rotation" in row[0]:
                    current_rotation = row[0].strip()
                else:
                    mission_match = re.match(r"([^/]+)/(.+?) \((.+)\)", row[0])
                    if mission_match:
                        planet, name, t = mission_match.groups()
                        current_planet = planet.strip()
                        current_mission_name = name.strip()
                        current_mission_type = t.strip()
            elif len(row) == 2:
                item_name, probability = row[0].strip(), row[1].strip()
                prob_match = re.match(r"(.+?) \(([\d.]+%?)\)", probability)
                if prob_match:
                    _, p_value = prob_match.groups()
                    items[item_name.strip()] = {
                        "name": item_name.strip(),
                        "source": current_mission_name,
                        "chance": p_value.strip(),
                        "rotation": current_rotation.strip() if current_rotation else None,
                        "planet": current_planet,
                        "type": current_mission_type,
                        "source_type": "mission",
                    }
            else:
                continue
        
        drop_sources.extend(items.values())

    def handle_keys(row_list: List[List[str]], drop_sources: List[Dict]):
        items = dict()
        current_key_name = ""
        current_rotation = ""
        cursor = 0
        while cursor < len(row_list):
            row = row_list[cursor]
            cursor += 1
            if len(row) == 1:
                if "Rotation" in row[0]:
                    current_rotation = row[0]
                else:
                    current_key_name = row[0]
            elif len(row) == 2:
                item_name, probability = row[0].strip(), row[1].strip()
                prob_match = re.match(r"(.+?) \(([\d.]+%?)\)", probability)
                if prob_match:
                    _, p_value = prob_match.groups()
                    items[item_name.strip()] = {
                        "name": item_name.strip(),
                        "chance": p_value.strip(),
                        "source": current_key_name.strip(),
                        "source_type": "key",
                        "rotation": current_rotation.strip() if current_rotation else None,
                    }
            else:
                continue
        
        drop_sources.extend(items.values())

    def handle_dynamic_location_items(row_list: List[List[str]], drop_sources: List[Dict]):
        for sub_list in row_list:
            for element in sub_list:
                if element == "":
                    sub_list.remove(element)

        items = dict()
        current_dynamic_location_name = ""
        current_rotation: Optional[str] = ""
        cursor = 0
        while cursor < len(row_list):
            row = row_list[cursor]
            cursor += 1
            if len(row) == 1:
                if "Rotation" in row[0]:
                    current_rotation = row[0]
                else:
                    current_dynamic_location_name = row[0]
            elif len(row) == 2:
                item_name, probability = row[0].strip(), row[1].strip()
                prob_match = re.match(r"(.+?) \(([\d.]+%?)\)", probability)
                if prob_match:
                    _, p_value = prob_match.groups()
                    items[item_name.strip()] = {
                        "name": item_name.strip(),
                        "source": current_dynamic_location_name.strip(),
                        "type": "dynamic_location",
                        "chance": p_value.strip(),
                        "rotation": current_rotation.strip() if current_rotation else None,
                        "source_type": "dynamic_location",
                    }
            else:
                continue

        drop_sources.extend(items.values())

    def handle_sorties(row_list: List[List[str]], drop_sources: List[Dict]):
        items = dict()
        cursor = 0
        while cursor < len(row_list):
            row = row_list[cursor]
            cursor += 1
            if len(row) == 2:
                item_name, probability = row[0].strip(), row[1].strip()
                prob_match = re.match(r"(.+?) \(([\d.]+%?)\)", probability)
                if prob_match:
                    _, p_value = prob_match.groups()
                    items[item_name.strip()] = {
                        "name": item_name.strip(),
                        "source": "Sortie",
                        "source_type": "sortie",
                        "chance": p_value.strip(),
                        "rotation": None,
                    }
            else:
                continue
        
        drop_sources.extend(items.values())

    def handle_bounty_items(row_list: List[List[str]], mission_title: str, drop_sources: List[Dict]):
        def parse_stages(s):
            if s.strip() == "Final Stage":
                return ["Final Stage"]
            parts = re.split(r",\s*|\s+and\s+", s)
            return [re.sub(r"\band\b", "", part).strip() for part in parts if part.strip()]

        items = dict()
        cursor = 0
        current_level_name = ""
        current_rotation = ""
        current_stages = []
        while cursor < len(row_list):
            row = row_list[cursor]
            cursor += 1
            if len(row) == 1:
                if "Rotation" in row[0]:
                    current_rotation = row[0].strip()
                else:
                    current_level_name = row[0]
            elif len(row) == 2:
                current_stages = parse_stages(row[1])
            elif len(row) == 3:
                item_name, probability = row[1].strip(), row[2].strip()
                prob_match = re.match(r"(.+?) \(([\d.]+%?)\)", probability)
                if prob_match:
                    _, p_value = prob_match.groups()
                    items[item_name.strip()] = {
                        "name": item_name.strip(),
                        "source": mission_title + " " + current_level_name,
                        "source_type": "bounty",
                        "chance": p_value.strip(),
                        "rotation": f"{current_rotation} ({', '.join(current_stages)})",
                    }
            else:
                continue

        drop_sources.extend(items.values())

    def handle_general_drops(row_list: List[List[str]], title: str, drop_sources: List[Dict]):
        items = dict()
        cursor = 0
        current_source_name = ""
        current_global_drop_chance = ""
        while cursor < len(row_list):
            row = row_list[cursor]
            cursor += 1
            if len(row) == 1:
                current_source_name = row[0]
            elif len(row) == 2:
                source, match = row[0], re.search(r"(\d+\.?\d*)%", row[1])
                current_source_name = source
                if match:
                    current_global_drop_chance = match.group(0)
            elif len(row) == 3:
                if row[0] == "Source":
                    continue
                item_name, probability = row[1].strip(), row[2].strip()
                prob_match = re.match(r"(.+?) \(([\d.]+%?)\)", probability)
                if prob_match:
                    _, p_value = prob_match.groups()
                    items[item_name.strip()] = {
                        "name": item_name.strip(),
                        "source": f"{current_source_name.strip()} ({current_global_drop_chance.strip()}%)",
                        "source_type": "general_drop",
                        "chance": p_value.strip(),
                        "rotation": None,
                    }
            else:
                continue

        drop_sources.extend(items.values())

    def handle_read_values(title: Optional[str], reading_list: list, drop_sources: List[Dict]):
        if title is None:
            return

        if title == "Missions:":
            handle_missions(reading_list, drop_sources)
        elif title == "Keys:":
            handle_keys(reading_list, drop_sources)
        elif title == "Dynamic Location Rewards:":
            handle_dynamic_location_items(reading_list, drop_sources)
        elif title == "Sorties:":
            handle_sorties(reading_list, drop_sources)
        elif title in [
            "Cetus Bounty Rewards:",
            "Orb Vallis Bounty Rewards:",
            "Cambion Drift Bounty Rewards:",
            "Zariman Bounty Rewards:",
            "Albrecht's Laboratories Bounty Rewards:",
            "Hex Bounty Rewards:",
        ]:
            handle_bounty_items(reading_list, title[:-1], drop_sources)
        elif " Drops by " in title:
            handle_general_drops(reading_list, title.replace("/", "-"), drop_sources)

    for table in tables:
        h3 = table.find_previous("h3")
        title = h3.get_text(strip=True) if h3 else None
        if title != last_header:
            handle_read_values(last_header, reading_list, drop_sources)
            last_header = title
            reading_list = []
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            values = [cell.get_text(strip=True) for cell in cells]
            if values == [""]:
                continue
            reading_list.append(values)
    if last_header:
        handle_read_values(last_header, reading_list, drop_sources)

    return drop_sources


def main() -> None:
    asyncio.run(_async_main())


async def _async_main() -> None:
    log_dir = "/app/logs/db_init"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_dir, f"db_init_{timestamp}.log")

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers.clear()

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter("%(message)s"))
    root_logger.addHandler(console_handler)

    logging.info("POSTGRES DB INIT LOG - " + timestamp)
    logging.info("")

    if "--help" in sys.argv or "-h" in sys.argv:
        logging.info("Usage: python db_init_script.py [options]")
        logging.info("Options:")
        logging.info("  -y                    Skip confirmation prompts")
        logging.info("  --save-json, -sj      Save JSON files to disk (default: False)")
        logging.info("  --limit=<number>      Number of lines to show per table (default: 10)")
        logging.info("  --limit <number>      Same as above")
        logging.info("  -h, --help            Show this help message")
        sys.exit(0)

    skip_confirmation = "-y" in sys.argv
    save_json_to_disk = "--save-json" in sys.argv or "-sj" in sys.argv

    limit = 10
    for i, arg in enumerate(sys.argv):
        if arg.startswith("--limit="):
            try:
                limit = int(arg.split("=")[1])
                if limit < 1:
                    logging.error("Limit must be a positive integer")
                    sys.exit(1)
            except (ValueError, IndexError):
                logging.error("Invalid limit format. Use --limit=<number>")
                sys.exit(1)
        elif arg == "--limit" and i + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[i + 1])
                if limit < 1:
                    logging.error("Limit must be a positive integer")
                    sys.exit(1)
            except ValueError:
                logging.error("Invalid limit value. Must be an integer.")
                sys.exit(1)

    postgres_db.initialize()
    await postgres_db.create_tables()
    logging.info("PostgreSQL tables created")

    jsons_collector = JsonCollector()

    try:
        jsons: List[str] = [
            "ExportRecipes",
            "ExportRegions",
            "ExportRelicArcane",
            "ExportUpgrades",
            "ExportWarframes",
            "ExportWeapons",
            "ExportManifest",
            "ExportSentinels",
            "ExportResources",
        ]
        extra_jsons: List[str] = [
            "ExportCustoms",
            "ExportDrones",
            "ExportFlavour",
            "ExportFusionBundles",
            "ExportGear",
            "ExportKeys",
            "ExportSortieRewards",
        ]
        all_jsons = jsons + extra_jsons
        raw_data = jsons_collector.get_jsons("en", all_jsons)
        if raw_data is None:
            logging.error("Failed to fetch JSON data from Warframe")
            return

        extra_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "json", "extra")
        extra_data = {k: v for k, v in raw_data.items() if k in extra_jsons}
        if extra_data:
            os.makedirs(extra_dir, exist_ok=True)
            for name, content in extra_data.items():
                path = os.path.join(extra_dir, f"{name}.json")
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(content, f, ensure_ascii=False, indent=2)
                logging.info(f"Saved extra export: {path}")

        if save_json_to_disk:
            if not jsons_collector.save_to_disk(raw_data):
                logging.error("Failed to save JSONs to disk")

        async with postgres_db._session_factory() as session:
            recipes = raw_data.get("ExportRecipes", [])
            await fill_recipes_db(session, recipes)

            warframes = raw_data.get("ExportWarframes", [])
            await fill_warframe_db(session, warframes)

            imgs = raw_data.get("ExportManifest", [])
            await fill_img_db(session, imgs)

            mods = raw_data.get("ExportUpgrades", [])
            await fill_mods_db(session, mods)

            weapons = raw_data.get("ExportWeapons", [])
            await fill_weapons_db(session, weapons)

            missions = raw_data.get("ExportRegions", [])
            await fill_missions_db(session, missions)

            relics = raw_data.get("ExportRelicArcane", [])
            await fill_relic_db(session, relics)

            companions = raw_data.get("ExportSentinels", [])
            await fill_companion_db(session, companions)

            resources = raw_data.get("ExportResources", [])
            await fill_resource_db(session, resources)

            weapons_for_amps = raw_data.get("ExportWeapons", [])
            await fill_amp_db(session, weapons_for_amps)

        loot_table_url = "https://www.warframe.com/fr/droptables"
        logging.info("Fetching loot tables from Warframe website...")
        drop_sources = await asyncio.get_event_loop().run_in_executor(
            None, lambda: parse_loot_tables_sync(loot_table_url)
        )
        logging.info(f"Found {len(drop_sources)} drop sources")
        
        if drop_sources:
            async with postgres_db._session_factory() as session:
                await fill_drop_sources_db(session, drop_sources)

        logging.info("")
        logging.info("PostgreSQL Database initialized successfully!")

    except Exception as e:
        logging.error(f"While initializing DB: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await postgres_db.close()


if __name__ == "__main__":
    main()
