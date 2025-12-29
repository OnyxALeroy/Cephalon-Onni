import logging

from database.static.age_helper import AgeDB, get_dict_from_agtype
from fastapi import APIRouter, Depends, HTTPException
from models.age_models import (
    CypherRequest,
    GraphEdge,
    GraphNode,
    GraphResponse,
    NodeNeighbor,
    NodeNeighborsResponse,
    NodeSearchResponse,
    SearchRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin/graph", tags=["graph"])


def get_age_helper():
    try:
        return AgeDB()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize graph connection: {e}"
        )


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
                name=node.label,
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
                id=node_id,
                name=node.label,
                type=node.type,
                label=node.label,
                properties=node.properties,
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


@router.post("/search", response_model=NodeSearchResponse)
async def search_nodes(request: SearchRequest, age: AgeDB = Depends(get_age_helper)):
    """Search for nodes using the frontend's expected format."""
    try:
        # For now, treat the query as a name search
        name = request.query
        label = ""  # Default to empty label

        # Build WHERE clause based on provided parameters
        conditions = []
        if name:
            conditions.append(f"n.name CONTAINS '{name}'")
        if label:
            conditions.append(f"'{label}' IN labels(n)")

        if not conditions:
            return NodeSearchResponse(nodes=[])

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
                    GraphNode(
                        id=str(node_id or ""),
                        name=node_name or "Unknown",
                        type=label,
                        label=label,
                        properties=properties,
                    )
                )

        return NodeSearchResponse(nodes=nodes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search nodes: {e}")
    finally:
        age.close()


@router.get("/search/nodes", response_model=NodeSearchResponse)
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
                node_id = node_data.get("id")
                node_name = node_data["properties"].get("name")
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

        return NodeSearchResponse(nodes=nodes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search nodes: {e}")
    finally:
        age.close()


@router.get("/neighbors", response_model=NodeNeighborsResponse)
async def get_node_neighbors(
    name: str = "",
    label: str = "",
    age: AgeDB = Depends(get_age_helper),
):
    """Get the direct neighborGraphResponses of a node using name and/or label."""
    try:
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

        # Cypher query to get direct neighbors (depth = 1)
        query = f"""
        MATCH (start_node)
        WHERE {where_clause}
        MATCH (start_node)-[r]->(end_node)
        RETURN start_node, labels(start_node) as start_labels, r as rel, end_node, labels(end_node) as end_labels
        LIMIT 200
        """

        result = age.cypher(
            "loot_tables",
            query,
            "start_node agtype, start_labels agtype, rel agtype, end_node agtype, end_labels agtype",
        )
        if not result:
            raise HTTPException(
                status_code=404, detail="No nodes found matching the criteria"
            )

        neighbors = []
        starting_node_data = None

        # Process the results to collect neighbors with relationship info
        for row in result:
            # Get starting node info from first row
            if starting_node_data is None:
                start_node_data = get_dict_from_agtype(row["start_node"])
                start_node_labels = get_dict_from_agtype(row["start_labels"])

                if isinstance(start_node_data, dict):
                    start_id = str(start_node_data.get("id", ""))

                    # Extract label from the returned labels
                    start_label = "Unknown"
                    if start_node_labels and len(start_node_labels) > 0:
                        if isinstance(start_node_labels, str):
                            start_label = start_node_labels.strip('[]"')
                        elif (
                            isinstance(start_node_labels, list)
                            and len(start_node_labels) > 0
                        ):
                            start_label = str(start_node_labels[0])

                    starting_node_data = GraphNode(
                        id=start_id,
                        name=start_node_data.get("properties", {}).get(
                            "name", "Unknown"
                        ),
                        type=start_label,
                        label=start_label,
                        properties=start_node_data.get("properties", {}),
                    )

            end_node_data = get_dict_from_agtype(row["end_node"])
            end_node_labels = get_dict_from_agtype(row["end_labels"])
            rel_data = get_dict_from_agtype(row["rel"])

            # Add neighbor node
            if isinstance(end_node_data, dict):
                end_id = str(end_node_data.get("id"))

                # Extract label from the returned labels
                end_label = "Unknown"
                if end_node_labels and len(end_node_labels) > 0:
                    if isinstance(end_node_labels, str):
                        end_label = end_node_labels.strip('[]"')
                    elif isinstance(end_node_labels, list) and len(end_node_labels) > 0:
                        end_label = str(end_node_labels[0])

                # Extract relationship information
                relationship_type = (
                    rel_data.get("label", "Unknown") if rel_data else "Unknown"
                )
                relationship_properties = (
                    rel_data.get("properties", {}) if rel_data else {}
                )

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

        if not starting_node_data:
            raise HTTPException(
                status_code=404, detail="No starting node found matching the criteria"
            )

        return NodeNeighborsResponse(
            starting_node=starting_node_data,
            neighbors=neighbors,
            count=len(neighbors),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get node neighbors: {e}"
        )
    finally:
        age.close()
