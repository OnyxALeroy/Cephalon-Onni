import os
from typing import List, Dict, Any, Optional
import psycopg2
import psycopg2.extras


class StaticDB:
    def __init__(self):
        self.conn = psycopg2.connect(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
        )
        self.conn.autocommit = True

    @staticmethod
    def _get_connection():
        return psycopg2.connect(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
        )

    def get_warframe_by_unique_name(self, unique_name: str) -> Optional[Dict[str, Any]]:
        """Get a warframe by its uniqueName with all details including abilities"""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT w.*, 
                       array_agg(
                           json_build_object(
                               'abilityUniqueName', wa.abilityUniqueName,
                               'abilityName', wa.abilityName,
                               'description', wa.description
                           )
                       ) FILTER (WHERE wa.abilityUniqueName IS NOT NULL) as abilities
                FROM warframes w
                LEFT JOIN warframe_abilities wa ON w.uniqueName = wa.warframe_uniqueName
                WHERE w.uniqueName = %s
                GROUP BY w.id, w.uniqueName, w.name, w.parentName, w.description, 
                         w.health, w.shield, w.armor, w.stamina, w.power, w.codexSecret,
                         w.masteryReq, w.sprintSpeed, w.passiveDescription, w.exalted, w.productCategory
            """, (unique_name,))
            
            result = cur.fetchone()
            if result:
                # Convert RealDictRow to regular dict
                warframe = dict(result)
                # Convert abilities from None to empty list if no abilities
                if warframe['abilities'] == [None]:
                    warframe['abilities'] = []
                return warframe
            return None

    def get_all_warframes(self) -> List[Dict[str, Any]]:
        """Get all warframes with basic info"""
        with self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT uniqueName, name, description, health, shield, armor, power, masteryReq
                FROM warframes
                ORDER BY name
            """)
            return [dict(row) for row in cur.fetchall()]

    def warframe_exists(self, unique_name: str) -> bool:
        """Check if a warframe with the given uniqueName exists"""
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM warframes WHERE uniqueName = %s", (unique_name,))
            return cur.fetchone() is not None

    def close(self):
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()


# Singleton instance for reuse
_static_db_instance = None

def get_static_db() -> StaticDB:
    """Get a singleton instance of StaticDB"""
    global _static_db_instance
    if _static_db_instance is None:
        _static_db_instance = StaticDB()
    return _static_db_instance