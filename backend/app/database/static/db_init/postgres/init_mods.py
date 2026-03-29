import logging
import json
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from models.postgres.mods import Mod
from models.postgres.base import Base
from database.postgres_db import postgres_db

logger = logging.getLogger(__name__)


async def create_mods_tables() -> bool:
    try:
        async with postgres_db._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Created mods table")
        return True
    except Exception as e:
        logger.error(f"While creating mods tables: {e}")
        return False


async def fill_mods_db(session: AsyncSession, mods: List[dict]) -> bool:
    try:
        count = 0
        for mod in mods:
            mod_doc = {
                "unique_name": mod.get("uniqueName", ""),
                "name": mod.get("name", ""),
                "polarity": mod.get("polarity", ""),
                "rarity": mod.get("rarity", ""),
                "type": mod.get("type", ""),
                "subtype": mod.get("subtype"),
                "codex_secret": mod.get("codexSecret", False),
                "base_drain": mod.get("baseDrain", 0),
                "fusion_limit": mod.get("fusionLimit", 0),
                "compat_name": mod.get("compatName"),
                "mod_set": mod.get("modSet"),
                "mod_set_values": json.dumps(mod.get("modSetValues", [])),
                "is_utility": mod.get("isUtility", False),
                "description": json.dumps(mod.get("description")),
                "level_stats": json.dumps(mod.get("levelStats", [])),
                "upgrade_entries": json.dumps(mod.get("upgradeEntries", [])),
                "available_challenges": json.dumps(mod.get("availableChallenges", [])),
            }

            stmt = insert(Mod).values(**mod_doc).on_conflict_do_nothing(index_elements=['unique_name'])
            await session.execute(stmt)
            count += 1

        await session.commit()
        logger.info(f"Inserted {count} mods (skipped duplicates)")
        return True
    except Exception as e:
        logger.error(f"While loading mods database: {e}")
        await session.rollback()
        return False
