import os
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import psycopg2
import psycopg2.extras
from psycopg2 import sql


def get_dict_from_agtype(agtype_value: str) -> Any:
    import json
    import re

    if not agtype_value:
        return None

    # Handle arrays: remove suffix from each element
    if agtype_value.startswith("[") and agtype_value.endswith("]"):
        # Remove ::edge, ::vertex etc. from each element in the array
        cleaned = re.sub(r"::\w+", "", agtype_value)
        return json.loads(cleaned)

    # Handle single values: remove suffix
    json_part = agtype_value.split("::")[0]
    return json.loads(json_part)


class AgeDB:
    def __init__(self):
        self.conn = psycopg2.connect(
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database=os.getenv("POSTGRES_DB"),
            host=os.getenv("POSTGRES_HOST"),
            port=os.getenv("POSTGRES_PORT"),
        )
        self.conn.autocommit = True
        self._ensure_age()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_age(self) -> None:
        """Ensure AGE extension and search path are set."""
        with self.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS age;")
            cur.execute("LOAD 'age';")
            cur.execute("SET search_path = ag_catalog, public;")
            # Create default graph if it doesn't exist
            if not self.graph_exists("loot_tables"):
                self.create_graph("loot_tables")

    def _to_cypher_map(self, props: dict) -> str:
        """
        Convert a Python dict to a Cypher map literal.
        """

        def serialize(v):
            if v is None:
                return "null"
            if isinstance(v, bool):
                return "true" if v else "false"
            if isinstance(v, (int, float)):
                return str(v)
            if isinstance(v, str):
                import json

                return json.dumps(v)
            if isinstance(v, list):
                return "[" + ", ".join(serialize(x) for x in v) + "]"
            if isinstance(v, dict):
                return (
                    "{"
                    + ", ".join(f"{k}: {serialize(val)}" for k, val in v.items())
                    + "}"
                )
            raise TypeError(f"Unsupported property type: {type(v)}")

        return "{" + ", ".join(f"{k}: {serialize(v)}" for k, v in props.items()) + "}"

    @contextmanager
    def cursor(self) -> Any:
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            yield cur
        finally:
            cur.close()

    def close(self):
        self.conn.close()

    # ------------------------------------------------------------------
    # Graph management
    # ------------------------------------------------------------------

    def create_graph(self, graph_name: str) -> None:
        with self.cursor() as cur:
            cur.execute("SELECT create_graph(%s);", (graph_name,))

    def drop_graph(self, graph_name: str, cascade: bool = False) -> None:
        with self.cursor() as cur:
            cur.execute(
                "SELECT drop_graph(%s, %s);",
                (graph_name, cascade),
            )

    def list_graphs(self) -> List[str]:
        with self.cursor() as cur:
            cur.execute("SELECT name FROM ag_catalog.ag_graph;")
            return [row["name"] for row in cur.fetchall()]

    # ------------------------------------------------------------------
    # Cypher execution
    # ------------------------------------------------------------------

    def cypher(
        self,
        graph: str,
        query: str,
        columns: str,
    ) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query.

        Args:
            graph: Graph name
            query: Cypher query
            columns: Column definitions, e.g. "n agtype", "n agtype, count agtype"

        Example:
            db.cypher(
                "loot_tables",
                "MATCH (n:Mission) RETURN n",
                "n agtype"
            )
        """
        sql = f"""
        SELECT *
        FROM cypher(%s, $$ {query} $$)
        AS ({columns})
        """
        with self.cursor() as cur:
            cur.execute(sql, (graph,))
            return [dict(row) for row in cur.fetchall()]

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def create_node(
        self,
        graph: str,
        label: str,
        properties: Dict[str, Any],
        return_node: bool = False,
    ):
        prop_map = self._to_cypher_map(properties)

        cypher = f"""
        MERGE (n:{label} {prop_map})
        """

        if return_node:
            cypher += "\nRETURN n"

        sql = f"""
        SELECT 1
        FROM cypher(%s, $$
        {cypher}
        $$) AS (_ agtype)
        """

        with self.cursor() as cur:
            cur.execute(sql, (graph,))

    def create_relationship(
        self,
        graph: str,
        from_label: str,
        from_match: dict,
        rel_type: str,
        to_label: str,
        to_match: dict,
        rel_props: dict | None = None,
    ) -> None:
        rel_props = rel_props or {}

        from_map = self._to_cypher_map(from_match)
        to_map = self._to_cypher_map(to_match)
        rel_map = self._to_cypher_map(rel_props) if rel_props else ""

        cypher = f"""
        MATCH (f:{from_label} {from_map})
        MATCH (t:{to_label} {to_map})
        MERGE (f)-[r:{rel_type}]->(t)
        """

        if rel_props:
            cypher += f"\nSET r += {rel_map}"

        query = sql.SQL("""
        SELECT 1
        FROM cypher({graph}, $$
        {cypher}
        $$) AS (_ agtype)
        """).format(
            graph=sql.Literal(graph),
            cypher=sql.SQL(cypher),
        )

        with self.cursor() as cur:
            cur.execute(query)

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def match(
        self,
        graph: str,
        label: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        filters = filters or {}
        where = ""
        if filters:
            conds = [f"n.{k} = '{v}'" for k, v in filters.items()]
            where = "WHERE " + " AND ".join(conds)

        limit_clause = f"LIMIT {limit}" if limit else ""

        cypher = f"""
        MATCH (n:{label})
        {where}
        RETURN n
        {limit_clause}
        """

        with self.cursor() as cur:
            cur.execute(
                f"""
                SELECT n
                FROM cypher(%s, $$ {cypher} $$)
                AS (n agtype)
                """,
                (graph,),
            )
            return [dict(row) for row in cur.fetchall()]

    # ------------------------------------------------------------------
    # Deletion
    # ------------------------------------------------------------------

    def graph_exists(self, graph_name: str) -> bool:
        with self.cursor() as cur:
            cur.execute(
                """
                        SELECT 1
                        FROM ag_catalog.ag_graph
                        WHERE name = %s
                        """,
                (graph_name,),
            )
            return cur.fetchone() is not None

    def clear_graph(self, graph_name: str) -> bool:
        """
        Safely clear all nodes and edges from a graph.

        Returns:
            True  -> graph existed and was cleared
            False -> graph did not exist, nothing done
        """
        if not self.graph_exists(graph_name):
            return False

        with self.cursor() as cur:
            cur.execute(
                """
                SELECT 1
                FROM cypher(%s, $$
                    MATCH (n)
                    DETACH DELETE n
                $$) AS (_ agtype)
                """,
                (graph_name,),
            )
        return True
