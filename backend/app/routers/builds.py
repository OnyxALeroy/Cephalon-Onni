from typing import List

from dependencies import get_current_user_id
from fastapi import APIRouter, HTTPException, Request
from models.builds import BuildCreate, BuildPublic, BuildUpdate, BuildWithDetails
from services.build_service import BuildService

router = APIRouter(prefix="/api/builds", tags=["builds"])


@router.post("/", response_model=dict, status_code=201)
async def create_build_endpoint(request: Request, build: BuildCreate):
    user_id = get_current_user_id(request)

    try:
        new_build = await BuildService.create_build(user_id, build)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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


@router.get("/", response_model=List[BuildPublic])
@router.get("", response_model=List[BuildPublic])
async def get_user_builds_endpoint(
    request: Request, skip: int = 0, limit: int = 30, include_details: bool = False
):
    user_id = get_current_user_id(request)
    builds = await BuildService.get_user_builds(user_id, skip, limit, include_details)

    return [
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


@router.get("/{build_id}", response_model=BuildWithDetails)
async def get_build_endpoint(request: Request, build_id: str):
    user_id = get_current_user_id(request)

    build = await BuildService.get_build_by_id(build_id, user_id, include_details=True)
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")

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
    user_id = get_current_user_id(request)

    try:
        updated_build = await BuildService.update_build(build_id, user_id, build_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not updated_build:
        raise HTTPException(status_code=404, detail="Build not found")

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
    user_id = get_current_user_id(request)

    deleted = await BuildService.delete_build(build_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Build not found")


@router.get("/available/warframes")
async def get_available_warframes_endpoint():
    try:
        return await BuildService.get_available_warframes()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/available/weapons")
async def get_available_weapons_endpoint():
    try:
        return await BuildService.get_available_weapons()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/available/mods")
async def get_available_mods_endpoint():
    try:
        return await BuildService.get_available_mods()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/available/arcanes")
async def get_available_arcanes_endpoint():
    try:
        return await BuildService.get_available_arcanes()
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
