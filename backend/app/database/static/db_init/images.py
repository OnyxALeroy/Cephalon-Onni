from sqlalchemy import text
from sqlalchemy.orm import Session

from database.static.db_init.db_init_models import ImgItem


def create_images_database(session: Session) -> bool:
    try:
        session.execute(
            text("""
            CREATE TABLE IF NOT EXISTS items (
                id SERIAL PRIMARY KEY,
                uniqueName VARCHAR(255) NOT NULL,
                imageURL VARCHAR(255) NOT NULL
            );
        """)
        )
        session.commit()
        return True
    except Exception as e:
        print(f"[ERROR] While creating image database: {e}")
        session.rollback()
        return False


def fill_img_db(session: Session, items: list[ImgItem]) -> bool:
    try:
        for item in items:
            session.execute(
                text("""
                INSERT INTO items (uniqueName, imageURL)
                VALUES(:uniqueName, :imageURL)
                ON CONFLICT (uniqueName) DO NOTHING
            """),
                {
                    "uniqueName": item.get("uniqueName"),
                    "imageURL": item.get("textureLocation"),
                },
            )
        session.commit()
        return True
    except KeyError as ke:
        print(f"[ERROR] While loading image database: {ke}")
        session.rollback()
        return False
    except Exception as e:
        print(f"[ERROR] While loading image database: {e}")
        session.rollback()
        return False
