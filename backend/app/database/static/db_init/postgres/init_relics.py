import logging
import json
from typing import List, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from models.postgres.relics import Relic
from models.postgres.base import Base
from database.postgres_db import postgres_db

logger = logging.getLogger(__name__)


async def create_relic_tables() -> bool:
    try:
        async with postgres_db._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Created relics table")
        return True
    except Exception as e:
        logger.error(f"While creating relic tables: {e}")
        return False


async def fill_relic_db(session: AsyncSession, relics: List[Union[dict, str]]) -> bool:
    try:
        count = 0
        for relic in relics:
            if isinstance(relic, str):
                continue
                
            relic_doc = {
                "unique_name": relic.get("uniqueName", ""),
                "name": relic.get("name", ""),
                "codex_secret": relic.get("codexSecret", False),
                "description": relic.get("description", ""),
                "relic_rewards": json.dumps(relic.get("relicRewards", [])),
            }

            stmt = insert(Relic).values(**relic_doc).on_conflict_do_nothing(index_elements=['unique_name'])
            await session.execute(stmt)
            count += 1

        await session.commit()
        logger.info(f"Inserted {count} relics (skipped duplicates)")
        return True
    except Exception as e:
        logger.error(f"While loading relics database: {e}")
        await session.rollback()
        return False
