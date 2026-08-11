from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.postgres.missions import Mission


class MissionRepository:
    @staticmethod
    async def find_all(session: AsyncSession) -> List[Mission]:
        result = await session.execute(select(Mission))
        return result.scalars().all()

    @staticmethod
    async def search_by_name(
        session: AsyncSession, name: str, limit: int = 50
    ) -> List[Mission]:
        query = select(Mission).where(Mission.mission_name.ilike(f"%{name}%")).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()
