from typing import Any, Dict, List

from database.static.db_helpers import connect_to_mongodb
from fastapi import APIRouter, Depends, HTTPException
from pymongo import MongoClient

router = APIRouter(prefix="/api/warframes", tags=["warframes"])


# Dependency to get MongoDB client
def get_static_db_client():
    client = connect_to_mongodb()
    if not client:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")
    try:
        yield client
    finally:
        if client:
            client.close()


@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_warframes(client: MongoClient = Depends(get_static_db_client)):
    """Get all warframes with basic info"""
    try:
        db = client["cephalon_onni"]
        warframes_collection = db["warframes"]
        warframes = []
        for w in warframes_collection.find({}):
            w["_id"] = str(w["_id"])
            warframes.append(w)
        return warframes
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch warframes: {str(e)}"
        )


@router.get("/{unique_name}", response_model=Dict[str, Any])
async def get_warframe_by_unique_name(
    unique_name: str, client: MongoClient = Depends(get_static_db_client)
):
    """Get a specific warframe by uniqueName with all details including abilities"""
    try:
        db = client["cephalon_onni"]
        warframes_collection = db["warframes"]
        warframe = warframes_collection.find_one({"uniqueName": unique_name})

        if not warframe:
            raise HTTPException(status_code=404, detail="Warframe not found")

        warframe["_id"] = str(warframe["_id"])
        return warframe
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch warframe: {str(e)}"
        )
