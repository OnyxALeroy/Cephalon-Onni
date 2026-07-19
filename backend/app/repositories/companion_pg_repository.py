from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.postgres.companions import Companion


class CompanionPGRepository:
    @staticmethod
    async def exists(session: AsyncSession, unique_name: str) -> bool:
        result = await session.execute(
            select(Companion.unique_name).where(Companion.unique_name == unique_name)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def find_by_unique_name(
        session: AsyncSession, unique_name: str
    ) -> Optional[Companion]:
        result = await session.execute(
            select(Companion).where(Companion.unique_name == unique_name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def find_all_basic(session: AsyncSession) -> List[dict]:
        result = await session.execute(
            select(
                Companion.unique_name,
                Companion.name,
                Companion.product_category,
            )
        )
        return [
            {
                "uniqueName": row.unique_name,
                "name": row.name,
                "productCategory": row.product_category,
            }
            for row in result.all()
        ]
