import re
from typing import List, Optional

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from database.db import get_value_by_field

# -------------------------------------------------------------------------------------------------


def handle_missions(
    row_list: List[str],
    client: MongoClient,
    db_name: str,
) -> None:
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
                # NOTE: Missions are stored using the format: '<planet>/<mission name> (<mission type>)'
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
                    "rotation": current_rotation.strip(),
                    "planet": current_planet,
                    "type": current_mission_type,
                }
        else:
            continue

    # Update missions loot-tables
    try:
        for item in items.values():
            mission_uniqueName = get_value_by_field(
                client, db_name, "missions", "name", item["source"], "mission_name"
            )
            res = client[db_name]["missions"].update_one(
                {"mission_name": mission_uniqueName},
                {
                    "$addToSet": {
                        "drops": {
                            "item": item["name"],
                            "chance": item["chance"],
                            "rotation": item["rotation"]
                            if item["rotation"] != ""
                            else None,
                        }
                    }
                },
            )
            if res.matched_count == 0:
                print(
                    f'[INFO] Inserting new drop source: "{item["planet"]}, {item["source"]} ({item["type"]})" not found as mission, inserted as "auxiliary_mission"'
                )
                db = client[db_name]
                collection = db["drop_sources"]
                collection.insert_one(
                    {
                        "name": item["name"],
                        "chance": item["chance"],
                        "source": f"{item['planet']}, {item['source']} ({item['type']})",
                        "source_type": "auxiliary_mission",
                        "rotation": item["rotation"],
                    }
                )
    except PyMongoError as e:
        print(f"Error updating mission loot-tables: {e}")
        raise


def handle_keys(
    row_list: List[str],
    client: MongoClient,
    db_name: str,
) -> None:
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
                    "rotation": current_rotation.strip(),
                }
        else:
            continue

    try:
        db = client[db_name]
        collection = db["drop_sources"]
        if list(items.values()):
            collection.insert_many(items.values())
            print(f"Inserted {len(items)} drop sources")
    except PyMongoError as e:
        print(f"Error inserting drop sources: {e}")


def handle_dynamic_location_items(
    row_list: List[List[str]],
    client: MongoClient,
    db_name: str,
) -> None:
    # Early cleanup
    for sub_list in row_list:
        for element in sub_list:
            if element == "":
                sub_list.remove(element)

    items = dict()
    current_dynamic_location_name = ""
    current_rotation: str | None = ""
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
                }
        else:
            continue

    try:
        db = client[db_name]
        collection = db["drop_sources"]
        if list(items.values()):
            collection.insert_many(items.values())
            print(f"Inserted {len(items)} drop sources")
    except PyMongoError as e:
        print(f"Error inserting drop sources: {e}")


def handle_sorties(
    row_list: List[List[str]],
    client: MongoClient,
    db_name: str,
) -> None:
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

    try:
        db = client[db_name]
        collection = db["drop_sources"]
        if list(items.values()):
            collection.insert_many(items.values())
            print(f"Inserted {len(items)} drop sources")
    except PyMongoError as e:
        print(f"Error inserting drop sources: {e}")


def handle_bounty_items(
    row_list: List[List[str]],
    mission_title: str,
    client: MongoClient,
    db_name: str,
) -> None:
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
                current_level_name = row[0]  # use mission title
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

    try:
        db = client[db_name]
        collection = db["drop_sources"]
        if list(items.values()):
            collection.insert_many(items.values())
            print(f"Inserted {len(items)} drop sources")
    except PyMongoError as e:
        print(f"Error inserting drop sources: {e}")


def handle_general_drops(
    row_list: List[List[str]],
    title: str,
    client: MongoClient,
    db_name: str,
) -> None:
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

    try:
        db = client[db_name]
        collection = db["drop_sources"]
        if list(items.values()):
            collection.insert_many(items.values())
            print(f"Inserted {len(items)} drop sources")
    except PyMongoError as e:
        print(f"Error inserting drop sources: {e}")


# -------------------------------------------------------------------------------------------------


def handle_read_values(
    title: Optional[str],
    reading_list: list,
    client: MongoClient,
    db_name: str,
) -> None:
    if title is None:
        return

    if title == "Missions:":
        handle_missions(reading_list, client, db_name)
    elif title == "Keys:":
        handle_keys(reading_list, client, db_name)
    elif title == "Dynamic Location Rewards:":
        handle_dynamic_location_items(reading_list, client, db_name)
    elif title == "Sorties:":
        handle_sorties(reading_list, client, db_name)
    elif title in [
        "Cetus Bounty Rewards:",
        "Orb Vallis Bounty Rewards:",
        "Cambion Drift Bounty Rewards:",
        "Zariman Bounty Rewards:",
        "Albrecht's Laboratories Bounty Rewards:",
        "Hex Bounty Rewards:",
    ]:
        handle_bounty_items(reading_list, title[:-1], client, db_name)
    elif title in [
        "Relics:",
        "Mod Drops by Mod:",
        "Resource Drops by Resource:",
        "Blueprint/Item Drops by Blueprint/Item:",
    ]:
        return
    elif " Drops by " in title:
        handle_general_drops(reading_list, title.replace("/", "-"), client, db_name)
    else:
        raise ValueError(f"Unknown title: {title}")


# -------------------------------------------------------------------------------------------------


def init_loot_tables(
    client: MongoClient,
    loot_table_url: str,
    db_name: str = "cephalon_onni",
) -> bool:
    # Fetching loot tables
    resp = requests.get(loot_table_url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    tables = soup.find_all("table")

    last_header = None
    reading_list = []
    for table in tables:
        h3 = table.find_previous("h3")
        title = h3.get_text(strip=True) if h3 else None
        if title != last_header:
            handle_read_values(last_header, reading_list, client, db_name)
            last_header = title
            reading_list = []
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            values = [cell.get_text(strip=True) for cell in cells]

            if values == [""]:
                continue
            reading_list.append(values)
    if last_header:
        handle_read_values(last_header, reading_list, client, db_name)

    return True


# -------------------------------------------------------------------------------------------------
