import logging
import re
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from models.postgres.drop_sources import DropSource
from models.postgres.base import Base
from database.postgres_db import postgres_db

logger = logging.getLogger(__name__)


def parse_chance(chance_str) -> float:
    """Parse chance string like '50.00%' to float 50.00."""
    if chance_str is None:
        return 0.0
    if isinstance(chance_str, (int, float)):
        return float(chance_str)
    match = re.match(r"([\d.]+)%?", str(chance_str))
    if match:
        return float(match.group(1))
    return 0.0


async def create_drop_source_tables() -> bool:
    try:
        async with postgres_db._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Created drop_sources table")
        return True
    except Exception as e:
        logger.error(f"While creating drop source tables: {e}")
        return False


async def fill_drop_sources_db(session: AsyncSession, drop_sources: List[dict]) -> bool:
    try:
        count = 0
        for ds in drop_sources:
            ds_doc = {
                "name": ds.get("name", ""),
                "source_type": ds.get("source_type", ds.get("type", "")),
                "source": ds.get("source", ""),
                "chance": parse_chance(ds.get("chance")),
                "rotation": ds.get("rotation"),
            }

            stmt = insert(DropSource).values(**ds_doc).on_conflict_do_nothing()
            await session.execute(stmt)
            count += 1

        await session.commit()
        logger.info(f"Inserted {count} drop sources (skipped duplicates)")
        return True
    except Exception as e:
        logger.error(f"While loading drop sources database: {e}")
        await session.rollback()
        return False
