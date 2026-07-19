import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.postgres.amp_parts import AmpPart


class AmpPartPGRepository:
    @staticmethod
    async def exists(session: AsyncSession, unique_name: str) -> bool:
        result = await session.execute(
            select(AmpPart.unique_name).where(AmpPart.unique_name == unique_name)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def find_by_unique_name(
        session: AsyncSession, unique_name: str
    ) -> Optional[AmpPart]:
        result = await session.execute(
            select(AmpPart).where(AmpPart.unique_name == unique_name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def find_by_component_type(
        session: AsyncSession, component_type: str
    ) -> List[dict]:
        result = await session.execute(
            select(
                AmpPart.unique_name,
                AmpPart.name,
                AmpPart.component_type,
            ).where(AmpPart.component_type == component_type)
        )
        return [
            {
                "uniqueName": row.unique_name,
                "name": row.name,
                "componentType": row.component_type,
            }
            for row in result.all()
        ]

    @staticmethod
    async def find_all_basic(session: AsyncSession) -> List[dict]:
        result = await session.execute(
            select(
                AmpPart.unique_name,
                AmpPart.name,
                AmpPart.component_type,
            )
        )
        return [
            {
                "uniqueName": row.unique_name,
                "name": row.name,
                "componentType": row.component_type,
            }
            for row in result.all()
        ]
