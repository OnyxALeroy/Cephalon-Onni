import logging
import json
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from models.postgres.recipes import Recipe
from models.postgres.base import Base
from database.postgres_db import postgres_db

logger = logging.getLogger(__name__)


async def create_recipe_tables() -> bool:
    try:
        async with postgres_db._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Created recipes table")
        return True
    except Exception as e:
        logger.error(f"While creating recipe tables: {e}")
        return False


async def fill_recipes_db(session: AsyncSession, recipes: List[dict]) -> bool:
    try:
        count = 0
        for recipe in recipes:
            recipe_doc = {
                "unique_name": recipe.get("uniqueName", ""),
                "build_price": recipe.get("buildPrice", 0),
                "build_time": recipe.get("buildTime", 0),
                "skip_build_time_price": recipe.get("skipBuildTimePrice", 0),
                "consume_on_use": recipe.get("consumeOnUse", True),
                "num": recipe.get("num", 1),
                "codex_secret": recipe.get("codexSecret", False),
                "result_type": recipe.get("resultType", ""),
                "ingredients": json.dumps(recipe.get("ingredients", [])),
            }

            stmt = insert(Recipe).values(**recipe_doc).on_conflict_do_nothing(index_elements=['unique_name'])
            await session.execute(stmt)
            count += 1

        await session.commit()
        logger.info(f"Inserted {count} recipes (skipped duplicates)")
        return True
    except Exception as e:
        logger.error(f"While loading recipes database: {e}")
        await session.rollback()
        return False
