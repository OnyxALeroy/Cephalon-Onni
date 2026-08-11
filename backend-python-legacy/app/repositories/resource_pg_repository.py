import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.postgres.resources import Resource


class ResourcePGRepository:
    @staticmethod
    async def exists(session: AsyncSession, unique_name: str) -> bool:
        result = await session.execute(
            select(Resource.unique_name).where(Resource.unique_name == unique_name)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def find_by_unique_name(
        session: AsyncSession, unique_name: str
    ) -> Optional[Resource]:
        result = await session.execute(
            select(Resource).where(Resource.unique_name == unique_name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def find_all_basic(session: AsyncSession) -> List[dict]:
        result = await session.execute(
            select(
                Resource.unique_name,
                Resource.name,
                Resource.parent_name,
            )
        )
        return [
            {
                "uniqueName": row.unique_name,
                "name": row.name,
                "parentName": row.parent_name,
            }
            for row in result.all()
        ]
