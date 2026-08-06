from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.postgres.warframes import Warframe


class WarframePGRepository:
    @staticmethod
    async def exists(session: AsyncSession, unique_name: str) -> bool:
        result = await session.execute(
            select(Warframe.unique_name).where(Warframe.unique_name == unique_name)
        )
        return result.scalar_one_or_none() is not None

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

    @staticmethod
    async def find_all_basic(session: AsyncSession) -> List[dict]:
        result = await session.execute(
            select(
                Warframe.unique_name,
                Warframe.name,
                Warframe.mastery_req,
            )
        )
        return [
            {
                "uniqueName": row.unique_name,
                "name": row.name,
                "masteryReq": row.mastery_req,
            }
            for row in result.all()
        ]
