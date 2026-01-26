from datetime import datetime

from bson import ObjectId
from models.builds import BuildCreate, BuildUpdate
from models.users import UserCreate

from database.db import (
    connect_to_mongodb,
    db_manager,
    does_value_exists,
)
from database.dynamic.security import hash_password


async def create_user(user: UserCreate):
    existing = await db_manager.users.find_one({"email": user.email})
    if existing:
        raise ValueError("Email already registered")

    doc = {
        "email": user.email,
        "username": user.username,
        "hashed_password": hash_password(user.password),
        "role": user.role.value if hasattr(user.role, "value") else user.role,
    }

    res = await db_manager.users.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc


async def get_user_by_email(email: str):
    return await db_manager.users.find_one({"email": email})


async def create_build(user_id: str, build: BuildCreate):
    # Check user's existing builds count
    build_count = await db_manager.builds.count_documents({"user_id": user_id})
    if build_count >= 30:
        raise ValueError("Maximum number of builds (30) reached")

    # Validate warframe exists
    client = connect_to_mongodb()
    if not client:
        raise ValueError("Could not connect to static database to validate warframe.")

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

    # Validate mods exist
    for mod in build.warframe_mods:
        if not does_value_exists(
            client, "cephalon_onni", "mods", "uniqueName", mod.uniqueName
        ):
            raise ValueError(f"Mod with uniqueName '{mod.uniqueName}' not found")

    # Validate arcanes exist
    for arcane_name in build.warframe_arcanes:
        if not does_value_exists(
            client, "cephalon_onni", "arcanes", "uniqueName", arcane_name
        ):
            raise ValueError(f"Arcane with uniqueName '{arcane_name}' not found")

    # Validate weapons and their mods/arcanes exist
    for weapon_field in [
        build.primary_weapon,
        build.secondary_weapon,
        build.melee_weapon,
    ]:
        if weapon_field:
            if not does_value_exists(
                client,
                "cephalon_onni",
                "weapons",
                "uniqueName",
                weapon_field.weapon_uniqueName,
            ):
                raise ValueError(
                    f"Weapon with uniqueName '{weapon_field.weapon_uniqueName}' not found"
                )

            # Validate weapon mods
            for mod in weapon_field.mods:
                if not does_value_exists(
                    client, "cephalon_onni", "mods", "uniqueName", mod.uniqueName
                ):
                    raise ValueError(
                        f"Weapon mod with uniqueName '{mod.uniqueName}' not found"
                    )

            # Validate weapon arcane
            if weapon_field.arcane_uniqueName:
                if not does_value_exists(
                    client,
                    "cephalon_onni",
                    "arcanes",
                    "uniqueName",
                    weapon_field.arcane_uniqueName,
                ):
                    raise ValueError(
                        f"Weapon arcane with uniqueName '{weapon_field.arcane_uniqueName}' not found"
                    )

    doc = {
        "name": build.name,
        "warframe_uniqueName": build.warframe_uniqueName,
        "warframe_mods": [mod.dict() for mod in build.warframe_mods],
        "warframe_arcanes": build.warframe_arcanes,
        "primary_weapon": build.primary_weapon.dict() if build.primary_weapon else None,
        "secondary_weapon": build.secondary_weapon.dict()
        if build.secondary_weapon
        else None,
        "melee_weapon": build.melee_weapon.dict() if build.melee_weapon else None,
        "user_id": user_id,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    res = await db_manager.builds.insert_one(doc)
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
    total_builds = await db_manager.builds.count_documents({})
    print(f"DEBUG: Total builds in database: {total_builds}")

    # Debug: Check builds for this specific user
    user_build_count = await db_manager.builds.count_documents({"user_id": user_id})
    print(f"DEBUG: Builds for user {user_id}: {user_build_count}")

    cursor = (
        db_manager.builds.find({"user_id": user_id})
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

        # Convert string lists and nested objects to match model structure
        if "warframe_mods" not in build_dict:
            build_dict["warframe_mods"] = []
        if "warframe_arcanes" not in build_dict:
            build_dict["warframe_arcanes"] = []
        if "primary_weapon" not in build_dict:
            build_dict["primary_weapon"] = None
        if "secondary_weapon" not in build_dict:
            build_dict["secondary_weapon"] = None
        if "melee_weapon" not in build_dict:
            build_dict["melee_weapon"] = None

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
                abilities = list(
                    abilities_collection.find(
                        {"warframe_uniqueName": build["warframe_uniqueName"]},
                        {
                            "_id": 0,
                            "abilityUniqueName": 1,
                            "abilityName": 1,
                            "description": 1,
                        },
                    )
                )
                # Transform database field names to match the model
                warframe["abilities"] = abilities
                build_dict["warframe"] = warframe
            else:
                build_dict["warframe"] = None
        builds.append(build_dict)

    print(f"DEBUG: Found {build_count} builds total in database")
    return builds


async def get_available_warframes():
    """Get all available warframes for build creation"""
    mongo_client = connect_to_mongodb()
    if not mongo_client:
        raise ValueError("Could not connect to static database")

    db = mongo_client["cephalon_onni"]
    warframes_collection = db["warframes"]

    warframes = list(
        warframes_collection.find(
            {}, {"_id": 0, "uniqueName": 1, "name": 1, "masteryReq": 1}
        )
    )
    return warframes


async def get_available_weapons():
    """Get all available weapons for build creation"""
    mongo_client = connect_to_mongodb()
    if not mongo_client:
        raise ValueError("Could not connect to static database")

    db = mongo_client["cephalon_onni"]
    weapons_collection = db["weapons"]

    weapons = list(
        weapons_collection.find(
            {},
            {
                "_id": 0,
                "uniqueName": 1,
                "name": 1,
                "masteryReq": 1,
                "productCategory": 1,
            },
        )
    )
    return weapons


async def get_available_mods():
    """Get all available mods for build creation"""
    mongo_client = connect_to_mongodb()
    if not mongo_client:
        raise ValueError("Could not connect to static database")

    db = mongo_client["cephalon_onni"]
    mods_collection = db["mods"]

    mods = list(
        mods_collection.find(
            {},
            {
                "_id": 0,
                "uniqueName": 1,
                "name": 1,
                "type": 1,
                "rarity": 1,
                "polarity": 1,
            },
        )
    )
    return mods


async def get_available_arcanes():
    """Get all available arcanes for build creation"""
    mongo_client = connect_to_mongodb()
    if not mongo_client:
        raise ValueError("Could not connect to static database")

    db = mongo_client["cephalon_onni"]
    arcanes_collection = db["arcanes"]

    arcanes = list(
        arcanes_collection.find({}, {"_id": 0, "uniqueName": 1, "name": 1, "rarity": 1})
    )
    return arcanes


async def get_build_by_id(
    build_id: str, user_id: str, include_warframe_details: bool = False
):
    try:
        build = await db_manager.builds.find_one(
            {"_id": ObjectId(build_id), "user_id": user_id}
        )

        if not build:
            return None

        # Convert string lists and nested objects to match model structure
        if "warframe_mods" not in build:
            build["warframe_mods"] = []
        if "warframe_arcanes" not in build:
            build["warframe_arcanes"] = []
        if "primary_weapon" not in build:
            build["primary_weapon"] = None
        if "secondary_weapon" not in build:
            build["secondary_weapon"] = None
        if "melee_weapon" not in build:
            build["melee_weapon"] = None

        if include_warframe_details:
            mongo_client = connect_to_mongodb()
            if not mongo_client:
                raise ValueError(
                    "Could not connect to static database to validate warframe."
                )

            db = mongo_client["cephalon_onni"]

            # Get warframe details
            warframes_collection = db["warframes"]
            abilities_collection = db["warframe_abilities"]
            warframe = warframes_collection.find_one(
                {"uniqueName": build["warframe_uniqueName"]}
            )
            if warframe and warframe.get("name"):
                abilities = list(
                    abilities_collection.find(
                        {"warframe_uniqueName": build["warframe_uniqueName"]},
                        {
                            "_id": 0,
                            "abilityUniqueName": 1,
                            "abilityName": 1,
                            "description": 1,
                        },
                    )
                )
                warframe["abilities"] = abilities
                build["warframe"] = warframe
            else:
                build["warframe"] = None

            # Get weapon details
            weapons_collection = db["weapons"]
            if build["primary_weapon"]:
                build["primary_weapon_details"] = weapons_collection.find_one(
                    {"uniqueName": build["primary_weapon"]["weapon_uniqueName"]}
                )
                if build["primary_weapon"]["arcane_uniqueName"]:
                    arcanes_collection = db["arcanes"]
                    build["primary_arcane_details"] = arcanes_collection.find_one(
                        {"uniqueName": build["primary_weapon"]["arcane_uniqueName"]}
                    )

            if build["secondary_weapon"]:
                build["secondary_weapon_details"] = weapons_collection.find_one(
                    {"uniqueName": build["secondary_weapon"]["weapon_uniqueName"]}
                )
                if build["secondary_weapon"]["arcane_uniqueName"]:
                    arcanes_collection = db["arcanes"]
                    build["secondary_arcane_details"] = arcanes_collection.find_one(
                        {"uniqueName": build["secondary_weapon"]["arcane_uniqueName"]}
                    )

            if build["melee_weapon"]:
                build["melee_weapon_details"] = weapons_collection.find_one(
                    {"uniqueName": build["melee_weapon"]["weapon_uniqueName"]}
                )
                if build["melee_weapon"]["arcane_uniqueName"]:
                    arcanes_collection = db["arcanes"]
                    build["melee_arcane_details"] = arcanes_collection.find_one(
                        {"uniqueName": build["melee_weapon"]["arcane_uniqueName"]}
                    )

            # Get arcane details
            arcanes_collection = db["arcanes"]
            build["warframe_arcanes_details"] = []
            for arcane_name in build.get("warframe_arcanes", []):
                arcane = arcanes_collection.find_one({"uniqueName": arcane_name})
                if arcane:
                    build["warframe_arcanes_details"].append(arcane)

        return build
    except:
        return None


async def update_build(build_id: str, user_id: str, build_update: BuildUpdate):
    update_data = {}
    client = connect_to_mongodb()

    if build_update.name is not None:
        update_data["name"] = build_update.name

    if build_update.warframe_uniqueName is not None:
        if not client:
            raise ValueError(
                "Could not connect to static database to validate warframe."
            )

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
        update_data["warframe_uniqueName"] = build_update.warframe_uniqueName

    if build_update.warframe_mods is not None:
        if not client:
            raise ValueError("Could not connect to static database to validate mods.")

        for mod in build_update.warframe_mods:
            if not does_value_exists(
                client, "cephalon_onni", "mods", "uniqueName", mod.uniqueName
            ):
                raise ValueError(f"Mod with uniqueName '{mod.uniqueName}' not found")
        update_data["warframe_mods"] = [
            mod.dict() for mod in build_update.warframe_mods
        ]

    if build_update.warframe_arcanes is not None:
        if not client:
            raise ValueError(
                "Could not connect to static database to validate arcanes."
            )

        for arcane_name in build_update.warframe_arcanes:
            if not does_value_exists(
                client, "cephalon_onni", "arcanes", "uniqueName", arcane_name
            ):
                raise ValueError(f"Arcane with uniqueName '{arcane_name}' not found")
        update_data["warframe_arcanes"] = build_update.warframe_arcanes

    # Validate weapons
    for weapon_field, weapon_key in [
        (build_update.primary_weapon, "primary_weapon"),
        (build_update.secondary_weapon, "secondary_weapon"),
        (build_update.melee_weapon, "melee_weapon"),
    ]:
        if weapon_field is not None:
            if weapon_field is None:
                update_data[weapon_key] = None
            else:
                if not client:
                    raise ValueError(
                        "Could not connect to static database to validate weapons."
                    )

                if not does_value_exists(
                    client,
                    "cephalon_onni",
                    "weapons",
                    "uniqueName",
                    weapon_field.weapon_uniqueName,
                ):
                    raise ValueError(
                        f"Weapon with uniqueName '{weapon_field.weapon_uniqueName}' not found"
                    )

                for mod in weapon_field.mods:
                    if not does_value_exists(
                        client, "cephalon_onni", "mods", "uniqueName", mod.uniqueName
                    ):
                        raise ValueError(
                            f"Weapon mod with uniqueName '{mod.uniqueName}' not found"
                        )

                if weapon_field.arcane_uniqueName and not does_value_exists(
                    client,
                    "cephalon_onni",
                    "arcanes",
                    "uniqueName",
                    weapon_field.arcane_uniqueName,
                ):
                    raise ValueError(
                        f"Weapon arcane with uniqueName '{weapon_field.arcane_uniqueName}' not found"
                    )

                update_data[weapon_key] = weapon_field.dict()

    if update_data:
        update_data["updated_at"] = datetime.now()
        await db_manager.builds.update_one(
            {"_id": ObjectId(build_id), "user_id": user_id}, {"$set": update_data}
        )

    return await get_build_by_id(build_id, user_id)


async def delete_build(build_id: str, user_id: str):
    try:
        result = await db_manager.builds.delete_one(
            {"_id": ObjectId(build_id), "user_id": user_id}
        )
        return result.deleted_count > 0
    except:
        return False
