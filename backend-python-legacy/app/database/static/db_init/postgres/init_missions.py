import logging
import json
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert

from models.postgres.missions import Mission
from models.postgres.base import Base
from database.postgres_db import postgres_db

logger = logging.getLogger(__name__)


async def create_mission_tables() -> bool:
    try:
        async with postgres_db._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Created missions table")
        return True
    except Exception as e:
        logger.error(f"While creating mission tables: {e}")
        return False


async def fill_missions_db(session: AsyncSession, missions: List[dict]) -> bool:
    try:
        count = 0
        for mission in missions:
            mission_doc = {
                "unique_name": mission.get("uniqueName", ""),
                "mission_name": mission.get("name", mission.get("missionName", "")),
                "system_name": mission.get("systemName", ""),
                "planet": mission.get("planet", ""),
                "type": mission.get("type", ""),
                "node_type": mission.get("nodeType", 0),
                "faction_index": mission.get("factionIndex", 0),
                "mastery_req": mission.get("masteryReq", 0),
                "min_enemy_level": mission.get("minEnemyLevel", 0),
                "max_enemy_level": mission.get("maxEnemyLevel", 0),
                "mission_index": mission.get("missionIndex", 0),
                "system_index": mission.get("systemIndex", 0),
                "drops": json.dumps(mission.get("drops", [])),
            }

            stmt = insert(Mission).values(**mission_doc).on_conflict_do_nothing(index_elements=['unique_name'])
            await session.execute(stmt)
            count += 1

        await session.commit()
        logger.info(f"Inserted {count} missions (skipped duplicates)")
        return True
    except Exception as e:
        logger.error(f"While loading missions database: {e}")
        await session.rollback()
        return False
