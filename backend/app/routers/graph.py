from datetime import datetime
from typing import List

from database.static.age_helper import AgeDB, get_dict_from_agtype
from fastapi import APIRouter, Depends, HTTPException
from models.age_models import (
    CypherRequest,
    GraphEdge,
    GraphNode,
    GraphStats,
    SearchRequest,
)

router = APIRouter(prefix="/api/graph", tags=["graph"])


def get_age_helper():
    try:
        return AgeDB()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize graph connection: {e}"
        )


@router.get("/stats", response_model=GraphStats)
async def get_graph_stats(age: AgeDB = Depends(get_age_helper)):
    """Get statistics about the graph."""
    try:
        # Get total nodes
        node_query = "MATCH (n) RETURN COUNT(n) as total"
        node_result = age.cypher("loot_tables", node_query, "total agtype")
        total_nodes = node_result[0]["total"] if node_result else 0

        # Get total edges
        edge_query = "MATCH ()-[r]->() RETURN COUNT(r) as total"
        edge_result = age.cypher("loot_tables", edge_query, "total agtype")
        total_edges = edge_result[0]["total"] if edge_result else 0

        # Get node types
        types_query = "MATCH (n) RETURN labels(n) as labels, COUNT(n) as node_count"
        types_result = age.cypher(
            "loot_tables", types_query, "labels agtype, node_count agtype"
        )
        node_types = {}
        for row in types_result:
            if row["labels"]:
                label = (
                    row["labels"][0]
                    if isinstance(row["labels"], list)
                    else row["labels"]
                )
                node_types[label] = row["node_count"]

        return GraphStats(
            totalNodes=total_nodes,
            totalEdges=total_edges,
            nodeTypes=node_types,
            lastUpdated=datetime.now().isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get graph stats: {e}")
    finally:
        age.close()


@router.post("/search", response_model=List[GraphNode])
async def search_graph(request: SearchRequest, age: AgeDB = Depends(get_age_helper)):
    """Search for nodes in the graph."""
    try:
        if request.type == "all" or request.type == "nodes":
            # Search nodes by properties
            query = f"""
            MATCH (n)
            WHERE n.name CONTAINS '{request.query}'
               OR toString(n) CONTAINS '{request.query}'
            RETURN n LIMIT 50
            """
            result = age.cypher("loot_tables", query, "n agtype")

            nodes = []
            for row in result:
                node_data = row["n"]
                if isinstance(node_data, dict):
                    nodes.append(
                        GraphNode(
                            id=str(node_data.get("id")),
                            type=node_data.get("labels", ["Unknown"])[0]
                            if node_data.get("labels")
                            else "Unknown",
                            label=node_data.get("labels", ["Unknown"])[0]
                            if node_data.get("labels")
                            else "Unknown",
                            properties=node_data.get("properties", node_data),
                        )
                    )

            return nodes
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search graph: {e}")
    finally:
        age.close()


@router.post("/cypher")
async def execute_cypher(request: CypherRequest, age: AgeDB = Depends(get_age_helper)):
    """Execute a custom Cypher query."""
    try:
        result = age.cypher("loot_tables", request.query, "result agtype")
        return {"results": result}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to execute Cypher query: {e}"
        )
    finally:
        age.close()


@router.post("/nodes", response_model=GraphNode)
async def create_node(node: GraphNode, age: AgeDB = Depends(get_age_helper)):
    """Create a new node."""
    try:
        # Create node properties
        properties = {"name": node.label, **node.properties}

        age.create_node(
            graph="loot_tables",
            label=node.type,
            properties=properties,
            return_node=True,
        )

        if properties:
            return GraphNode(
                id=str(properties.get("id", "")),
                type=node.type,
                label=node.label,
                properties=properties,
            )

        raise HTTPException(status_code=500, detail="Failed to create node")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create node: {e}")
    finally:
        age.close()


@router.put("/nodes/{node_id}", response_model=GraphNode)
async def update_node(
    node_id: str, node: GraphNode, age: AgeDB = Depends(get_age_helper)
):
    """Update an existing node."""
    try:
        # Build update query
        set_clauses = []
        for key, value in node.properties.items():
            set_clauses.append(f"n.{key} = '{value}'")

        if set_clauses:
            query = f"""
            MATCH (n) WHERE id(n) = {node_id}
            SET {", ".join(set_clauses)}
            RETURN n
            """
            age.cypher("loot_tables", query, "n agtype")

            return GraphNode(
                id=node_id, type=node.type, label=node.label, properties=node.properties
            )

        raise HTTPException(status_code=404, detail="Node not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update node: {e}")
    finally:
        age.close()


@router.delete("/nodes/{node_id}")
async def delete_node(node_id: str, age: AgeDB = Depends(get_age_helper)):
    """Delete a node and all its relationships."""
    try:
        query = f"MATCH (n) WHERE id(n) = {node_id} DETACH DELETE n"
        age.cypher("loot_tables", query, "_ agtype")
        return {"message": "Node deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete node: {e}")
    finally:
        age.close()


@router.post("/edges", response_model=GraphEdge)
async def create_edge(edge: GraphEdge, age: AgeDB = Depends(get_age_helper)):
    """Create a new edge between nodes."""
    try:
        # Create relationship
        age.create_relationship(
            graph="loot_tables",
            from_label="Node",  # Generic, would need proper label matching
            from_match={"id": edge.from_node},
            rel_type=edge.relationship_type,
            to_label="Node",  # Generic, would need proper label matching
            to_match={"id": edge.to_node},
            rel_props=edge.properties,
        )

        return edge
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create edge: {e}")
    finally:
        age.close()


@router.delete("/edges/{edge_id}")
async def delete_edge(edge_id: str, age: AgeDB = Depends(get_age_helper)):
    """Delete an edge."""
    try:
        query = f"MATCH ()-[r]-() WHERE id(r) = {edge_id} DELETE r"
        age.cypher("loot_tables", query, "_ agtype")
        return {"message": "Edge deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete edge: {e}")
    finally:
        age.close()


@router.get("/search/nodes")
async def search_nodes_by_name_or_label(
    name: str = "", label: str = "", age: AgeDB = Depends(get_age_helper)
):
    """Search for nodes by name and/or label."""
    try:
        # Build WHERE clause based on provided parameters
        conditions = []
        if name:
            conditions.append(f"n.name CONTAINS '{name}'")
        if label:
            conditions.append(f"'{label}' IN labels(n)")

        if not conditions:
            raise HTTPException(
                status_code=400, detail="At least name or label must be provided"
            )

        where_clause = " AND ".join(conditions)
        query = f"""
        MATCH (n)
        WHERE {where_clause}
        RETURN n, labels(n) as node_labels
        LIMIT 50
        """

        result = age.cypher("loot_tables", query, "n agtype, node_labels agtype")

        nodes = []
        for row in result:
            node_data = get_dict_from_agtype(row["n"])
            node_labels = row["node_labels"]

            if isinstance(node_data, dict):
                # Extract node ID (could be direct or in properties)
                node_id = node_data.get("id")
                if not node_id and "properties" in node_data:
                    node_id = node_data["properties"].get("id")

                # Extract node name (could be direct or in properties)
                node_name = node_data.get("name")
                if not node_name and "properties" in node_data:
                    node_name = node_data["properties"].get("name")

                # Extract properties
                properties = node_data.get("properties", {})

                # Fix label extraction - handle AGE response format
                label = "Unknown"
                if node_labels and len(node_labels) > 0:
                    if isinstance(node_labels, str):
                        label = node_labels.strip('[]"')
                    elif isinstance(node_labels, list):
                        if isinstance(node_labels[0], str):
                            label = node_labels[0]
                        else:
                            label = str(node_labels[0])

                nodes.append(
                    {
                        "id": str(node_id or ""),
                        "name": node_name or "Unknown",
                        "label": label,
                        "properties": properties,
                    }
                )

        return {"nodes": nodes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search nodes: {e}")
    finally:
        age.close()


@router.get("/neighbors", response_model=dict)
async def get_node_neighbors(
    name: str = "",
    label: str = "",
    depth: int = 1,
    age: AgeDB = Depends(get_age_helper),
):
    """Get a node and all its neighbors up to a specified depth using name and/or label."""
    try:
        if depth < 1 or depth > 5:
            raise HTTPException(status_code=400, detail="Depth must be between 1 and 5")

        if not name and not label:
            raise HTTPException(
                status_code=400, detail="At least name or label must be provided"
            )

        # Build WHERE clause to find the start node
        conditions = []
        if name:
            conditions.append(f"start_node.name = '{name}'")
        if label:
            conditions.append(f"'{label}' IN labels(start_node)")

        where_clause = " AND ".join(conditions)

        # Cypher query to get neighbors up to specified depth
        query = f"""
        MATCH (start_node)
        WHERE {where_clause}
        MATCH (start_node)-[r*1..{depth}]->(end_node)
        WITH start_node, r, end_node
        MATCH path = (start_node)-[r]->(end_node)
        RETURN start_node, relationships(path) as rels, end_node
        LIMIT 200
        """

        result = age.cypher(
            "loot_tables", query, "start_node agtype, rels agtype, end_node agtype"
        )

        if not result:
            raise HTTPException(
                status_code=404, detail="No nodes found matching the criteria"
            )

        nodes = {}
        edges = []
        start_node_id = None

        # Process the results to collect all nodes and edges
        for row in result:
            start_node_data = row["start_node"]
            end_node_data = row["end_node"]
            relationships = row["rels"]

            # Add start node
            if isinstance(start_node_data, dict):
                start_id = str(start_node_data.get("id"))
                start_node_id = start_id
                if start_id not in nodes:
                    nodes[start_id] = {
                        "id": start_id,
                        "label": start_node_data.get("name", "Unknown"),
                        "type": (
                            start_node_data.get("labels", ["Unknown"])[0]
                            if start_node_data.get("labels")
                            else "Unknown"
                        ),
                        "properties": start_node_data.get("properties", {}),
                        "isStartNode": True,
                    }

            # Add end node
            if isinstance(end_node_data, dict):
                end_id = str(end_node_data.get("id"))
                if end_id not in nodes:
                    nodes[end_id] = {
                        "id": end_id,
                        "label": end_node_data.get("name", "Unknown"),
                        "type": (
                            end_node_data.get("labels", ["Unknown"])[0]
                            if end_node_data.get("labels")
                            else "Unknown"
                        ),
                        "properties": end_node_data.get("properties", {}),
                        "isStartNode": False,
                    }

            # Add edges for all relationships in the path
            if isinstance(relationships, list):
                for rel in relationships:
                    if isinstance(rel, dict):
                        # Try to get from and to nodes from the relationship
                        rel_query = f"MATCH (n)-[r]->(m) WHERE id(r) = {rel.get('id')} RETURN n, r, m"
                        rel_result = age.cypher(
                            "loot_tables", rel_query, "n agtype, r agtype, m agtype"
                        )

                        if rel_result:
                            rel_row = rel_result[0]
                            from_node = rel_row["n"]
                            to_node = rel_row["m"]
                            rel_data = rel_row["r"]

                            if (
                                isinstance(from_node, dict)
                                and isinstance(to_node, dict)
                                and isinstance(rel_data, dict)
                            ):
                                from_id = str(from_node.get("id"))
                                to_id = str(to_node.get("id"))
                                rel_id = str(rel_data.get("id"))

                                edges.append(
                                    {
                                        "id": rel_id,
                                        "source": from_id,
                                        "target": to_id,
                                        "type": rel_data.get("label", "RELATED_TO"),
                                        "properties": rel_data.get("properties", {}),
                                    }
                                )

        return {
            "nodes": list(nodes.values()),
            "edges": edges,
            "stats": {
                "totalNodes": len(nodes),
                "totalEdges": len(edges),
                "startNodeId": start_node_id,
                "depth": depth,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get node neighbors: {e}"
        )
    finally:
        age.close()
