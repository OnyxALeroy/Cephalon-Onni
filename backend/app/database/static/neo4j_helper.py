import logging
import os
import time
from contextlib import contextmanager
from typing import Any, Dict, List, Literal, Optional, Union, LiteralString, overload

from neo4j import Driver, GraphDatabase, Result, Session


# Define type-safe query templates
class QueryTemplates:
    CREATE_NODE = "CREATE (n:{label} $properties) RETURN n"
    CREATE_NODES_BATCH = "UNWIND $batch AS properties CREATE (n:{label} $properties) RETURN n"
    MATCH_NODE = "MATCH (n:{label}"
    MATCH_NODE_WITH_PROPS = MATCH_NODE + " $props)"
    MATCH_NODE_NO_PROPS = MATCH_NODE + ")"
    RETURN_NODE = " RETURN n"
    UPDATE_NODE = "MATCH (n:{label} $match_props) SET n += $update_props RETURN n"
    DELETE_NODE = "MATCH (n:{label} $props) DETACH DELETE n"
    CREATE_RELATIONSHIP = """
    MATCH (a:{from_label} $from_props), (b:{to_label} $to_props)
    CREATE (a)-[r:{relationship_type}{rel_props}]->(b)
    RETURN r
    """
    MATCH_BASE = "MATCH "
    COUNT_NODES = "MATCH (n{label_part}{props_part}) RETURN count(n) as count"
    COUNT_RELS = "MATCH (){rel_part}() RETURN count(r) as count"
    CLEAR_DB = "MATCH (n) DETACH DELETE n"
    APOC_CLEAR = "CALL apoc.schema.assert({}, {}, true) RETURN *"
    DB_LABELS = "CALL db.labels() RETURN label"
    DB_REL_TYPES = "CALL db.relationshipTypes() RETURN relationshipType"


class Neo4jHelper:
    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        database: str = "neo4j",
    ):
        uri = uri or os.getenv("NEO4J_URI")
        user = user or os.getenv("NEO4J_USER")
        password = password or os.getenv("NEO4J_PASSWORD")
        
        if not uri:
            raise ValueError("NEO4J_URI environment variable is not set")
        if not user:
            raise ValueError("NEO4J_USER environment variable is not set")
        if not password:
            raise ValueError("NEO4J_PASSWORD environment variable is not set")
        
        self.uri: str = uri
        self.user: str = user
        self.password: str = password
        self.database: str = database
        self.driver: Optional[Driver] = None
        self.logger = logging.getLogger(__name__)

    def connect(self, with_retry: bool = False, retry_cooldown: int = 5) -> None:
        if not self.driver:
            try:
                self.driver = GraphDatabase.driver(
                    self.uri, auth=(self.user, self.password)
                )
                if self.driver:
                    self.driver.verify_connectivity()
                    self.logger.info(f"Connected to Neo4j at {self.uri}")
                else:
                    raise ConnectionError("Failed to create Neo4j driver")
            except Exception as e:
                self.logger.error(f"Failed to connect to Neo4j at {self.uri}: {e}")
                if with_retry:
                    while True:
                        try:
                            time.sleep(retry_cooldown)
                            if self.driver:
                                self.driver.verify_connectivity()
                                self.logger.info(f"Connected to Neo4j at {self.uri}")
                                break
                        except Exception as retry_e:
                            self.logger.error(f"Retrying connection: {retry_e}")
                else:
                    raise

    def close(self) -> None:
        if self.driver:
            self.driver.close()
            self.driver = None
            self.logger.info("Neo4j connection closed")

    @contextmanager
    def session(self, database: Optional[str] = None):
        if not self.driver:
            self.connect()
        if not self.driver:
            raise ConnectionError("Failed to establish Neo4j connection")
        db = database or self.database
        session = self.driver.session(database=db)
        try:
            yield session
        finally:
            session.close()

    def execute_query(
        self,
        query: LiteralString,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        with self.session(database) as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    def execute_write_query(
        self,
        query: LiteralString,
        parameters: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        with self.session(database) as session:
            result = session.execute_write(lambda tx: tx.run(query, parameters or {}))
            return [record.data() for record in result]

    def create_node(
        self, 
        label: str, 
        properties: Dict[str, Any], 
        database: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        if not isinstance(label, str) or not label.strip():
            raise ValueError("Label must be a non-empty string")
        if not isinstance(properties, dict):
            raise ValueError("Properties must be a dictionary")
            
        # Build the query dynamically but cast to LiteralString for the Neo4j driver
        query_str = QueryTemplates.CREATE_NODE.format(label=label)
        query: LiteralString = query_str  # type: ignore
        
        with self.session(database) as session:
            result = session.execute_write(
                lambda tx: tx.run(query, {"properties": properties})
            )
            node = result.single()
            return node["n"] if node else None

    def create_nodes_batch(
        self,
        label: str,
        nodes_list: List[Dict[str, Any]],
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not isinstance(label, str) or not label.strip():
            raise ValueError("Label must be a non-empty string")
        if not isinstance(nodes_list, list) or not nodes_list:
            raise ValueError("Nodes list must be a non-empty list")
        if not all(isinstance(node, dict) for node in nodes_list):
            raise ValueError("All nodes must be dictionaries")
            
        query_str = QueryTemplates.CREATE_NODES_BATCH.format(label=label)
        query: LiteralString = query_str  # type: ignore
        
        with self.session(database) as session:
            result = session.execute_write(
                lambda tx: tx.run(query, {"batch": nodes_list})
            )
            return [record.data()["n"] for record in result]

    def find_nodes(
        self,
        label: str,
        properties: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not isinstance(label, str) or not label.strip():
            raise ValueError("Label must be a non-empty string")
        if properties is not None and not isinstance(properties, dict):
            raise ValueError("Properties must be a dictionary or None")
        if limit is not None and (not isinstance(limit, int) or limit <= 0):
            raise ValueError("Limit must be a positive integer or None")
            
        # Build query dynamically
        if properties:
            base_query = QueryTemplates.MATCH_NODE_WITH_PROPS.format(label=label)
        else:
            base_query = QueryTemplates.MATCH_NODE_NO_PROPS.format(label=label)
            
        query_str = base_query + QueryTemplates.RETURN_NODE
        if limit:
            query_str = f"{query_str} LIMIT {limit}"
            
        query: LiteralString = query_str  # type: ignore
        params = {"props": properties} if properties else {}

        with self.session(database) as session:
            result = session.run(query, params)
            return [record.data()["n"] for record in result]

    def update_node(
        self,
        label: str,
        match_properties: Dict[str, Any],
        update_properties: Dict[str, Any],
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not isinstance(label, str) or not label.strip():
            raise ValueError("Label must be a non-empty string")
        if not isinstance(match_properties, dict) or not match_properties:
            raise ValueError("Match properties must be a non-empty dictionary")
        if not isinstance(update_properties, dict) or not update_properties:
            raise ValueError("Update properties must be a non-empty dictionary")
            
        query_str = QueryTemplates.UPDATE_NODE.format(label=label)
        query: LiteralString = query_str  # type: ignore
        params = {"match_props": match_properties, "update_props": update_properties}
        
        with self.session(database) as session:
            result = session.execute_write(lambda tx: tx.run(query, params))
            return [record.data()["n"] for record in result]

    def delete_node(
        self, 
        label: str, 
        properties: Dict[str, Any], 
        database: Optional[str] = None
    ) -> bool:
        if not isinstance(label, str) or not label.strip():
            raise ValueError("Label must be a non-empty string")
        if not isinstance(properties, dict) or not properties:
            raise ValueError("Properties must be a non-empty dictionary")
            
        query_str = QueryTemplates.DELETE_NODE.format(label=label)
        query: LiteralString = query_str  # type: ignore
        
        with self.session(database) as session:
            result = session.execute_write(
                lambda tx: tx.run(query, {"props": properties})
            )
            return result.consume().counters.nodes_deleted > 0

    def create_relationship(
        self,
        from_label: str,
        from_props: Dict[str, Any],
        relationship_type: str,
        to_label: str,
        to_props: Dict[str, Any],
        relationship_props: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        # Validate inputs
        for name, value in [("from_label", from_label), ("to_label", to_label), ("relationship_type", relationship_type)]:
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name, value in [("from_props", from_props), ("to_props", to_props)]:
            if not isinstance(value, dict) or not value:
                raise ValueError(f"{name} must be a non-empty dictionary")
        if relationship_props is not None and not isinstance(relationship_props, dict):
            raise ValueError("Relationship properties must be a dictionary or None")
            
        rel_props_str = " $rel_props" if relationship_props else ""
        query_str = QueryTemplates.CREATE_RELATIONSHIP.format(
            from_label=from_label,
            to_label=to_label,
            relationship_type=relationship_type,
            rel_props=rel_props_str
        )
        query: LiteralString = query_str  # type: ignore
        params = {"from_props": from_props, "to_props": to_props}
        if relationship_props:
            params["rel_props"] = relationship_props

        with self.session(database) as session:
            result = session.execute_write(lambda tx: tx.run(query, params))
            rel = result.single()
            return rel["r"] if rel else None

    def find_relationships(
        self,
        relationship_type: Optional[str] = None,
        from_label: Optional[str] = None,
        to_label: Optional[str] = None,
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        # Validate inputs
        if relationship_type is not None and (not isinstance(relationship_type, str) or not relationship_type.strip()):
            raise ValueError("Relationship type must be a non-empty string or None")
        for name, value in [("from_label", from_label), ("to_label", to_label)]:
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be a non-empty string or None")
                
        # Build query components
        query_parts = [QueryTemplates.MATCH_BASE]
        
        if from_label:
            query_parts.append(f"(a:{from_label})")
        else:
            query_parts.append("(a)")

        if relationship_type:
            query_parts.append(f"-[r:{relationship_type}]-")
        else:
            query_parts.append("-[r]-")

        if to_label:
            query_parts.append(f"(b:{to_label})")
        else:
            query_parts.append("(b)")

        query_parts.append(" RETURN a, r, b")
        query_str = "".join(query_parts)
        query: LiteralString = query_str  # type: ignore

        with self.session(database) as session:
            result = session.run(query)
            return [record.data() for record in result]

    def get_node_relationships(
        self,
        label: str,
        properties: Dict[str, Any],
        direction: Literal["in", "out", "both"] = "both",
        relationship_type: Optional[str] = None,
        database: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        if not isinstance(label, str) or not label.strip():
            raise ValueError("Label must be a non-empty string")
        if not isinstance(properties, dict) or not properties:
            raise ValueError("Properties must be a non-empty dictionary")
        if relationship_type is not None and (not isinstance(relationship_type, str) or not relationship_type.strip()):
            raise ValueError("Relationship type must be a non-empty string or None")

        if direction == "out":
            pattern = f"-[{relationship_type}]->" if relationship_type else "-[r]->"
        elif direction == "in":
            pattern = f"<-[{relationship_type}]-" if relationship_type else "<-[r]-"
        else:
            pattern = f"-[{relationship_type}]-" if relationship_type else "-[r]-"

        query_str = f"MATCH (n:{label} $props) {pattern} (related) RETURN n, r, related"
        query: LiteralString = query_str  # type: ignore

        with self.session(database) as session:
            result = session.run(query, {"props": properties})
            return [record.data() for record in result]

    def delete_relationship(
        self,
        from_label: str,
        from_props: Dict[str, Any],
        relationship_type: str,
        to_label: str,
        to_props: Dict[str, Any],
        database: Optional[str] = None,
    ) -> bool:
        # Validate inputs
        for name, value in [("from_label", from_label), ("to_label", to_label), ("relationship_type", relationship_type)]:
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        for name, value in [("from_props", from_props), ("to_props", to_props)]:
            if not isinstance(value, dict) or not value:
                raise ValueError(f"{name} must be a non-empty dictionary")
                
        query_str = f"""
        MATCH (a:{from_label} $from_props)-[r:{relationship_type}]->(b:{to_label} $to_props)
        DELETE r
        """
        query: LiteralString = query_str  # type: ignore
        params = {"from_props": from_props, "to_props": to_props}

        with self.session(database) as session:
            result = session.execute_write(lambda tx: tx.run(query, params))
            return result.consume().counters.relationships_deleted > 0

    def count_nodes(
        self,
        label: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
        database: Optional[str] = None,
    ) -> int:
        if label is not None and (not isinstance(label, str) or not label.strip()):
            raise ValueError("Label must be a non-empty string or None")
        if properties is not None and not isinstance(properties, dict):
            raise ValueError("Properties must be a dictionary or None")

        # Build query parts
        label_part = f":{label}" if label else ""
        props_part = " $props" if properties else ""
        
        query_str = QueryTemplates.COUNT_NODES.format(
            label_part=label_part,
            props_part=props_part
        )
        query: LiteralString = query_str  # type: ignore
        params = {"props": properties} if properties else {}

        with self.session(database) as session:
            result = session.run(query, params)
            count_result = result.single()
            return count_result["count"] if count_result else 0

    def count_relationships(
        self, 
        relationship_type: Optional[str] = None, 
        database: Optional[str] = None
    ) -> int:
        if relationship_type is not None and (not isinstance(relationship_type, str) or not relationship_type.strip()):
            raise ValueError("Relationship type must be a non-empty string or None")

        rel_part = f"[{relationship_type}]" if relationship_type else "[r]"
        query_str = QueryTemplates.COUNT_RELS.format(rel_part=rel_part)
        query: LiteralString = query_str  # type: ignore

        with self.session(database) as session:
            result = session.run(query)
            count_result = result.single()
            return count_result["count"] if count_result else 0

    def clear_database(
        self, database: Optional[str] = None, confirm: bool = True
    ) -> None:
        if confirm:
            response = input(
                f"Are you sure you want to clear database '{database or self.database}'? [y/N]: "
            )
            if response.lower() != "y":
                print("Database clear cancelled.")
                return

        queries: List[LiteralString] = [
            QueryTemplates.CLEAR_DB,
            QueryTemplates.APOC_CLEAR,
        ]

        for query in queries:
            try:
                self.execute_write_query(query, database=database)
            except Exception as e:
                self.logger.warning(
                    f"Query failed (may be expected if APOC not available): {e}"
                )

    def get_database_info(self, database: Optional[str] = None) -> Dict[str, Any]:
        info: Dict[str, Any] = {}

        try:
            node_count = self.count_nodes(database=database)
            info["node_count"] = node_count
        except Exception as e:
            info["node_count_error"] = str(e)

        try:
            rel_count = self.count_relationships(database=database)
            info["relationship_count"] = rel_count
        except Exception as e:
            info["relationship_count_error"] = str(e)

        try:
            labels_result = self.execute_query(QueryTemplates.DB_LABELS, database=database)
            info["labels"] = [record["label"] for record in labels_result]
        except Exception as e:
            info["labels_error"] = str(e)

        try:
            rel_types_result = self.execute_query(QueryTemplates.DB_REL_TYPES, database=database)
            info["relationship_types"] = [
                record["relationshipType"] for record in rel_types_result
            ]
        except Exception as e:
            info["relationship_types_error"] = str(e)

        return info

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()