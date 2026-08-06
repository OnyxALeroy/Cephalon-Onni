import logging
import json
from typing import List, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from models.postgres.relics import Relic
from models.postgres.arcanes import Arcane
from models.postgres.base import Base
from database.postgres_db import postgres_db

logger = logging.getLogger(__name__)


async def create_relic_tables() -> bool:
    try:
        async with postgres_db._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Created relics and arcanes tables")
        return True
    except Exception as e:
        logger.error(f"While creating relic tables: {e}")
        return False


async def fill_relic_db(session: AsyncSession, relics: List[Union[dict, str]]) -> bool:
    try:
        relic_count = 0
        arcane_count = 0
        for element in relics:
            if isinstance(element, str):
                continue

            if "relicRewards" in element:
                relic_doc = {
                    "unique_name": element.get("uniqueName", ""),
                    "name": element.get("name", ""),
                    "codex_secret": element.get("codexSecret", False),
                    "description": element.get("description", ""),
                    "relic_rewards": json.dumps(element.get("relicRewards", [])),
                }
                stmt = insert(Relic).values(**relic_doc).on_conflict_do_nothing(index_elements=['unique_name'])
                await session.execute(stmt)
                relic_count += 1
            elif "rarity" in element or "levelStats" in element:
                arcane_doc = {
                    "unique_name": element.get("uniqueName", ""),
                    "name": element.get("name", ""),
                    "codex_secret": element.get("codexSecret", False),
                    "rarity": element.get("rarity"),
                    "level_stats": json.dumps(element.get("levelStats", [])),
                }
                stmt = insert(Arcane).values(**arcane_doc).on_conflict_do_nothing(index_elements=['unique_name'])
                await session.execute(stmt)
                arcane_count += 1

        await session.commit()
        logger.info(f"Inserted {relic_count} relics and {arcane_count} arcanes (skipped duplicates)")
        return True
    except Exception as e:
        logger.error(f"While loading relics database: {e}")
        await session.rollback()
        return False
