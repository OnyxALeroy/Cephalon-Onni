from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.postgres.warframes import Warframe


class WarframePGRepository:
    @staticmethod
    async def find_all(session: AsyncSession) -> List[Warframe]:
        result = await session.execute(select(Warframe))
        return result.scalars().all()

    @staticmethod
    async def find_by_unique_name(
        session: AsyncSession, unique_name: str
    ) -> Optional[Warframe]:
        result = await session.execute(
            select(Warframe).where(Warframe.unique_name == unique_name)
        )
        return result.scalar_one_or_none()
