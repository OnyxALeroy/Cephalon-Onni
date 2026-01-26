from typing import List

from database.dynamic.auth import decode_token
from database.dynamic.crud import (
    create_build,
    delete_build,
    get_build_by_id,
    get_user_builds,
    update_build,
    get_available_warframes,
    get_available_weapons,
    get_available_mods,
    get_available_arcanes,
)
from fastapi import APIRouter, HTTPException, Request
from models.builds import BuildCreate, BuildPublic, BuildUpdate, BuildWithDetails

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

    # Log the build data for debugging
    print(
        f"Creating build - User: {user_id}, Name: '{build.name}', Warframe: '{build.warframe_uniqueName}'"
    )

    try:
        new_build = await create_build(user_id, build)
        print(
            f"DEBUG: Build created with _id: {new_build.get('_id')}, user_id: {new_build.get('user_id')}"
        )

        return {
            "id": str(new_build["_id"]),
            "name": new_build["name"],
            "warframe_uniqueName": new_build["warframe_uniqueName"],
            "warframe_mods": new_build.get("warframe_mods", []),
            "warframe_arcanes": new_build.get("warframe_arcanes", []),
            "primary_weapon": new_build.get("primary_weapon"),
            "secondary_weapon": new_build.get("secondary_weapon"),
            "melee_weapon": new_build.get("melee_weapon"),
            "user_id": new_build["user_id"],
            "created_at": new_build["created_at"].isoformat()
            if new_build["created_at"]
            else None,
            "updated_at": new_build["updated_at"].isoformat()
            if new_build["updated_at"]
            else None,
        }
    except ValueError as e:
        print(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=List[BuildPublic])
@router.get("", response_model=List[BuildPublic])
async def get_user_builds_endpoint(
    request: Request, skip: int = 0, limit: int = 30, include_details: bool = False
):
    """Get all builds for the current user"""
    user_id = await get_current_user_id(request)
    print(f"DEBUG: Getting builds for user_id: {user_id}")

    builds = await get_user_builds(user_id, skip, limit, include_details)
    print(f"DEBUG: Found {len(builds)} builds for user {user_id}")

    # Build response and debug it
    response_data = [
        {
            "id": str(build["_id"]),
            "name": build["name"],
            "warframe_uniqueName": build["warframe_uniqueName"],
            "warframe_mods": build.get("warframe_mods", []),
            "warframe_arcanes": build.get("warframe_arcanes", []),
            "primary_weapon": build.get("primary_weapon"),
            "secondary_weapon": build.get("secondary_weapon"),
            "melee_weapon": build.get("melee_weapon"),
            "created_at": build["created_at"].isoformat()
            if build["created_at"]
            else None,
            "updated_at": build["updated_at"].isoformat()
            if build["updated_at"]
            else None,
            "warframe": build.get("warframe"),
        }
        for build in builds
    ]

    print(f"DEBUG: Response data: {response_data}")
    return response_data


@router.get("/{build_id}", response_model=BuildWithDetails)
async def get_build_endpoint(request: Request, build_id: str):
    """Get a specific build by ID with full warframe details"""
    user_id = await get_current_user_id(request)

    build = await get_build_by_id(build_id, user_id, include_warframe_details=True)
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")

    # Return dictionary - FastAPI will validate against response_model
    return {
        "id": str(build["_id"]),
        "name": build["name"],
        "warframe_uniqueName": build["warframe_uniqueName"],
        "warframe_mods": build.get("warframe_mods", []),
        "warframe_arcanes": build.get("warframe_arcanes", []),
        "primary_weapon": build.get("primary_weapon"),
        "secondary_weapon": build.get("secondary_weapon"),
        "melee_weapon": build.get("melee_weapon"),
        "created_at": build["created_at"].isoformat() if build["created_at"] else None,
        "updated_at": build["updated_at"].isoformat() if build["updated_at"] else None,
        "warframe": build["warframe"],
    }


@router.put("/{build_id}", response_model=BuildWithDetails)
async def update_build_endpoint(
    request: Request, build_id: str, build_update: BuildUpdate
):
    """Update a specific build and return with full warframe details"""
    user_id = await get_current_user_id(request)

    updated_build = await update_build(build_id, user_id, build_update)
    if not updated_build:
        raise HTTPException(status_code=404, detail="Build not found")

    # Enrich with warframe details for the response
    from database.db import connect_to_mongodb

    warframe = None
    mongo_client = connect_to_mongodb()
    if mongo_client:
        db = mongo_client["cephalon_onni"]
        warframes_collection = db["warframes"]
        abilities_collection = db["warframe_abilities"]
        warframe = warframes_collection.find_one(
            {"uniqueName": updated_build["warframe_uniqueName"]}
        )
        if warframe and warframe.get("name"):
            # Fetch abilities for this warframe
            abilities = list(
                abilities_collection.find(
                    {"warframe_uniqueName": updated_build["warframe_uniqueName"]},
                    {
                        "_id": 0,
                        "abilityUniqueName": 1,
                        "abilityName": 1,
                        "description": 1,
                    },
                )
            )
            warframe["abilities"] = abilities
            updated_build["warframe"] = warframe
        else:
            updated_build["warframe"] = None
    else:
        updated_build["warframe"] = None

    # Return dictionary - FastAPI will validate against response_model
    return {
        "id": str(updated_build["_id"]),
        "name": updated_build["name"],
        "warframe_uniqueName": updated_build["warframe_uniqueName"],
        "warframe_mods": updated_build.get("warframe_mods", []),
        "warframe_arcanes": updated_build.get("warframe_arcanes", []),
        "primary_weapon": updated_build.get("primary_weapon"),
        "secondary_weapon": updated_build.get("secondary_weapon"),
        "melee_weapon": updated_build.get("melee_weapon"),
        "created_at": updated_build["created_at"].isoformat()
        if updated_build["created_at"]
        else None,
        "updated_at": updated_build["updated_at"].isoformat()
        if updated_build["updated_at"]
        else None,
        "warframe": updated_build.get("warframe"),
    }


@router.delete("/{build_id}", status_code=204)
async def delete_build_endpoint(request: Request, build_id: str):
    """Delete a specific build"""
    user_id = await get_current_user_id(request)

    deleted = await delete_build(build_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Build not found")


@router.get("/available/warframes")
async def get_available_warframes_endpoint():
    """Get all available warframes for build creation"""
    try:
        warframes = await get_available_warframes()
        return warframes
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/available/weapons")
async def get_available_weapons_endpoint():
    """Get all available weapons for build creation"""
    try:
        weapons = await get_available_weapons()
        return weapons
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/available/mods")
async def get_available_mods_endpoint():
    """Get all available mods for build creation"""
    try:
        mods = await get_available_mods()
        return mods
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/available/arcanes")
async def get_available_arcanes_endpoint():
    """Get all available arcanes for build creation"""
    try:
        arcanes = await get_available_arcanes()
        return arcanes
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
