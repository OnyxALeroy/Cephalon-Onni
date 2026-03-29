import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from models.postgres.images import Image
from models.postgres.base import Base
from database.postgres_db import postgres_db

logger = logging.getLogger(__name__)


async def create_images_tables() -> bool:
    try:
        async with postgres_db._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Created image table")
        return True
    except Exception as e:
        logger.error(f"While creating images tables: {e}")
        return False


async def fill_img_db(session: AsyncSession, imgs: List[dict]) -> bool:
    try:
        count = 0
        for img in imgs:
            img_doc = {
                "unique_name": img.get("uniqueName", ""),
                "texture_location": img.get("textureLocation", ""),
            }

            stmt = insert(Image).values(**img_doc).on_conflict_do_nothing(index_elements=['unique_name'])
            await session.execute(stmt)
            count += 1

        await session.commit()
        logger.info(f"Inserted {count} images (skipped duplicates)")
        return True
    except Exception as e:
        logger.error(f"While loading images database: {e}")
        await session.rollback()
        return False
