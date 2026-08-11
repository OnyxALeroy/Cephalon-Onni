import logging
from typing import Any, Dict

import httpx

from database.postgres_db import postgres_db
from models.postgres.weapons import Weapon
from models.postgres.warframes import Warframe
from models.postgres.mods import Mod

logger = logging.getLogger(__name__)

WARFRAME_API_BASE = "https://api.warframe.com/v1"
ITEMS_API_BASE = "https://api.warframe.market/v1"


def _flatten_item(item: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Flatten nested JSON fields for PostgreSQL storage."""
    flat = {}
    skip_keys = {"components", "levelStats", "imageName", "patchLogs", "polyCount"}
    
    for key, value in item.items():
        if key in skip_keys:
            continue
        
        flat_key = f"{prefix}{key}" if prefix else key
        
        if isinstance(value, dict):
            flat.update(_flatten_item(value, f"{flat_key}_"))
        elif isinstance(value, list):
            try:
                import json
                flat[flat_key] = json.dumps(value) if value else None
            except:
                flat[flat_key] = str(value) if value else None
        else:
            flat[flat_key] = value
    
    return flat


def _weapon_from_api(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform API weapon data to database format."""
    return {
        "unique_name": data.get("uniqueName", ""),
        "name": data.get("name", ""),
        "codex_secret": data.get("codexSecret", False),
        "critical_chance": data.get("criticalChance", 0.0),
        "critical_multiplier": data.get("criticalMultiplier", 0.0),
        "damage_per_shot": data.get("damagePerShot", []),
        "description": data.get("description", ""),
        "fire_rate": data.get("fireRate", 0.0),
        "mastery_req": data.get("masteryReq", 0),
        "omega_attenuation": data.get("omegaAttenuation", 0.0),
        "proc_chance": data.get("procChance", 0.0),
        "product_category": data.get("productCategory", ""),
        "total_damage": data.get("totalDamage", 0),
        "accuracy": data.get("accuracy"),
        "blocking_angle": data.get("blockingAngle"),
        "combo_duration": data.get("comboDuration"),
        "exclude_from_codex": data.get("excludeFromCodex", False),
        "follow_through": data.get("followThrough"),
        "heavy_attack_damage": data.get("heavyAttackDamage"),
        "heavy_slam_attack": data.get("heavySlamAttack"),
        "heavy_slam_radial_damage": data.get("heavySlamRadialDamage"),
        "heavy_slam_radius": data.get("heavySlamRadius"),
        "magazine_size": data.get("magazineSize"),
        "max_level_cap": data.get("maxLevelCap"),
        "multishot": data.get("multishot"),
        "noise": data.get("noise"),
        "prime_omega_attenuation": data.get("primeOmegaAttenuation"),
        "range": data.get("range"),
        "reload_time": data.get("reloadTime"),
        "sentinel": data.get("sentinel", False),
        "slam_attack": data.get("slamAttack"),
        "slam_radial_damage": data.get("slamRadialDamage"),
        "slam_radius": data.get("slamRadius"),
        "slide_attack": data.get("slideAttack"),
        "slot": data.get("slot"),
        "trigger": data.get("trigger"),
        "wind_up": data.get("windUp"),
    }


def _warframe_from_api(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform API warframe data to database format."""
    return {
        "unique_name": data.get("uniqueName", ""),
        "name": data.get("name", ""),
        "parent_name": data.get("parentName", ""),
        "description": data.get("description", ""),
        "health": data.get("health", 0),
        "shield": data.get("shield", 0),
        "armor": data.get("armor", 0),
        "stamina": data.get("stamina", 0),
        "power": data.get("power", 0),
        "codex_secret": data.get("codexSecret", False),
        "mastery_req": data.get("masteryReq", 0),
        "sprint_speed": data.get("sprintSpeed", 1.0),
        "passive_description": data.get("passiveDescription"),
        "exalted": data.get("exalted", []),
        "abilities": data.get("abilities", []),
        "product_category": data.get("productCategory", "Suits"),
    }


def _mod_from_api(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transform API mod data to database format."""
    return {
        "unique_name": data.get("uniqueName", ""),
        "name": data.get("name", ""),
        "polarity": data.get("polarity", ""),
        "rarity": data.get("rarity", ""),
        "type": data.get("type", ""),
        "subtype": data.get("subtype"),
        "codex_secret": data.get("codexSecret", False),
        "base_drain": data.get("baseDrain", 0),
        "fusion_limit": data.get("fusionLimit", 0),
        "compat_name": data.get("compatName"),
        "mod_set": data.get("modSet"),
        "mod_set_values": data.get("modSetValues"),
        "is_utility": data.get("isUtility", False),
        "description": data.get("description"),
        "level_stats": data.get("levelStats", []),
        "upgrade_entries": data.get("upgradeEntries", []),
        "available_challenges": data.get("availableChallenges", []),
    }


async def sync_weapons(session) -> int:
    """Fetch and sync weapons from Warframe API."""
    count = 0
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(f"{WARFRAME_API_BASE}/items")
            response.raise_for_status()
            data = response.json()
            
            weapons_data = data.get("payload", {}).get("items", [])
            
            for item in weapons_data:
                if "weapon" in item.get("url_name", "").lower() or "sentinel" in item.get("url_name", "").lower():
                    try:
                        detail_response = await client.get(f"{WARFRAME_API_BASE}/item/{item['url_name']}")
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            item_data = detail_data.get("payload", {}).get("item", {})
                            
                            if item_data.get("type") in ["Primary", "Secondary", "Melee", "Arch-Gun", "Arch-Melee", "Melee Weapon", "Shotgun", "Rifle", "Pistol", "Sentinel Weapon"]:
                                weapon_dict = _weapon_from_api(item_data)
                                weapon = Weapon(**weapon_dict)
                                session.add(weapon)
                                count += 1
                    except Exception as e:
                        logger.warning(f"Failed to fetch weapon {item['url_name']}: {e}")
                        continue
            
            await session.commit()
            logger.info(f"Synced {count} weapons")
    except Exception as e:
        logger.error(f"Failed to sync weapons: {e}")
        await session.rollback()
    
    return count


async def sync_warframes(session) -> int:
    """Fetch and sync warframes from Warframe API."""
    count = 0
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(f"{WARFRAME_API_BASE}/items")
            response.raise_for_status()
            data = response.json()
            
            items_data = data.get("payload", {}).get("items", [])
            
            for item in items_data:
                url_name = item.get("url_name", "")
                if "warframe" in url_name.lower() and "prime" not in url_name.lower() and "component" not in url_name.lower():
                    try:
                        detail_response = await client.get(f"{WARFRAME_API_BASE}/item/{url_name}")
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            item_data = detail_data.get("payload", {}).get("item", {})
                            
                            if item_data.get("productCategory") in ["Suits", "SpaceSuits", "MechSuits"]:
                                warframe_dict = _warframe_from_api(item_data)
                                warframe = Warframe(**warframe_dict)
                                session.add(warframe)
                                count += 1
                    except Exception as e:
                        logger.warning(f"Failed to fetch warframe {url_name}: {e}")
                        continue
            
            await session.commit()
            logger.info(f"Synced {count} warframes")
    except Exception as e:
        logger.error(f"Failed to sync warframes: {e}")
        await session.rollback()
    
    return count


async def sync_mods(session) -> int:
    """Fetch and sync mods from Warframe API."""
    count = 0
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(f"{WARFRAME_API_BASE}/items")
            response.raise_for_status()
            data = response.json()
            
            items_data = data.get("payload", {}).get("items", [])
            
            for item in items_data:
                url_name = item.get("url_name", "")
                if "mod" in url_name.lower():
                    try:
                        detail_response = await client.get(f"{WARFRAME_API_BASE}/item/{url_name}")
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            item_data = detail_data.get("payload", {}).get("item", {})
                            
                            mod_dict = _mod_from_api(item_data)
                            mod = Mod(**mod_dict)
                            session.add(mod)
                            count += 1
                    except Exception as e:
                        logger.warning(f"Failed to fetch mod {url_name}: {e}")
                        continue
            
            await session.commit()
            logger.info(f"Synced {count} mods")
    except Exception as e:
        logger.error(f"Failed to sync mods: {e}")
        await session.rollback()
    
    return count


async def sync_static_data() -> Dict[str, int]:
    """Sync all static data from Warframe API to PostgreSQL."""
    if not postgres_db._engine:
        postgres_db.initialize()
    
    results = {"weapons": 0, "warframes": 0, "mods": 0}
    
    async with postgres_db._session_factory() as session:
        try:
            logger.info("Starting static data sync from Warframe API...")
            
            results["warframes"] = await sync_warframes(session)
            results["weapons"] = await sync_weapons(session)
            results["mods"] = await sync_mods(session)
            
            logger.info(f"Static data sync complete: {results}")
        except Exception as e:
            logger.error(f"Static data sync failed: {e}")
    
    return results
