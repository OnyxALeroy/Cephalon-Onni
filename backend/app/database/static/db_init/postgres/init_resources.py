import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from models.postgres.resources import Resource
from models.postgres.base import Base
from database.postgres_db import postgres_db

logger = logging.getLogger(__name__)


async def create_resource_tables() -> bool:
    try:
        async with postgres_db._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Created resources table")
        return True
    except Exception as e:
        logger.error(f"While creating resource tables: {e}")
        return False


async def fill_resource_db(session: AsyncSession, resources: List[dict]) -> bool:
    try:
        count = 0
        for resource in resources:
            resource_doc = {
                "unique_name": resource.get("uniqueName", ""),
                "name": resource.get("name", ""),
                "description": resource.get("description", ""),
                "codex_secret": resource.get("codexSecret", False),
                "parent_name": resource.get("parentName", ""),
                "exclude_from_codex": resource.get("excludeFromCodex", False),
                "show_in_inventory": resource.get("showInInventory", False),
                "prime_selling_price": resource.get("primeSellingPrice"),
            }

            stmt = insert(Resource).values(**resource_doc).on_conflict_do_nothing(index_elements=['unique_name'])
            await session.execute(stmt)
            count += 1

        await session.commit()
        logger.info(f"Inserted {count} resources (skipped duplicates)")
        return True
    except Exception as e:
        logger.error(f"While loading resource database: {e}")
        await session.rollback()
        return False
