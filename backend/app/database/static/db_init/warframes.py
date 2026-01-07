from sqlalchemy import text
from sqlalchemy.orm import Session

from database.static.db_init.db_init_models import Warframe


def create_warframe_database(session: Session) -> bool:
    try:
        session.execute(
            text("""
            CREATE TABLE IF NOT EXISTS warframes (
                id SERIAL PRIMARY KEY,
                uniqueName VARCHAR(255) NOT NULL UNIQUE,
                name VARCHAR(255) NOT NULL,
                parentName VARCHAR(255),
                description TEXT,
                health INTEGER,
                shield INTEGER,
                armor INTEGER,
                stamina INTEGER,
                power INTEGER,
                codexSecret BOOLEAN,
                masteryReq INTEGER,
                sprintSpeed FLOAT,
                passiveDescription TEXT,
                exalted TEXT[],
                productCategory VARCHAR(50)
            );
        """)
        )
        session.execute(
            text("""
            CREATE TABLE IF NOT EXISTS warframe_abilities (
                id SERIAL PRIMARY KEY,
                warframe_uniqueName VARCHAR(255) NOT NULL,
                abilityUniqueName VARCHAR(255) NOT NULL,
                abilityName VARCHAR(255) NOT NULL,
                description TEXT,
                FOREIGN KEY (warframe_uniqueName) REFERENCES warframes(uniqueName),
                UNIQUE (warframe_uniqueName, abilityUniqueName)
            );
        """)
        )
        session.commit()
        return True
    except Exception as e:
        print(f"[ERROR] While creating warframe database: {e}")
        session.rollback()
        return False


def fill_warframe_db(session: Session, warframes: list[Warframe]) -> bool:
    try:
        for warframe in warframes:
            session.execute(
                text("""
                INSERT INTO warframes (
                    uniqueName, name, parentName, description, health, shield, armor,
                    stamina, power, codexSecret, masteryReq, sprintSpeed, passiveDescription,
                    exalted, productCategory
                )
                VALUES(:uniqueName, :name, :parentName, :description, :health, :shield, :armor,
                       :stamina, :power, :codexSecret, :masteryReq, :sprintSpeed, :passiveDescription,
                       :exalted, :productCategory)
                ON CONFLICT (uniqueName) DO NOTHING
            """),
                {
                    "uniqueName": warframe["uniqueName"],
                    "name": warframe["name"],
                    "parentName": warframe.get("parentName"),
                    "description": warframe["description"],
                    "health": warframe["health"],
                    "shield": warframe["shield"],
                    "armor": warframe["armor"],
                    "stamina": warframe["stamina"],
                    "power": warframe["power"],
                    "codexSecret": warframe["codexSecret"],
                    "masteryReq": warframe["masteryReq"],
                    "sprintSpeed": warframe["sprintSpeed"],
                    "passiveDescription": warframe.get("passiveDescription"),
                    "exalted": warframe.get("exalted", []),
                    "productCategory": warframe["productCategory"],
                },
            )

            abilities = warframe.get("abilities", [])
            if not isinstance(abilities, list):
                print(
                    f"[ERROR] abilities is not a list: {type(abilities)} for warframe {warframe.get('uniqueName', 'unknown')}"
                )
                continue
            for ability in abilities:
                session.execute(
                    text("""
                    INSERT INTO warframe_abilities (
                        warframe_uniqueName, abilityUniqueName, abilityName, description
                    )
                    VALUES(:warframe_uniqueName, :abilityUniqueName, :abilityName, :description)
                    ON CONFLICT (warframe_uniqueName, abilityUniqueName) DO NOTHING
                """),
                    {
                        "warframe_uniqueName": warframe["uniqueName"],
                        "abilityUniqueName": ability.get("abilityUniqueName", ""),
                        "abilityName": ability.get("abilityName", ""),
                        "description": ability.get("description", ""),
                    },
                )
        session.commit()
        return True
    except KeyError as ke:
        print(f"[ERROR] While loading warframe database: key error {ke}")
        session.rollback()
        return False
    except Exception as e:
        print(f"[ERROR] While loading warframe database: {e}")
        session.rollback()
        return False
