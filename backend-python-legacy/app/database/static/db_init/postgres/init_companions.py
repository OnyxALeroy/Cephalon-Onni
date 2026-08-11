import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from models.postgres.companions import Companion
from models.postgres.base import Base
from database.postgres_db import postgres_db

logger = logging.getLogger(__name__)


async def create_companion_tables() -> bool:
    try:
        async with postgres_db._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Created companions table")
        return True
    except Exception as e:
        logger.error(f"While creating companion tables: {e}")
        return False


async def fill_companion_db(session: AsyncSession, companions: List[dict]) -> bool:
    try:
        count = 0
        for companion in companions:
            companion_doc = {
                "unique_name": companion.get("uniqueName", ""),
                "name": companion.get("name", ""),
                "description": companion.get("description", ""),
                "health": companion.get("health", 0),
                "shield": companion.get("shield", 0),
                "armor": companion.get("armor", 0),
                "stamina": companion.get("stamina", 0),
                "power": companion.get("power", 0),
                "codex_secret": companion.get("codexSecret", False),
                "exclude_from_codex": companion.get("excludeFromCodex", False),
                "product_category": companion.get("productCategory", ""),
            }

            stmt = insert(Companion).values(**companion_doc).on_conflict_do_nothing(index_elements=['unique_name'])
            await session.execute(stmt)
            count += 1

        await session.commit()
        logger.info(f"Inserted {count} companions (skipped duplicates)")
        return True
    except Exception as e:
        logger.error(f"While loading companion database: {e}")
        await session.rollback()
        return False
