from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.postgres.drop_sources import DropSource


class DropSourceRepository:
    @staticmethod
    async def search_by_name(
        session: AsyncSession, name: str, limit: int = 50
    ) -> List[DropSource]:
        query = select(DropSource).where(DropSource.name.ilike(f"%{name}%")).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def find_by_source_type(
        session: AsyncSession, source_type: str, name: str = "", limit: int = 50
    ) -> List[DropSource]:
        query = select(DropSource).where(DropSource.source_type == source_type.lower())
        if name:
            query = query.where(DropSource.name.ilike(f"%{name}%"))
        query = query.limit(limit)
        result = await session.execute(query)
        return result.scalars().all()
