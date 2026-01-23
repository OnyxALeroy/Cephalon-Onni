from models.static_models import Weapon
from pymongo import MongoClient
from pymongo.errors import PyMongoError


def create_weapon_database(client: MongoClient, db_name: str = "cephalon_onni") -> bool:
    """Create weapons collection in MongoDB."""
    try:
        db = client[db_name]

        # Create collection with index
        collection = db["weapons"]

        # Create unique index on weapon_name
        collection.create_index("weapon_name", unique=True)

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

        documents = []
        for weapon in weapons:
            # Create document
            doc = {
                "weapon_name": weapon.get("uniqueName"),
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

            documents.append(doc)

        if documents:
            collection.insert_many(documents)
            print(f"Inserted {len(documents)} weapons")

        return True
    except KeyError as ke:
        print(f"[ERROR] While loading weapon database: {ke}")
        return False
    except PyMongoError as e:
        print(f"[ERROR] While loading weapon database: {e}")
        return False
