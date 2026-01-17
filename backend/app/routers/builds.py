from bson import ObjectId
from fastapi import APIRouter, HTTPException, Request, Depends
from typing import List

from models.builds import BuildCreate, BuildPublic, BuildUpdate, BuildWithDetails
from database.dynamic.crud import create_build, get_user_builds, get_build_by_id, update_build, delete_build
from database.dynamic.auth import decode_token

router = APIRouter(prefix="/api/builds", tags=["builds"])


async def get_current_user_id(request: Request) -> str:
    """Extract user_id from JWT token"""
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(401, "Invalid token")
        return user_id
            
    except Exception:
        raise HTTPException(status_code=401, detail="Token expired or invalid")


@router.post("/", response_model=dict, status_code=201)
async def create_build_endpoint(request: Request, build: BuildCreate):
    """Create a new build"""
    user_id = await get_current_user_id(request)
    
    try:
        new_build = await create_build(user_id, build)
        return {
            "id": str(new_build["_id"]),
            "name": new_build["name"],
            "warframe_uniqueName": new_build["warframe_uniqueName"],
            "user_id": new_build["user_id"],
            "created_at": new_build["created_at"],
            "updated_at": new_build["updated_at"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[BuildPublic])
async def get_user_builds_endpoint(request: Request, skip: int = 0, limit: int = 30, include_details: bool = False):
    """Get all builds for the current user"""
    user_id = await get_current_user_id(request)
    
    builds = await get_user_builds(user_id, skip, limit, include_details)
    return [
        {
            "id": str(build["_id"]),
            "name": build["name"],
            "warframe_uniqueName": build["warframe_uniqueName"],
            "created_at": build["created_at"],
            "updated_at": build["updated_at"],
            "warframe": build.get("warframe")
        }
        for build in builds
    ]


@router.get("/{build_id}", response_model=BuildWithDetails)
async def get_build_endpoint(request: Request, build_id: str):
    """Get a specific build by ID with full warframe details"""
    user_id = await get_current_user_id(request)
    
    build = await get_build_by_id(build_id, user_id, include_warframe_details=True)
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    
    return {
        "id": str(build["_id"]),
        "name": build["name"],
        "warframe_uniqueName": build["warframe_uniqueName"],
        "created_at": build["created_at"],
        "updated_at": build["updated_at"],
        "warframe": build["warframe"]
    }


@router.put("/{build_id}", response_model=BuildWithDetails)
async def update_build_endpoint(request: Request, build_id: str, build_update: BuildUpdate):
    """Update a specific build and return with full warframe details"""
    user_id = await get_current_user_id(request)
    
    updated_build = await update_build(build_id, user_id, build_update)
    if not updated_build:
        raise HTTPException(status_code=404, detail="Build not found")
    
    # Enrich with warframe details for the response
    from database.static.warframe_helper import get_static_db
    static_db = get_static_db()
    warframe = static_db.get_warframe_by_unique_name(updated_build["warframe_uniqueName"])
    updated_build["warframe"] = warframe
    
    return {
        "id": str(updated_build["_id"]),
        "name": updated_build["name"],
        "warframe_uniqueName": updated_build["warframe_uniqueName"],
        "created_at": updated_build["created_at"],
        "updated_at": updated_build["updated_at"],
        "warframe": warframe
    }


@router.delete("/{build_id}", status_code=204)
async def delete_build_endpoint(request: Request, build_id: str):
    """Delete a specific build"""
    user_id = await get_current_user_id(request)
    
    deleted = await delete_build(build_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Build not found")