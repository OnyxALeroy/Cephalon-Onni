from fastapi import APIRouter, HTTPException

from services.worldstate import get_worldstate_cache

router = APIRouter(prefix="/api/worldstate", tags=["worldstate"])


@router.get("")
async def get_worldstate():
    cache = get_worldstate_cache()
    if cache is None:
        raise HTTPException(status_code=503, detail="WorldState service not initialized")

    worldstate = await cache.get()
    if worldstate is None:
        raise HTTPException(status_code=503, detail="WorldState data not available yet")

    return worldstate.model_dump()
