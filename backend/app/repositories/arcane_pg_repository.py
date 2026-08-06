from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.postgres.arcanes import Arcane


class ArcanePGRepository:
    @staticmethod
    async def exists(session: AsyncSession, unique_name: str) -> bool:
        result = await session.execute(
            select(Arcane.unique_name).where(Arcane.unique_name == unique_name)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def find_by_unique_name(
        session: AsyncSession, unique_name: str
    ) -> Optional[Arcane]:
        result = await session.execute(
            select(Arcane).where(Arcane.unique_name == unique_name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def find_all_basic(session: AsyncSession) -> List[dict]:
        result = await session.execute(
            select(
                Arcane.unique_name,
                Arcane.name,
                Arcane.rarity,
            )
        )
        return [
            {
                "uniqueName": row.unique_name,
                "name": row.name,
                "rarity": row.rarity,
            }
            for row in result.all()
        ]
