from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.postgres.weapons import Weapon


class WeaponPGRepository:
    @staticmethod
    async def exists(session: AsyncSession, unique_name: str) -> bool:
        result = await session.execute(
            select(Weapon.unique_name).where(Weapon.unique_name == unique_name)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def find_by_unique_name(
        session: AsyncSession, unique_name: str
    ) -> Optional[Weapon]:
        result = await session.execute(
            select(Weapon).where(Weapon.unique_name == unique_name)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def find_all_basic(session: AsyncSession) -> List[dict]:
        result = await session.execute(
            select(
                Weapon.unique_name,
                Weapon.name,
                Weapon.mastery_req,
                Weapon.product_category,
            )
        )
        return [
            {
                "uniqueName": row.unique_name,
                "name": row.name,
                "masteryReq": row.mastery_req,
                "productCategory": row.product_category,
            }
            for row in result.all()
        ]
