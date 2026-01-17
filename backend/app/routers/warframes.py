from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from database.static.warframe_helper import get_static_db

router = APIRouter(prefix="/api/warframes", tags=["warframes"])

@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_warframes():
    """Get all warframes with basic info"""
    try:
        static_db = get_static_db()
        warframes = static_db.get_all_warframes()
        return warframes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch warframes: {str(e)}")

@router.get("/{unique_name}", response_model=Dict[str, Any])
async def get_warframe_by_unique_name(unique_name: str):
    """Get a specific warframe by uniqueName with all details including abilities"""
    try:
        static_db = get_static_db()
        warframe = static_db.get_warframe_by_unique_name(unique_name)
        
        if not warframe:
            raise HTTPException(status_code=404, detail="Warframe not found")
            
        return warframe
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch warframe: {str(e)}")