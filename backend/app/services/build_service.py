from datetime import datetime
from typing import List, Optional

from models.builds import BuildCreate, BuildUpdate
from repositories.build_repository import BuildRepository
from repositories.warframe_pg_repository import WarframePGRepository
from repositories.weapon_pg_repository import WeaponPGRepository
from repositories.mod_pg_repository import ModPGRepository
from repositories.arcane_pg_repository import ArcanePGRepository
from database.postgres_db import postgres_db


def _warframe_to_dict(warframe) -> dict:
    return {
        "uniqueName": warframe.unique_name,
        "name": warframe.name,
        "parentName": warframe.parent_name,
        "description": warframe.description,
        "health": warframe.health,
        "shield": warframe.shield,
        "armor": warframe.armor,
        "stamina": warframe.stamina,
        "power": warframe.power,
        "codexSecret": warframe.codex_secret,
        "masteryReq": warframe.mastery_req,
        "sprintSpeed": warframe.sprint_speed,
        "passiveDescription": warframe.passive_description,
        "exalted": warframe.exalted,
        "abilities": warframe.abilities,
        "productCategory": warframe.product_category,
    }


def _weapon_to_dict(weapon) -> dict:
    return {
        "uniqueName": weapon.unique_name,
        "name": weapon.name,
        "codexSecret": weapon.codex_secret,
        "criticalChance": weapon.critical_chance,
        "criticalMultiplier": weapon.critical_multiplier,
        "damagePerShot": weapon.damage_per_shot,
        "description": weapon.description,
        "fireRate": weapon.fire_rate,
        "masteryReq": weapon.mastery_req,
        "omegaAttenuation": weapon.omega_attenuation,
        "procChance": weapon.proc_chance,
        "productCategory": weapon.product_category,
        "totalDamage": weapon.total_damage,
    }


def _arcane_to_dict(arcane) -> dict:
    return {
        "uniqueName": arcane.unique_name,
        "name": arcane.name,
        "codexSecret": arcane.codex_secret,
        "rarity": arcane.rarity,
        "levelStats": arcane.level_stats,
    }


class BuildService:
    @staticmethod
    async def _validate_build(build: BuildCreate):
        """Validate that all referenced entities exist."""
        async with postgres_db._session_factory() as session:
            if not await WarframePGRepository.exists(session, build.warframe_uniqueName):
                raise ValueError(
                    f"Warframe with uniqueName '{build.warframe_uniqueName}' not found"
                )

            for mod in build.warframe_mods:
                if not await ModPGRepository.exists(session, mod.uniqueName):
                    raise ValueError(f"Mod with uniqueName '{mod.uniqueName}' not found")

            for arcane_name in build.warframe_arcanes:
                if not await ArcanePGRepository.exists(session, arcane_name):
                    raise ValueError(f"Arcane with uniqueName '{arcane_name}' not found")

            for weapon_field in [build.primary_weapon, build.secondary_weapon, build.melee_weapon]:
                if weapon_field:
                    if not await WeaponPGRepository.exists(session, weapon_field.weapon_uniqueName):
                        raise ValueError(
                            f"Weapon with uniqueName '{weapon_field.weapon_uniqueName}' not found"
                        )
                    for mod in weapon_field.mods:
                        if not await ModPGRepository.exists(session, mod.uniqueName):
                            raise ValueError(
                                f"Weapon mod with uniqueName '{mod.uniqueName}' not found"
                            )
                    if weapon_field.arcane_uniqueName:
                        if not await ArcanePGRepository.exists(session, weapon_field.arcane_uniqueName):
                            raise ValueError(
                                f"Weapon arcane with uniqueName '{weapon_field.arcane_uniqueName}' not found"
                            )

    @staticmethod
    async def _validate_build_update(build_update: BuildUpdate):
        """Validate entities referenced in an update."""
        async with postgres_db._session_factory() as session:
            if build_update.warframe_uniqueName is not None:
                if not await WarframePGRepository.exists(session, build_update.warframe_uniqueName):
                    raise ValueError(
                        f"Warframe with uniqueName '{build_update.warframe_uniqueName}' not found"
                    )

            if build_update.warframe_mods is not None:
                for mod in build_update.warframe_mods:
                    if not await ModPGRepository.exists(session, mod.uniqueName):
                        raise ValueError(f"Mod with uniqueName '{mod.uniqueName}' not found")

            if build_update.warframe_arcanes is not None:
                for arcane_name in build_update.warframe_arcanes:
                    if not await ArcanePGRepository.exists(session, arcane_name):
                        raise ValueError(f"Arcane with uniqueName '{arcane_name}' not found")

            for weapon_field, weapon_key in [
                (build_update.primary_weapon, "primary_weapon"),
                (build_update.secondary_weapon, "secondary_weapon"),
                (build_update.melee_weapon, "melee_weapon"),
            ]:
                if weapon_field is not None:
                    if not weapon_field.weapon_uniqueName or weapon_field.weapon_uniqueName.strip() == "":
                        pass
                    else:
                        if not await WeaponPGRepository.exists(session, weapon_field.weapon_uniqueName):
                            raise ValueError(
                                f"Weapon with uniqueName '{weapon_field.weapon_uniqueName}' not found"
                            )
                        for mod in weapon_field.mods:
                            if not await ModPGRepository.exists(session, mod.uniqueName):
                                raise ValueError(
                                    f"Weapon mod with uniqueName '{mod.uniqueName}' not found"
                                )
                        if weapon_field.arcane_uniqueName:
                            if not await ArcanePGRepository.exists(session, weapon_field.arcane_uniqueName):
                                raise ValueError(
                                    f"Weapon arcane with uniqueName '{weapon_field.arcane_uniqueName}' not found"
                                )

    @staticmethod
    async def _enrich_build(build: dict) -> dict:
        """Enrich a build with warframe details from Postgres."""
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

        async with postgres_db._session_factory() as session:
            warframe = await WarframePGRepository.find_by_unique_name(
                session, build["warframe_uniqueName"]
            )
            if warframe:
                build["warframe"] = _warframe_to_dict(warframe)
            else:
                build["warframe"] = None

        return build

    @staticmethod
    async def _enrich_build_full(build: dict) -> dict:
        """Full enrichment including weapon and arcane details from Postgres."""
        build = await BuildService._enrich_build(build)

        async with postgres_db._session_factory() as session:
            if build.get("primary_weapon"):
                weapon = await WeaponPGRepository.find_by_unique_name(
                    session, build["primary_weapon"]["weapon_uniqueName"]
                )
                if weapon:
                    build["primary_weapon_details"] = _weapon_to_dict(weapon)
                if build["primary_weapon"].get("arcane_uniqueName"):
                    arcane = await ArcanePGRepository.find_by_unique_name(
                        session, build["primary_weapon"]["arcane_uniqueName"]
                    )
                    if arcane:
                        build["primary_arcane_details"] = _arcane_to_dict(arcane)

            if build.get("secondary_weapon"):
                weapon = await WeaponPGRepository.find_by_unique_name(
                    session, build["secondary_weapon"]["weapon_uniqueName"]
                )
                if weapon:
                    build["secondary_weapon_details"] = _weapon_to_dict(weapon)
                if build["secondary_weapon"].get("arcane_uniqueName"):
                    arcane = await ArcanePGRepository.find_by_unique_name(
                        session, build["secondary_weapon"]["arcane_uniqueName"]
                    )
                    if arcane:
                        build["secondary_arcane_details"] = _arcane_to_dict(arcane)

            if build.get("melee_weapon"):
                weapon = await WeaponPGRepository.find_by_unique_name(
                    session, build["melee_weapon"]["weapon_uniqueName"]
                )
                if weapon:
                    build["melee_weapon_details"] = _weapon_to_dict(weapon)
                if build["melee_weapon"].get("arcane_uniqueName"):
                    arcane = await ArcanePGRepository.find_by_unique_name(
                        session, build["melee_weapon"]["arcane_uniqueName"]
                    )
                    if arcane:
                        build["melee_arcane_details"] = _arcane_to_dict(arcane)

            build["warframe_arcanes_details"] = []
            for arcane_name in build.get("warframe_arcanes", []):
                arcane = await ArcanePGRepository.find_by_unique_name(session, arcane_name)
                if arcane:
                    build["warframe_arcanes_details"].append(_arcane_to_dict(arcane))

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
            builds = [await BuildService._enrich_build(build) for build in builds]
        return builds

    @staticmethod
    async def get_build_by_id(
        build_id: str, user_id: str, include_details: bool = False
    ) -> Optional[dict]:
        build = await BuildRepository.find_by_id(build_id, user_id)
        if not build:
            return None

        if include_details:
            build = await BuildService._enrich_build_full(build)
        else:
            build = await BuildService._enrich_build(build)

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
    async def get_available_warframes() -> list:
        async with postgres_db._session_factory() as session:
            return await WarframePGRepository.find_all_basic(session)

    @staticmethod
    async def get_available_weapons() -> list:
        async with postgres_db._session_factory() as session:
            return await WeaponPGRepository.find_all_basic(session)

    @staticmethod
    async def get_available_mods() -> list:
        async with postgres_db._session_factory() as session:
            return await ModPGRepository.find_all_basic(session)

    @staticmethod
    async def get_available_arcanes() -> list:
        async with postgres_db._session_factory() as session:
            return await ArcanePGRepository.find_all_basic(session)
