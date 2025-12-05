import sqlite3
from typing import List, Optional, Any


# ----------------------------------------------------------------------------------------------------------------------
# DB Inspection
# ----------------------------------------------------------------------------------------------------------------------

def get_value_by_column(
    cursor: sqlite3.Cursor,
    table: str,
    lookup_column: str,
    lookup_value: Any,
    return_column: str = "id",
) -> Optional[Any]:
    cursor.execute(f"""
        SELECT {return_column}
        FROM {table}
        WHERE {lookup_column} = ?
        LIMIT 1
    """, (lookup_value,))
    row = cursor.fetchone()
    return row[0] if row else None

def value_exists(cursor: sqlite3.Cursor, table: str, column: str, value) -> bool:
    cursor.execute(
        f"SELECT EXISTS(SELECT 1 FROM {table} WHERE {column} = ?)",
        (value,)
    )
    return bool(cursor.fetchone()[0])

# ----------------------------------------------------------------------------------------------------------------------
# DB Safe deletion
# ----------------------------------------------------------------------------------------------------------------------

def drop_tables(conn: sqlite3.Connection, tables: List[str]) -> None:
    try:
        cursor = conn.cursor()
        for table in tables:
            answer = input(f"Drop table '{table}' ? [y/N]: ").strip().lower()
            if answer != "y":
                print(f"[SKIPPED] {table}")
                continue
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"[DROPPED] {table}")
        conn.commit()
    except Exception as e:
        print(f"[ERROR] While dropping tables: {e}")
    return

# ----------------------------------------------------------------------------------------------------------------------
# DB VIEWER
# ----------------------------------------------------------------------------------------------------------------------

def list_tables(conn: sqlite3.Connection) -> List[str]:
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name 
        FROM sqlite_master
        WHERE type='table'
    """)
    return [row[0] for row in cursor.fetchall()]

def describe_table(conn: sqlite3.Connection, table: str) -> None:
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table});")
    cols = cursor.fetchall()

    print(f"\n--- {table} ---")
    for cid, name, col_type, notnull, default, pk in cols:
        flags = []
        if pk:
            flags.append("PK")
        if notnull:
            flags.append("NOT NULL")
        flags = f" ({', '.join(flags)})" if flags else ""
        print(f"  {name:<15} {col_type:<10}{flags}")

PREVIEW_ROWS = 10
def preview_table(conn: sqlite3.Connection, table: str, limit: int = PREVIEW_ROWS) -> None:
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table} LIMIT {limit}")
    rows = cursor.fetchall()

    if not rows:
        print("  [EMPTY]")
        return

    for row in rows:
        print(" ", row)
