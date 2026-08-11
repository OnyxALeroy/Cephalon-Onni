from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.postgres.mods import Mod


class ModPGRepository:
    @staticmethod
    async def exists(session: AsyncSession, unique_name: str) -> bool:
        result = await session.execute(
            select(Mod.unique_name).where(Mod.unique_name == unique_name)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def find_by_unique_name(
        session: AsyncSession, unique_name: str
    ) -> Optional[Mod]:
        result = await session.execute(
            select(Mod).where(Mod.unique_name == unique_name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def find_all_basic(session: AsyncSession) -> List[dict]:
        result = await session.execute(
            select(
                Mod.unique_name,
                Mod.name,
                Mod.type,
                Mod.rarity,
                Mod.polarity,
            )
        )
        return [
            {
                "uniqueName": row.unique_name,
                "name": row.name,
                "type": row.type,
                "rarity": row.rarity,
                "polarity": row.polarity,
            }
            for row in result.all()
        ]
