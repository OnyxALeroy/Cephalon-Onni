from models.static_models import Weapon
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError


def create_weapon_database(client: MongoClient, db_name: str = "cephalon_onni") -> bool:
    """Create weapons collection in MongoDB."""
    try:
        db = client[db_name]

        # Create collection with index
        collection = db["weapons"]

        # Create unique index on weapon_name
        collection.create_index("uniqueName", unique=True)

        print("Created weapons collection")
        return True
    except PyMongoError as e:
        print(f"[ERROR] While creating weapon database: {e}")
        return False


def fill_weapons_db(
    client: MongoClient, weapons: list[Weapon], db_name: str = "cephalon_onni"
) -> bool:
    """Fill weapons collection with data."""
    try:
        db = client[db_name]
        collection = db["weapons"]

        ops = []

        for weapon in weapons:
            doc = {
                "uniqueName": weapon.get("uniqueName"),
                "name": weapon.get("name"),
                "description": weapon.get("description"),
                "product_category": weapon.get("productCategory"),
                "critical_chance": weapon.get("criticalChance"),
                "critical_multiplier": weapon.get("criticalMultiplier"),
                "damage_per_shot": weapon.get("damagePerShot"),
                "fire_rate": weapon.get("fireRate"),
                "mastery_req": weapon.get("masteryReq"),
                "omega_attenuation": weapon.get("omegaAttenuation"),
                "proc_chance": weapon.get("procChance"),
                "total_damage": weapon.get("totalDamage"),
                "codex_secret": weapon.get("codexSecret"),
                # Optional fields
                "accuracy": weapon.get("accuracy"),
                "blocking_angle": weapon.get("blockingAngle"),
                "combo_duration": weapon.get("comboDuration"),
                "exclude_from_codex": weapon.get("excludeFromCodex"),
                "follow_through": weapon.get("followThrough"),
                "heavy_attack_damage": weapon.get("heavyAttackDamage"),
                "heavy_slam_attack": weapon.get("heavySlamAttack"),
                "heavy_slam_radial_damage": weapon.get("heavySlamRadialDamage"),
                "heavy_slam_radius": weapon.get("heavySlamRadius"),
                "magazine_size": weapon.get("magazineSize"),
                "max_level_cap": weapon.get("maxLevelCap"),
                "multishot": weapon.get("multishot"),
                "noise": weapon.get("noise"),
                "prime_omega_attenuation": weapon.get("primeOmegaAttenuation"),
                "range": weapon.get("range"),
                "reload_time": weapon.get("reloadTime"),
                "sentinel": weapon.get("sentinel"),
                "slam_attack": weapon.get("slamAttack"),
                "slam_radial_damage": weapon.get("slamRadialDamage"),
                "slam_radius": weapon.get("slamRadius"),
                "slide_attack": weapon.get("slideAttack"),
                "slot": weapon.get("slot"),
                "trigger": weapon.get("trigger"),
                "wind_up": weapon.get("windUp"),
            }

            ops.append(
                UpdateOne(
                    {"uniqueName": doc["uniqueName"]},
                    {"$set": doc},
                    upsert=True,
                )
            )

        if ops:
            collection.bulk_write(ops, ordered=False)
            print(f"Upserted {len(ops)} weapons")

        return True

    except PyMongoError as e:
        print(f"[ERROR] While loading weapon database: {e}")
        return False
