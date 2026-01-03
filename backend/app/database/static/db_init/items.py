from sqlalchemy import text
from sqlalchemy.orm import Session


def create_item_database(session: Session) -> bool:
    try:
        session.execute(
            text("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            uniqueName TEXT NOT NULL UNIQUE,
            imageURL TEXT NOT NULL
        )""")
        )
        session.commit()
        return True
    except Exception as e:
        print(f"[ERROR] While creating item database: {e}")
        session.rollback()
        return False
