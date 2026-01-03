from sqlalchemy import text
from sqlalchemy.orm import Session


def create_translation_database(session: Session) -> bool:
    try:
        session.execute(
            text("""
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER NOT NULL,
            language TEXT NOT NULL,
            value TEXT NOT NULL,
            PRIMARY KEY (id, language)
        )""")
        )
        session.commit()
        return True
    except Exception as e:
        print(f"[ERROR] While creating translation database: {e}")
        session.rollback()
        return False
