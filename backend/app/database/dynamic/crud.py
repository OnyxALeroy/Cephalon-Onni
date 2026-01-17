from bson import ObjectId
from datetime import datetime
from database.dynamic.db import users_collection, builds_collection
from models.users import UserCreate
from models.builds import BuildCreate, BuildUpdate
from database.dynamic.security import hash_password
from database.static.warframe_helper import get_static_db


async def create_user(user: UserCreate):
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise ValueError("Email already registered")

    doc = {
        "email": user.email,
        "username": user.username,
        "hashed_password": hash_password(user.password),
        "role": user.role.value if hasattr(user.role, 'value') else user.role
    }

    res = await users_collection.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc


async def get_user_by_email(email: str):
    return await users_collection.find_one({"email": email})


async def create_build(user_id: str, build: BuildCreate):
    # Check user's existing builds count
    build_count = await builds_collection.count_documents({"user_id": user_id})
    if build_count >= 30:
        raise ValueError("Maximum number of builds (30) reached")
    
    # Validate warframe exists
    static_db = get_static_db()
    if not static_db.warframe_exists(build.warframe_uniqueName):
        raise ValueError(f"Warframe with uniqueName '{build.warframe_uniqueName}' not found")
    
    doc = {
        "name": build.name,
        "warframe_uniqueName": build.warframe_uniqueName,
        "user_id": user_id,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    res = await builds_collection.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc


async def get_user_builds(user_id: str, skip: int = 0, limit: int = 30, include_warframe_details: bool = False):
    cursor = builds_collection.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
    builds = []
    static_db = get_static_db() if include_warframe_details else None
    
    async for build in cursor:
        build_dict = dict(build)
        if include_warframe_details and static_db:
            warframe = static_db.get_warframe_by_unique_name(build["warframe_uniqueName"])
            build_dict["warframe"] = warframe
        builds.append(build_dict)
    return builds


async def get_build_by_id(build_id: str, user_id: str, include_warframe_details: bool = False):
    try:
        build = await builds_collection.find_one({"_id": ObjectId(build_id), "user_id": user_id})
        if build and include_warframe_details:
            static_db = get_static_db()
            warframe = static_db.get_warframe_by_unique_name(build["warframe_uniqueName"])
            build["warframe"] = warframe
        return build
    except:
        return None


async def update_build(build_id: str, user_id: str, build_update: BuildUpdate):
    update_data = {}
    if build_update.name is not None:
        update_data["name"] = build_update.name
    if build_update.warframe_uniqueName is not None:
        # Validate warframe exists
        static_db = get_static_db()
        if not static_db.warframe_exists(build_update.warframe_uniqueName):
            raise ValueError(f"Warframe with uniqueName '{build_update.warframe_uniqueName}' not found")
        update_data["warframe_uniqueName"] = build_update.warframe_uniqueName
    
    if update_data:
        update_data["updated_at"] = datetime.now()
        await builds_collection.update_one(
            {"_id": ObjectId(build_id), "user_id": user_id},
            {"$set": update_data}
        )
    
    return await get_build_by_id(build_id, user_id)


async def delete_build(build_id: str, user_id: str):
    try:
        result = await builds_collection.delete_one({"_id": ObjectId(build_id), "user_id": user_id})
        return result.deleted_count > 0
    except:
        return False
