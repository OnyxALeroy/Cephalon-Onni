import json
from typing import Any, Dict, List, Optional

from dependencies import get_postgres_session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.postgres.warframes import Warframe

router = APIRouter(prefix="/api/warframes", tags=["warframes"])


def _parse_json(value: Any) -> Any:
    """Parse JSON string to Python object."""
    if value is None:
        return None
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_warframes(session: AsyncSession = Depends(get_postgres_session)):
    """Get all warframes with basic info"""
    try:
        result = await session.execute(select(Warframe))
        warframes = result.scalars().all()
        return [
            {
                "id": w.id,
                "uniqueName": w.unique_name,
                "name": w.name,
                "parentName": w.parent_name,
                "description": w.description,
                "health": w.health,
                "shield": w.shield,
                "armor": w.armor,
                "stamina": w.stamina,
                "power": w.power,
                "codexSecret": w.codex_secret,
                "masteryReq": w.mastery_req,
                "sprintSpeed": w.sprint_speed,
                "productCategory": w.product_category,
            }
            for w in warframes
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch warframes: {str(e)}"
        )


@router.get("/{unique_name}", response_model=Dict[str, Any])
async def get_warframe_by_unique_name(
    unique_name: str, session: AsyncSession = Depends(get_postgres_session)
):
    """Get a specific warframe by uniqueName with all details including abilities"""
    try:
        result = await session.execute(
            select(Warframe).where(Warframe.unique_name == unique_name)
        )
        warframe = result.scalar_one_or_none()

        if not warframe:
            raise HTTPException(status_code=404, detail="Warframe not found")

        return {
            "id": warframe.id,
            "uniqueName": warframe.unique_name,
            "name": warframe.name,
            "parentName": warframe.parent_name,
            "description": warframe.description,
            "health": warframe.health,
            "shield": warframe.shield,
            "armor": warframe.armor,
            "stamina": warframe.stamina,
            "power": warframe.power,
            "codexSecret": warframe.codex_secret,
            "masteryReq": warframe.mastery_req,
            "sprintSpeed": warframe.sprint_speed,
            "passiveDescription": warframe.passive_description,
            "exalted": _parse_json(warframe.exalted),
            "abilities": _parse_json(warframe.abilities),
            "productCategory": warframe.product_category,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch warframe: {str(e)}"
        )
