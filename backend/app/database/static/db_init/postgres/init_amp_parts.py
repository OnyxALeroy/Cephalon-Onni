import logging
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from models.postgres.amp_parts import AmpPart
from models.postgres.base import Base
from database.postgres_db import postgres_db

logger = logging.getLogger(__name__)

COMPONENT_MAP = {
    "/Barrel/": "Prism",
    "/Chassis/": "Scaffold",
    "/Grip/": "Brace",
}


async def create_amp_tables() -> bool:
    try:
        async with postgres_db._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Created amp_parts table")
        return True
    except Exception as e:
        logger.error(f"While creating amp_parts tables: {e}")
        return False


def _get_component_type(unique_name: str) -> str:
    for path_segment, component_type in COMPONENT_MAP.items():
        if path_segment in unique_name:
            return component_type
    return "Unknown"


def _is_amp_part(item: dict) -> bool:
    return "/OperatorAmplifiers/" in item.get("uniqueName", "")


async def fill_amp_db(session: AsyncSession, weapons: List[dict]) -> bool:
    try:
        count = 0
        for weapon in weapons:
            if not _is_amp_part(weapon):
                continue

            amp_doc = {
                "unique_name": weapon.get("uniqueName", ""),
                "name": weapon.get("name", ""),
                "description": weapon.get("description", ""),
                "codex_secret": weapon.get("codexSecret", False),
                "component_type": _get_component_type(weapon.get("uniqueName", "")),
            }

            stmt = insert(AmpPart).values(**amp_doc).on_conflict_do_nothing(index_elements=["unique_name"])
            await session.execute(stmt)
            count += 1

        await session.commit()
        logger.info(f"Inserted {count} amp parts (skipped duplicates)")
        return True
    except Exception as e:
        logger.error(f"While loading amp_parts database: {e}")
        await session.rollback()
        return False
