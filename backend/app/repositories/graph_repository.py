from typing import Any, Dict, List, Optional

from database.static.age_helper import AgeDB, get_dict_from_agtype
from models.age_models import GraphEdge, GraphNode, NodeNeighbor


class GraphRepository:
    def __init__(self, age: AgeDB):
        self.age = age
        self.graph = "loot_tables"

    def execute_cypher(self, query: str, columns: str) -> List[Dict[str, Any]]:
        return self.age.cypher(self.graph, query, columns)

    def create_node(
        self, label: str, properties: Dict[str, Any], return_node: bool = False
    ):
        self.age.create_node(self.graph, label, properties, return_node)

    def create_relationship(
        self,
        from_label: str,
        from_match: dict,
        rel_type: str,
        to_label: str,
        to_match: dict,
        rel_props: Optional[dict] = None,
    ):
        self.age.create_relationship(
            self.graph, from_label, from_match, rel_type, to_label, to_match, rel_props
        )

    def update_node(self, node_id: str, properties: dict) -> Optional[GraphNode]:
        set_clauses = []
        for key, value in properties.items():
            set_clauses.append(f"n.{key} = '{value}'")

        if not set_clauses:
            return None

        query = f"""
        MATCH (n) WHERE id(n) = {node_id}
        SET {", ".join(set_clauses)}
        RETURN n
        """
        self.age.cypher(self.graph, query, "n agtype")
        return True

    def delete_node(self, node_id: str):
        query = f"MATCH (n) WHERE id(n) = {node_id} DETACH DELETE n"
        self.age.cypher(self.graph, query, "_ agtype")

    def delete_edge(self, edge_id: str):
        query = f"MATCH ()-[r]-() WHERE id(r) = {edge_id} DELETE r"
        self.age.cypher(self.graph, query, "_ agtype")

    def search_nodes_raw(
        self, name: str = "", label: str = "", limit: int = 50
    ) -> List[dict]:
        conditions = []
        if name:
            conditions.append(f"n.name CONTAINS '{name}'")
        if label:
            conditions.append(f"'{label}' IN labels(n)")

        if not conditions:
            return []

        where_clause = " AND ".join(conditions)
        query = f"""
        MATCH (n)
        WHERE {where_clause}
        RETURN n, labels(n) as node_labels
        LIMIT {limit}
        """
        return self.age.cypher(self.graph, query, "n agtype, node_labels agtype")

    def get_neighbors_raw(
        self, name: str = "", label: str = "", limit: int = 200
    ) -> List[dict]:
        conditions = []
        if name:
            conditions.append(f"start_node.name = '{name}'")
        if label:
            conditions.append(f"'{label}' IN labels(start_node)")

        if not conditions:
            return []

        where_clause = " AND ".join(conditions)
        query = f"""
        MATCH (start_node)
        WHERE {where_clause}
        MATCH (start_node)-[r]->(end_node)
        RETURN start_node, labels(start_node) as start_labels, r as rel, end_node, labels(end_node) as end_labels
        LIMIT {limit}
        """
        return self.age.cypher(
            self.graph,
            query,
            "start_node agtype, start_labels agtype, rel agtype, end_node agtype, end_labels agtype",
        )

    @staticmethod
    def parse_node_from_row(row: dict) -> Optional[GraphNode]:
        node_data = get_dict_from_agtype(row["n"])
        node_labels = row["node_labels"]

        if not isinstance(node_data, dict):
            return None

        node_id = node_data.get("id")
        if not node_id and "properties" in node_data:
            node_id = node_data["properties"].get("id")

        node_name = node_data.get("name")
        if not node_name and "properties" in node_data:
            node_name = node_data["properties"].get("name")

        properties = node_data.get("properties", {})

        parsed_label = "Unknown"
        if node_labels and len(node_labels) > 0:
            if isinstance(node_labels, str):
                parsed_label = node_labels.strip('[]"')
            elif isinstance(node_labels, list):
                if isinstance(node_labels[0], str):
                    parsed_label = node_labels[0]
                else:
                    parsed_label = str(node_labels[0])

        return GraphNode(
            id=str(node_id or ""),
            name=node_name or "Unknown",
            type=parsed_label,
            label=parsed_label,
            properties=properties,
        )

    @staticmethod
    def parse_neighbor_rows(result: List[dict]):
        starting_node = None
        neighbors = []

        for row in result:
            if starting_node is None:
                start_node_data = get_dict_from_agtype(row["start_node"])
                start_node_labels = get_dict_from_agtype(row["start_labels"])

                if isinstance(start_node_data, dict):
                    start_id = str(start_node_data.get("id", ""))
                    start_label = "Unknown"
                    if start_node_labels and len(start_node_labels) > 0:
                        if isinstance(start_node_labels, str):
                            start_label = start_node_labels.strip('[]"')
                        elif isinstance(start_node_labels, list) and len(start_node_labels) > 0:
                            start_label = str(start_node_labels[0])

                    starting_node = GraphNode(
                        id=start_id,
                        name=start_node_data.get("properties", {}).get("name", "Unknown"),
                        type=start_label,
                        label=start_label,
                        properties=start_node_data.get("properties", {}),
                    )

            end_node_data = get_dict_from_agtype(row["end_node"])
            end_node_labels = get_dict_from_agtype(row["end_labels"])
            rel_data = get_dict_from_agtype(row["rel"])

            if isinstance(end_node_data, dict):
                end_id = str(end_node_data.get("id"))
                end_label = "Unknown"
                if end_node_labels and len(end_node_labels) > 0:
                    if isinstance(end_node_labels, str):
                        end_label = end_node_labels.strip('[]"')
                    elif isinstance(end_node_labels, list) and len(end_node_labels) > 0:
                        end_label = str(end_node_labels[0])

                relationship_type = rel_data.get("label", "Unknown") if rel_data else "Unknown"
                relationship_properties = rel_data.get("properties", {}) if rel_data else {}

                neighbor = NodeNeighbor(
                    id=end_id,
                    name=end_node_data.get("properties", {}).get("name", "Unknown"),
                    type=end_label,
                    properties=end_node_data.get("properties", {}),
                    relationship_type=relationship_type,
                    relationship_properties=relationship_properties,
                    relationship_direction="outgoing",
                )
                neighbors.append(neighbor)

        return starting_node, neighbors
