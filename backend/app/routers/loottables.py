import logging

from database.static.age_helper import AgeDB, get_dict_from_agtype
from fastapi import APIRouter, Depends, HTTPException
from models.age_models import (
    GraphNode,
    NodeNeighbor,
    NodeNeighborsResponse,
    NodeSearchResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/loottables", tags=["loottables"])


def get_age_helper() -> AgeDB:
    try:
        return AgeDB()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize graph connection: {e}"
        )


@router.get("/search/nodes", response_model=NodeSearchResponse)
async def search_nodes_by_name_or_label(
    name: str = "", label: str = "", age: AgeDB = Depends(get_age_helper)
) -> NodeSearchResponse:
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

        # Convert node dicts to GraphNode objects
        graph_nodes = []
        for node in nodes:
            graph_node = GraphNode(
                id=node["id"],
                name=node["name"],
                type=node["label"],  # label is used as type
                label=node["label"],
                properties=node["properties"],
            )
            graph_nodes.append(graph_node)

        return NodeSearchResponse(nodes=graph_nodes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search nodes: {e}")
    finally:
        age.close()


@router.get("/neighbors", response_model=NodeNeighborsResponse)
async def get_node_neighbors(
    name: str = "",
    age: AgeDB = Depends(get_age_helper),
):
    """Get the direct neighbors of a node using name."""
    try:
        if not name:
            raise HTTPException(status_code=400, detail="Name must be provided")

        where_clause = f"start_node.name = '{name}'"
        query = f"""
        MATCH (start_node)
        WHERE {where_clause}
        MATCH (start_node)-[r]->(end_node)
        RETURN start_node, labels(start_node) as start_labels, r as rel, end_node, labels(end_node) as end_labels, 'outgoing' as direction
        LIMIT 100
        UNION ALL
        MATCH (start_node)
        WHERE {where_clause}
        MATCH (start_node)<-[r]-(end_node)
        RETURN start_node, labels(start_node) as start_labels, r as rel, end_node, labels(end_node) as end_labels, 'incoming' as direction
        LIMIT 100
        """

        result = age.cypher(
            "loot_tables",
            query,
            "start_node agtype, start_labels agtype, rel agtype, end_node agtype, end_labels agtype, direction agtype",
        )
        if not result:
            raise HTTPException(
                status_code=404, detail=f"No nodes found matching the criteria: {name}"
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
            direction = row["direction"].strip('"')  # Remove extra quotes from agtype string

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
                    relationship_direction=direction,
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
