import logging
import json
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from models.postgres.warframes import Warframe
from models.postgres.base import Base
from database.postgres_db import postgres_db

logger = logging.getLogger(__name__)


async def create_warframe_tables() -> bool:
    try:
        async with postgres_db._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Created warframes table")
        return True
    except Exception as e:
        logger.error(f"While creating warframe tables: {e}")
        return False


async def fill_warframe_db(session: AsyncSession, warframes: List[dict]) -> bool:
    try:
        count = 0
        for warframe in warframes:
            warframe_doc = {
                "unique_name": warframe.get("uniqueName", ""),
                "name": warframe.get("name", ""),
                "parent_name": warframe.get("parentName", ""),
                "description": warframe.get("description", ""),
                "health": warframe.get("health", 0),
                "shield": warframe.get("shield", 0),
                "armor": warframe.get("armor", 0),
                "stamina": warframe.get("stamina", 0),
                "power": warframe.get("power", 0),
                "codex_secret": warframe.get("codexSecret", False),
                "mastery_req": warframe.get("masteryReq", 0),
                "sprint_speed": warframe.get("sprintSpeed", 1.0),
                "passive_description": warframe.get("passiveDescription"),
                "exalted": json.dumps(warframe.get("exalted", [])),
                "abilities": json.dumps(warframe.get("abilities", [])),
                "product_category": warframe.get("productCategory", "Suits"),
            }

            stmt = insert(Warframe).values(**warframe_doc).on_conflict_do_nothing(index_elements=['unique_name'])
            await session.execute(stmt)
            count += 1

        await session.commit()
        logger.info(f"Inserted {count} warframes (skipped duplicates)")
        return True
    except Exception as e:
        logger.error(f"While loading warframe database: {e}")
        await session.rollback()
        return False
