import re
from typing import List

import requests
from bs4 import BeautifulSoup

# from database.static.neo4j_helper import Neo4jHelper

# -------------------------------------------------------------------------------------------------


def handle_missions(row_list: List[str]):
    # Build the graph
    graph_data = {"missions": [], "rewards": [], "relationships": []}
    current_mission = {}
    current_rotation = ""
    cursor = 0
    while cursor < len(row_list):
        row = row_list[cursor]
        cursor += 1
        if len(row) == 1:
            if "Rotation" in row[0]:
                current_rotation = row[0].strip()
            else:
                # Missions are stored using the format: '<planet>/<mission name> (<mission type>)'
                mission_match = re.match(r"([^/]+)/(.+?) \((.+)\)", row[0])
                if mission_match:
                    planet, name, type = mission_match.groups()
                    current_mission = {
                        "name": name.strip(),
                        "type": type.strip(),
                        "planet": planet.strip(),
                    }
                    graph_data["missions"].append(current_mission)
        elif len(row) == 2:
            item_name, probability = row[0].strip(), row[1].strip()
            prob_match = re.match(r"(.+?) \(([\d.]+%?)\)", probability)
            if prob_match:
                _, p_value = prob_match.groups()
                reward = {"name": item_name.strip()}
                graph_data["rewards"].append(reward)
                graph_data["relationships"].append(
                    {
                        "from": current_mission,
                        "to": reward,
                        "rel_type": "DROPS",
                        "properties": {
                            "chance": p_value.strip(),
                            "rotation": current_rotation.strip(),
                        },
                    }
                )
        else:
            continue

    # TEMP: store in a raw json
    import json

    with open("outputs/missions.json", "w") as f:
        json.dump(graph_data, f)


"""
    # Store it in Neo4J
    neo4j = Neo4jHelper()
    for mission in graph_data["missions"]:
        neo4j.create_node("Mission", mission)
    for reward in graph_data["rewards"]:
        neo4j.create_node("Reward", reward)

    for rel in graph_data["relationships"]:
        neo4j.create_relationship(
            from_label="Mission",
            from_props={"name": rel["from"]["name"], "type": rel["from"]["type"]},
            relationship_type=rel["rel_type"],
            to_label="Reward",
            to_props={"name": rel["to"]["name"]},
            relationship_props=rel.get("properties", {}),
        )
"""


def handle_relics(row_list: List[str]):
    # Build the graph
    graph_data = {"relics": [], "contents": [], "relationships": []}
    current_relic = ""
    cursor = 0
    while cursor < len(row_list):
        row = row_list[cursor]
        cursor += 1
        if len(row) == 1:
            current_relic = row[0].split("(")[0].strip()
            if {"name": current_relic} not in graph_data["relics"]:
                graph_data["relics"].append({"name": current_relic})
        elif len(row) == 2:
            item_name, probability = row[0].strip(), row[1].strip()
            prob_match = re.match(r"(.+?) \(([\d.]+%?)\)", probability)
            if prob_match:
                _, p_value = prob_match.groups()
                content = {"name": item_name.strip()}
                graph_data["contents"].append(content)
                graph_data["relationships"].append(
                    {
                        "from": current_relic,
                        "to": content,
                        "rel_type": "CONTAINS",
                        "properties": {"chance": p_value.strip()},
                    }
                )
        else:
            continue

    # TEMP: store in a raw json
    import json

    with open("outputs/relics.json", "w") as f:
        json.dump(graph_data, f)


def handle_keys(row_list: List[str]):
    # Build the graph
    graph_data = {"keys": [], "rewards": [], "relationships": []}
    current_key = {}
    current_rotation = ""
    cursor = 0
    while cursor < len(row_list):
        row = row_list[cursor]
        cursor += 1
        if len(row) == 1:
            if "Rotation" in row[0]:
                current_rotation = row[0].strip()
            else:
                current_key = {"name": row[0]}
                if current_key not in graph_data["keys"]:
                    graph_data["keys"].append(current_key)
        elif len(row) == 2:
            item_name, probability = row[0].strip(), row[1].strip()
            prob_match = re.match(r"(.+?) \(([\d.]+%?)\)", probability)
            if prob_match:
                _, p_value = prob_match.groups()
                reward = {"name": item_name.strip()}
                graph_data["rewards"].append(reward)
                graph_data["relationships"].append(
                    {
                        "from": current_key,
                        "to": reward,
                        "rel_type": "DROPS",
                        "properties": {
                            "chance": p_value.strip(),
                            "rotation": current_rotation.strip(),
                        },
                    }
                )
        else:
            continue

    # TEMP: store in a raw json
    import json

    with open("outputs/keys.json", "w") as f:
        json.dump(graph_data, f)


def handle_dynamic_location_rewards(row_list: List[List[str]]):
    for sub_list in row_list:
        for element in sub_list:
            if element == "":
                sub_list.remove(element)

    # Build the graph
    graph_data = {"dynamic_locations": [], "rewards": [], "relationships": []}
    current_dynamic_location = {}
    current_rotation: str | None = ""
    cursor = 0
    while cursor < len(row_list):
        row = row_list[cursor]
        cursor += 1
        if len(row) == 1:
            if "Rotation" in row[0]:
                current_rotation = row[0].strip()
            else:
                current_dynamic_location = {"name": row[0]}
                current_rotation = None
                if current_dynamic_location not in graph_data["dynamic_locations"]:
                    graph_data["dynamic_locations"].append(current_dynamic_location)
        elif len(row) == 2:
            item_name, probability = row[0].strip(), row[1].strip()
            prob_match = re.match(r"(.+?) \(([\d.]+%?)\)", probability)
            if prob_match:
                _, p_value = prob_match.groups()
                reward = {"name": item_name.strip()}
                graph_data["rewards"].append(reward)
                properties = {"chance": p_value.strip()}
                if current_rotation:
                    properties["rotation"] = current_rotation.strip()
                graph_data["relationships"].append(
                    {
                        "from": current_dynamic_location,
                        "to": reward,
                        "rel_type": "DROPS",
                        "properties": properties,
                    }
                )
        else:
            continue

    # TEMP: store in a raw json
    import json

    with open("outputs/dynamic_rewards.json", "w") as f:
        json.dump(graph_data, f)


def handle_sorties(row_list: List[List[str]]):
    # Build the graph
    graph_data = {"sorties": [{"name": "Sortie"}], "rewards": [], "relationships": []}
    cursor = 0
    while cursor < len(row_list):
        row = row_list[cursor]
        cursor += 1
        if len(row) == 2:
            item_name, probability = row[0].strip(), row[1].strip()
            prob_match = re.match(r"(.+?) \(([\d.]+%?)\)", probability)
            if prob_match:
                _, p_value = prob_match.groups()
                reward = {"name": item_name.strip()}
                graph_data["rewards"].append(reward)
                graph_data["relationships"].append(
                    {
                        "from": {"name": "Sortie"},
                        "to": reward,
                        "rel_type": "DROPS",
                        "properties": {"chance": p_value.strip()},
                    }
                )
        else:
            continue

    # TEMP: store in a raw json
    import json

    with open("outputs/sorties.json", "w") as f:
        json.dump(graph_data, f)


def handle_bounty_rewards(row_list: List[List[str]], mission_title: str):
    def parse_stages(s):
        if s.strip() == "Final Stage":
            return ["Final Stage"]
        parts = re.split(r",\s*|\s+and\s+", s)
        return [re.sub(r"\band\b", "", part).strip() for part in parts if part.strip()]

    # Build the graph
    graph_data = {
        "bounties": [{"name": mission_title}],
        "levels": [],
        "rewards": [],
        "relationships": [],
    }
    cursor = 0
    current_level = {}
    current_rotation = ""
    current_stages = []
    while cursor < len(row_list):
        row = row_list[cursor]
        cursor += 1
        if len(row) == 1:
            if "Rotation" in row[0]:
                current_rotation = row[0].strip()
            else:
                current_level = {"name": row[0]}
                if current_level not in graph_data["levels"]:
                    graph_data["levels"].append(current_level)
                    graph_data["relationships"].append(
                        {
                            "from": {"name": mission_title},
                            "to": current_level,
                            "rel_type": "HAS",
                        }
                    )
        elif len(row) == 2:
            current_stages = parse_stages(row[1])
        elif len(row) == 3:
            item_name, probability = row[1].strip(), row[2].strip()
            prob_match = re.match(r"(.+?) \(([\d.]+%?)\)", probability)
            if prob_match:
                _, p_value = prob_match.groups()
                reward = {"name": item_name.strip()}
                graph_data["rewards"].append(reward)
                properties = {
                    "chance": p_value.strip(),
                    "rotation": current_rotation.strip(),
                    "stages": current_stages,
                }
                graph_data["relationships"].append(
                    {
                        "from": current_level,
                        "to": reward,
                        "rel_type": "DROPS",
                        "properties": properties,
                    }
                )
        else:
            continue

    # TEMP: store in a raw json
    import json

    with open(
        f"outputs/{mission_title.lower().replace(' ', '_')}_bounties.json", "w"
    ) as f:
        json.dump(graph_data, f)


def handle_general_drops(row_list: List[List[str]], title):
    # Build the graph
    graph_data = {
        "sources": [],
        "drops": [],
        "relationships": [],
    }
    cursor = 0
    current_source = {}
    current_global_drop_chance = ""
    while cursor < len(row_list):
        row = row_list[cursor]
        cursor += 1
        if len(row) == 2:
            source, match = row[0], re.search(r"(\d+\.?\d*)%", row[1])
            current_source = {"name": source.strip()}
            if current_source not in graph_data["sources"]:
                graph_data["sources"].append(current_source)
            if match:
                current_global_drop_chance = match.group(0)
        elif len(row) == 3:
            item_name, probability = row[1].strip(), row[2].strip()
            prob_match = re.match(r"(.+?) \(([\d.]+%?)\)", probability)
            if prob_match:
                _, p_value = prob_match.groups()
                drop = {"name": item_name.strip()}
                graph_data["drops"].append(drop)
                properties = {
                    "chance": p_value.strip(),
                    "global_drop_chance": current_global_drop_chance.strip(),
                    "probability": p_value.strip(),
                }
                graph_data["relationships"].append(
                    {
                        "from": current_source,
                        "to": drop,
                        "rel_type": "DROPS",
                        "properties": properties,
                    }
                )
        else:
            continue

    # TEMP: store in a raw json
    import json

    with open(f"outputs/{title.lower().replace(' ', '_')}.json", "w") as f:
        json.dump(graph_data, f)


# -------------------------------------------------------------------------------------------------


def handle_read_values(title, reading_list):
    if title is None:
        return

    if title == "Missions:":
        handle_missions(reading_list)
    elif title == "Relics:":
        handle_relics(reading_list)
    elif title == "Keys:":
        handle_keys(reading_list)
    elif title == "Dynamic Location Rewards:":
        handle_dynamic_location_rewards(reading_list)
    elif title == "Sorties:":
        handle_sorties(reading_list)
    elif title in [
        "Cetus Bounty Rewards:",
        "Orb Vallis Bounty Rewards:",
        "Cambion Drift Bounty Rewards:",
        "Zariman Bounty Rewards:",
        "Albrecht's Laboratories Bounty Rewards:",
        "Hex Bounty Rewards:",
    ]:
        handle_bounty_rewards(reading_list, title[:-1])
    elif title in ["Mod Drops by Mod:", "Resource Drops by Resource:"]:
        return
    elif " Drops by " in title:
        # FIXME: do not need the title as a parameter here
        handle_general_drops(reading_list, title.replace("/", "-"))


url = "https://www.warframe.com/fr/droptables"
resp = requests.get(url, timeout=10)
resp.raise_for_status()

soup = BeautifulSoup(resp.text, "lxml")
tables = soup.find_all("table")

last_header = None
reading_list = []
with open("outputs/output.txt", "w", encoding="utf-8") as file:
    for table in tables:
        h3 = table.find_previous("h3")
        title = h3.get_text(strip=True) if h3 else None
        if title != last_header:
            handle_read_values(last_header, reading_list)
            last_header = title
            reading_list = []
        print("Table title:", title)
        file.write(str(title) + "\n")
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            values = [cell.get_text(strip=True) for cell in cells]

            if values == [""]:
                continue
            reading_list.append(values)
            print(values)
            file.write("\t" + str(values) + "\n")
    handle_read_values(last_header, reading_list)

    # table = soup.find("table", {"id": "results"})

# -------------------------------------------------------------------------------------------------
