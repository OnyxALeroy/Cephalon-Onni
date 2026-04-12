import logging
import json
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from models.postgres.weapons import Weapon
from models.postgres.base import Base
from database.postgres_db import postgres_db

logger = logging.getLogger(__name__)


async def create_weapon_tables() -> bool:
    try:
        async with postgres_db._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Created weapons table")
        return True
    except Exception as e:
        logger.error(f"While creating weapon tables: {e}")
        return False


async def fill_weapons_db(session: AsyncSession, weapons: List[dict]) -> bool:
    try:
        count = 0
        for weapon in weapons:
            weapon_doc = {
                "unique_name": weapon.get("uniqueName", ""),
                "name": weapon.get("name", ""),
                "codex_secret": weapon.get("codexSecret", False),
                "critical_chance": weapon.get("criticalChance", 0.0),
                "critical_multiplier": weapon.get("criticalMultiplier", 0.0),
                "damage_per_shot": json.dumps(weapon.get("damagePerShot", [])),
                "description": weapon.get("description", ""),
                "fire_rate": weapon.get("fireRate", 0.0),
                "mastery_req": weapon.get("masteryReq", 0),
                "omega_attenuation": weapon.get("omegaAttenuation", 0.0),
                "proc_chance": weapon.get("procChance", 0.0),
                "product_category": weapon.get("productCategory", ""),
                "total_damage": weapon.get("totalDamage", 0),
                "accuracy": weapon.get("accuracy"),
                "blocking_angle": weapon.get("blockingAngle"),
                "combo_duration": weapon.get("comboDuration"),
                "exclude_from_codex": weapon.get("excludeFromCodex", False),
                "follow_through": weapon.get("followThrough"),
                "heavy_attack_damage": weapon.get("heavyAttackDamage"),
                "heavy_slam_attack": weapon.get("heavySlamAttack"),
                "heavy_slam_radial_damage": weapon.get("heavySlamRadialDamage"),
                "heavy_slam_radius": weapon.get("heavySlamRadius"),
                "magazine_size": weapon.get("magazineSize"),
                "max_level_cap": weapon.get("maxLevelCap"),
                "multishot": weapon.get("multishot"),
                "noise": weapon.get("noise"),
                "prime_omega_attenuation": weapon.get("primeOmegaAttenuation"),
                "range": weapon.get("range"),
                "reload_time": weapon.get("reloadTime"),
                "sentinel": weapon.get("sentinel", False),
                "slam_attack": weapon.get("slamAttack"),
                "slam_radial_damage": weapon.get("slamRadialDamage"),
                "slam_radius": weapon.get("slamRadius"),
                "slide_attack": weapon.get("slideAttack"),
                "slot": weapon.get("slot"),
                "trigger": weapon.get("trigger"),
                "wind_up": weapon.get("windUp"),
            }

            stmt = insert(Weapon).values(**weapon_doc).on_conflict_do_nothing(index_elements=['unique_name'])
            await session.execute(stmt)
            count += 1

        await session.commit()
        logger.info(f"Inserted {count} weapons (skipped duplicates)")
        return True
    except Exception as e:
        logger.error(f"While loading weapons database: {e}")
        await session.rollback()
        return False
