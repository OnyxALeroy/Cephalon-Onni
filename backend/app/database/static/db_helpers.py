from typing import List, Optional, Any
from sqlalchemy import text, inspect
from sqlalchemy.orm import Session


# ----------------------------------------------------------------------------------------------------------------------
# DB Inspection
# ----------------------------------------------------------------------------------------------------------------------

def get_value_by_column(
    session: Session,
    table: str,
    lookup_column: str,
    lookup_value: Any,
    return_column: str = "id",
) -> Optional[Any]:
    result = session.execute(text(f"""
        SELECT {return_column}
        FROM {table}
        WHERE {lookup_column} = :lookup_value
        LIMIT 1
    """), {"lookup_value": lookup_value})
    row = result.fetchone()
    return row[0] if row else None

def value_exists(session: Session, table: str, column: str, value:str|int|bool) -> bool:
    result = session.execute(text(f"SELECT EXISTS(SELECT 1 FROM {table} WHERE {column} = :value)"), {"value": value}).fetchone()
    if result is None:
        return False
    return bool(result[0])

# ----------------------------------------------------------------------------------------------------------------------
# DB Safe deletion
# ----------------------------------------------------------------------------------------------------------------------

def drop_tables(session: Session, tables: List[str]) -> None:
    try:
        for table in tables:
            answer = input(f"Drop table '{table}' ? [y/N]: ").strip().lower()
            if answer != "y":
                print(f"[SKIPPED] {table}")
                continue
            session.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            print(f"[DROPPED] {table}")
        session.commit()
    except Exception as e:
        print(f"[ERROR] While dropping tables: {e}")
        session.rollback()
    return

# ----------------------------------------------------------------------------------------------------------------------
# DB VIEWER
# ----------------------------------------------------------------------------------------------------------------------

def list_tables(session: Session) -> List[str]:
    inspector = inspect(session.bind)
    if inspector is None:
        print("[ERROR] The table could not be inspected in list_table")
        return []
    return inspector.get_table_names()

def describe_table(session: Session, table: str) -> None:
    inspector = inspect(session.bind)
    if inspector is None:
        print("[ERROR] The table could not be inspected in describe_table")
        return None
    columns = inspector.get_columns(table)

    print(f"\n--- {table} ---")
    for column in columns:
        name = column["name"]
        col_type = str(column["type"])
        nullable = column["nullable"]
        default = column.get("default")
        primary_key = column.get("primary_key", False)
        
        flags: list[str] = []
        if primary_key:
            flags.append("PK")
        if not nullable:
            flags.append("NOT NULL")
        if default is not None:
            flags.append(f"DEFAULT {default}")
        flags_str = f" ({', '.join(flags)})" if flags else ""
        print(f"  {name:<15} {col_type:<20}{flags_str}")

PREVIEW_ROWS = 10
def preview_table(session: Session, table: str, limit: int = PREVIEW_ROWS) -> None:
    result = session.execute(text(f"SELECT * FROM {table} LIMIT {limit}"))
    rows = result.fetchall()

    if not rows:
        print("  [EMPTY]")
        return

    for row in rows:
        print(" ", row)