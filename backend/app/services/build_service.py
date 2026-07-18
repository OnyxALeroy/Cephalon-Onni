from datetime import datetime
from typing import List, Optional

from models.builds import BuildCreate, BuildUpdate
from repositories.build_repository import BuildRepository
from repositories.mongo_warframe_repository import WarframeRepository
from repositories.mongo_weapon_repository import WeaponRepository
from repositories.mongo_mod_repository import ModRepository, ArcaneRepository


class BuildService:
    @staticmethod
    async def _validate_build(build: BuildCreate):
        """Validate that all referenced entities exist."""
        if not await WarframeRepository.exists(build.warframe_uniqueName):
            raise ValueError(
                f"Warframe with uniqueName '{build.warframe_uniqueName}' not found"
            )

        for mod in build.warframe_mods:
            if not await ModRepository.exists(mod.uniqueName):
                raise ValueError(f"Mod with uniqueName '{mod.uniqueName}' not found")

        for arcane_name in build.warframe_arcanes:
            if not await ArcaneRepository.exists(arcane_name):
                raise ValueError(f"Arcane with uniqueName '{arcane_name}' not found")

        for weapon_field in [build.primary_weapon, build.secondary_weapon, build.melee_weapon]:
            if weapon_field:
                if not await WeaponRepository.exists(weapon_field.weapon_uniqueName):
                    raise ValueError(
                        f"Weapon with uniqueName '{weapon_field.weapon_uniqueName}' not found"
                    )
                for mod in weapon_field.mods:
                    if not await ModRepository.exists(mod.uniqueName):
                        raise ValueError(
                            f"Weapon mod with uniqueName '{mod.uniqueName}' not found"
                        )
                if weapon_field.arcane_uniqueName:
                    if not await ArcaneRepository.exists(weapon_field.arcane_uniqueName):
                        raise ValueError(
                            f"Weapon arcane with uniqueName '{weapon_field.arcane_uniqueName}' not found"
                        )

    @staticmethod
    async def _validate_build_update(build_update: BuildUpdate):
        """Validate entities referenced in an update."""
        client = None

        if build_update.warframe_uniqueName is not None:
            if not await WarframeRepository.exists(build_update.warframe_uniqueName):
                raise ValueError(
                    f"Warframe with uniqueName '{build_update.warframe_uniqueName}' not found"
                )

        if build_update.warframe_mods is not None:
            for mod in build_update.warframe_mods:
                if not await ModRepository.exists(mod.uniqueName):
                    raise ValueError(f"Mod with uniqueName '{mod.uniqueName}' not found")

        if build_update.warframe_arcanes is not None:
            for arcane_name in build_update.warframe_arcanes:
                if not await ArcaneRepository.exists(arcane_name):
                    raise ValueError(f"Arcane with uniqueName '{arcane_name}' not found")

        for weapon_field, weapon_key in [
            (build_update.primary_weapon, "primary_weapon"),
            (build_update.secondary_weapon, "secondary_weapon"),
            (build_update.melee_weapon, "melee_weapon"),
        ]:
            if weapon_field is not None:
                if not weapon_field.weapon_uniqueName or weapon_field.weapon_uniqueName.strip() == "":
                    pass  # will be set to None
                else:
                    if not await WeaponRepository.exists(weapon_field.weapon_uniqueName):
                        raise ValueError(
                            f"Weapon with uniqueName '{weapon_field.weapon_uniqueName}' not found"
                        )
                    for mod in weapon_field.mods:
                        if not await ModRepository.exists(mod.uniqueName):
                            raise ValueError(
                                f"Weapon mod with uniqueName '{mod.uniqueName}' not found"
                            )
                    if weapon_field.arcane_uniqueName:
                        if not await ArcaneRepository.exists(weapon_field.arcane_uniqueName):
                            raise ValueError(
                                f"Weapon arcane with uniqueName '{weapon_field.arcane_uniqueName}' not found"
                            )

    @staticmethod
    def _enrich_build(build: dict) -> dict:
        """Enrich a build with warframe and ability details from static MongoDB."""
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

        # Warframe details
        warframe = WarframeRepository.find_by_unique_name_sync(build["warframe_uniqueName"])
        if warframe and warframe.get("name"):
            abilities = WarframeRepository.find_abilities_sync(build["warframe_uniqueName"])
            warframe["abilities"] = abilities
            build["warframe"] = warframe
        else:
            build["warframe"] = None

        return build

    @staticmethod
    def _enrich_build_full(build: dict) -> dict:
        """Full enrichment including weapon and arcane details."""
        build = BuildService._enrich_build(build)

        weapons_collection = None
        arcanes_collection = None

        from database.db import connect_to_mongodb
        client = connect_to_mongodb()
        if client:
            db = client["cephalon_onni"]
            weapons_collection = db["weapons"]
            arcanes_collection = db["arcanes"]

        if weapons_collection:
            if build.get("primary_weapon"):
                build["primary_weapon_details"] = weapons_collection.find_one(
                    {"uniqueName": build["primary_weapon"]["weapon_uniqueName"]}
                )
                if build["primary_weapon"].get("arcane_uniqueName"):
                    build["primary_arcane_details"] = arcanes_collection.find_one(
                        {"uniqueName": build["primary_weapon"]["arcane_uniqueName"]}
                    )

            if build.get("secondary_weapon"):
                build["secondary_weapon_details"] = weapons_collection.find_one(
                    {"uniqueName": build["secondary_weapon"]["weapon_uniqueName"]}
                )
                if build["secondary_weapon"].get("arcane_uniqueName"):
                    build["secondary_arcane_details"] = arcanes_collection.find_one(
                        {"uniqueName": build["secondary_weapon"]["arcane_uniqueName"]}
                    )

            if build.get("melee_weapon"):
                build["melee_weapon_details"] = weapons_collection.find_one(
                    {"uniqueName": build["melee_weapon"]["weapon_uniqueName"]}
                )
                if build["melee_weapon"].get("arcane_uniqueName"):
                    build["melee_arcane_details"] = arcanes_collection.find_one(
                        {"uniqueName": build["melee_weapon"]["arcane_uniqueName"]}
                    )

        if arcanes_collection:
            build["warframe_arcanes_details"] = []
            for arcane_name in build.get("warframe_arcanes", []):
                arcane = arcanes_collection.find_one({"uniqueName": arcane_name})
                if arcane:
                    build["warframe_arcanes_details"].append(arcane)

        return build

    @staticmethod
    async def create_build(user_id: str, build: BuildCreate) -> dict:
        build_count = await BuildRepository.count_by_user(user_id)
        if build_count >= 30:
            raise ValueError("Maximum number of builds (30) reached")

        await BuildService._validate_build(build)

        doc = {
            "name": build.name,
            "warframe_uniqueName": build.warframe_uniqueName,
            "warframe_mods": [mod.dict() for mod in build.warframe_mods],
            "warframe_arcanes": build.warframe_arcanes,
            "primary_weapon": build.primary_weapon.dict() if build.primary_weapon else None,
            "secondary_weapon": build.secondary_weapon.dict() if build.secondary_weapon else None,
            "melee_weapon": build.melee_weapon.dict() if build.melee_weapon else None,
            "user_id": user_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        return await BuildRepository.create(doc)

    @staticmethod
    async def get_user_builds(
        user_id: str, skip: int = 0, limit: int = 30, include_details: bool = False
    ) -> List[dict]:
        builds = await BuildRepository.find_by_user(user_id, skip, limit)
        if include_details:
            builds = [BuildService._enrich_build(build) for build in builds]
        return builds

    @staticmethod
    async def get_build_by_id(
        build_id: str, user_id: str, include_details: bool = False
    ) -> Optional[dict]:
        build = await BuildRepository.find_by_id(build_id, user_id)
        if not build:
            return None

        if include_details:
            build = BuildService._enrich_build_full(build)
        else:
            build = BuildService._enrich_build(build)

        return build

    @staticmethod
    async def update_build(
        build_id: str, user_id: str, build_update: BuildUpdate
    ) -> Optional[dict]:
        update_data = {}

        if build_update.name is not None:
            update_data["name"] = build_update.name

        if build_update.warframe_uniqueName is not None:
            update_data["warframe_uniqueName"] = build_update.warframe_uniqueName

        if build_update.warframe_mods is not None:
            update_data["warframe_mods"] = [mod.dict() for mod in build_update.warframe_mods]

        if build_update.warframe_arcanes is not None:
            update_data["warframe_arcanes"] = build_update.warframe_arcanes

        for weapon_field, weapon_key in [
            (build_update.primary_weapon, "primary_weapon"),
            (build_update.secondary_weapon, "secondary_weapon"),
            (build_update.melee_weapon, "melee_weapon"),
        ]:
            if weapon_field is not None:
                if not weapon_field.weapon_uniqueName or weapon_field.weapon_uniqueName.strip() == "":
                    update_data[weapon_key] = None
                else:
                    update_data[weapon_key] = weapon_field.dict()

        if build_update.warframe_uniqueName or build_update.warframe_mods or build_update.warframe_arcanes:
            await BuildService._validate_build_update(build_update)

        for weapon_field in [build_update.primary_weapon, build_update.secondary_weapon, build_update.melee_weapon]:
            if weapon_field and weapon_field.weapon_uniqueName and weapon_field.weapon_uniqueName.strip():
                await BuildService._validate_build_update(build_update)
                break

        if update_data:
            await BuildRepository.update(build_id, user_id, update_data)

        return await BuildService.get_build_by_id(build_id, user_id, include_details=True)

    @staticmethod
    async def delete_build(build_id: str, user_id: str) -> bool:
        return await BuildRepository.delete(build_id, user_id)

    @staticmethod
    def get_available_warframes() -> list:
        return WarframeRepository.find_all_basic()

    @staticmethod
    def get_available_weapons() -> list:
        return WeaponRepository.find_all_basic()

    @staticmethod
    def get_available_mods() -> list:
        return ModRepository.find_all_basic()

    @staticmethod
    def get_available_arcanes() -> list:
        return ArcaneRepository.find_all_basic()
