from datetime import datetime

from bson import ObjectId
from models.builds import BuildCreate, BuildUpdate
from models.users import UserCreate

from database.dynamic.db import builds_collection, users_collection
from database.dynamic.security import hash_password
from database.static.db_helpers import connect_to_mongodb, does_value_exists


async def create_user(user: UserCreate):
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise ValueError("Email already registered")

    doc = {
        "email": user.email,
        "username": user.username,
        "hashed_password": hash_password(user.password),
        "role": user.role.value if hasattr(user.role, "value") else user.role,
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
    client = connect_to_mongodb()
    if not client:
        raise ValueError("Could not connect to static database to validate warframe.")
    try:
        if not does_value_exists(
            client,
            "cephalon_onni",
            "warframes",
            "uniqueName",
            build.warframe_uniqueName,
        ):
            raise ValueError(
                f"Warframe with uniqueName '{build.warframe_uniqueName}' not found"
            )
    finally:
        if client:
            client.close()

    doc = {
        "name": build.name,
        "warframe_uniqueName": build.warframe_uniqueName,
        "user_id": user_id,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    res = await builds_collection.insert_one(doc)
    doc["_id"] = res.inserted_id
    print(f"DEBUG: Inserted build with user_id: {user_id}, _id: {res.inserted_id}")
    return doc


async def get_user_builds(
    user_id: str,
    skip: int = 0,
    limit: int = 30,
    include_warframe_details: bool = False,
):
    print(f"DEBUG: Querying builds for user_id: {user_id}")

    # Debug: Check all builds in database
    total_builds = await builds_collection.count_documents({})
    print(f"DEBUG: Total builds in database: {total_builds}")

    # Debug: Check builds for this specific user
    user_build_count = await builds_collection.count_documents({"user_id": user_id})
    print(f"DEBUG: Builds for user {user_id}: {user_build_count}")

    cursor = (
        builds_collection.find({"user_id": user_id})
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )
    builds = []
    mongo_client = connect_to_mongodb() if include_warframe_details else None

    build_count = 0
    async for build in cursor:
        build_count += 1
        build_dict = dict(build)
        if include_warframe_details and mongo_client:
            db = mongo_client["cephalon_onni"]
            warframes_collection = db["warframes"]
            abilities_collection = db["warframe_abilities"]
            warframe = warframes_collection.find_one(
                {"uniqueName": build["warframe_uniqueName"]}
            )
            # Only include warframe if found and valid, with field name mapping
            if warframe and warframe.get("name"):
                # Fetch abilities for this warframe
                abilities = list(abilities_collection.find(
                    {"warframe_uniqueName": build["warframe_uniqueName"]},
                    {"_id": 0, "abilityUniqueName": 1, "abilityName": 1, "description": 1}
                ))
                # Transform database field names to match the model
                warframe["abilities"] = abilities
                build_dict["warframe"] = warframe
            else:
                build_dict["warframe"] = None
        builds.append(build_dict)

    if mongo_client:
        mongo_client.close()

    print(f"DEBUG: Found {build_count} builds total in database")
    return builds


async def get_build_by_id(
    build_id: str, user_id: str, include_warframe_details: bool = False
):
    try:
        build = await builds_collection.find_one(
            {"_id": ObjectId(build_id), "user_id": user_id}
        )
        if build and include_warframe_details:
            mongo_client = connect_to_mongodb()
            if not mongo_client:
                raise ValueError(
                    "Could not connect to static database to validate warframe."
                )
            try:
                db = mongo_client["cephalon_onni"]
                warframes_collection = db["warframes"]
                abilities_collection = db["warframe_abilities"]
                warframe = warframes_collection.find_one(
                    {"uniqueName": build["warframe_uniqueName"]}
                )
                # Only include warframe if found and valid, with field name mapping
                if warframe and warframe.get("name"):
                    # Fetch abilities for this warframe
                    abilities = list(abilities_collection.find(
                        {"warframe_uniqueName": build["warframe_uniqueName"]},
                        {"_id": 0, "abilityUniqueName": 1, "abilityName": 1, "description": 1}
                    ))
                    # Transform database field names to match the model
                    warframe["abilities"] = abilities
                    build["warframe"] = warframe
                else:
                    build["warframe"] = None
            finally:
                if mongo_client:
                    mongo_client.close()
        return build
    except:
        return None


async def update_build(build_id: str, user_id: str, build_update: BuildUpdate):
    update_data = {}
    if build_update.name is not None:
        update_data["name"] = build_update.name
    if build_update.warframe_uniqueName is not None:
        # Validate warframe exists
        client = connect_to_mongodb()
        if not client:
            raise ValueError(
                "Could not connect to static database to validate warframe."
            )
        try:
            if not does_value_exists(
                client,
                "cephalon_onni",
                "warframes",
                "uniqueName",
                build_update.warframe_uniqueName,
            ):
                raise ValueError(
                    f"Warframe with uniqueName '{build_update.warframe_uniqueName}' not found"
                )
        finally:
            if client:
                client.close()
        update_data["warframe_uniqueName"] = build_update.warframe_uniqueName

    if update_data:
        update_data["updated_at"] = datetime.now()
        await builds_collection.update_one(
            {"_id": ObjectId(build_id), "user_id": user_id}, {"$set": update_data}
        )

    return await get_build_by_id(build_id, user_id)


async def delete_build(build_id: str, user_id: str):
    try:
        result = await builds_collection.delete_one(
            {"_id": ObjectId(build_id), "user_id": user_id}
        )
        return result.deleted_count > 0
    except:
        return False
