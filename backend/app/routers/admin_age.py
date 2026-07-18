import logging

from database.static.age_helper import AgeDB
from dependencies import get_age_helper
from fastapi import APIRouter, Depends, HTTPException
from models.age_models import (
    CypherRequest,
    GraphEdge,
    GraphNode,
    NodeNeighborsResponse,
    NodeSearchResponse,
    SearchRequest,
)
from repositories.graph_repository import GraphRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin/graph", tags=["graph"])


@router.post("/cypher")
async def execute_cypher(request: CypherRequest, age: AgeDB = Depends(get_age_helper)):
    try:
        repo = GraphRepository(age)
        result = repo.execute_cypher(request.query, "result agtype")
        return {"results": result}
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to execute Cypher query: {e}"
        )


@router.post("/nodes", response_model=GraphNode)
async def create_node(node: GraphNode, age: AgeDB = Depends(get_age_helper)):
    try:
        repo = GraphRepository(age)
        properties = {"name": node.label, **node.properties}
        repo.create_node(label=node.type, properties=properties, return_node=True)

        if properties:
            return GraphNode(
                id=str(properties.get("id", "")),
                name=node.label,
                type=node.type,
                label=node.label,
                properties=properties,
            )

        raise HTTPException(status_code=500, detail="Failed to create node")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create node: {e}")


@router.put("/nodes/{node_id}", response_model=GraphNode)
async def update_node(
    node_id: str, node: GraphNode, age: AgeDB = Depends(get_age_helper)
):
    try:
        repo = GraphRepository(age)
        result = repo.update_node(node_id, node.properties)

        if result:
            return GraphNode(
                id=node_id,
                name=node.label,
                type=node.type,
                label=node.label,
                properties=node.properties,
            )

        raise HTTPException(status_code=404, detail="Node not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update node: {e}")


@router.delete("/nodes/{node_id}")
async def delete_node(node_id: str, age: AgeDB = Depends(get_age_helper)):
    try:
        repo = GraphRepository(age)
        repo.delete_node(node_id)
        return {"message": "Node deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete node: {e}")


@router.post("/edges", response_model=GraphEdge)
async def create_edge(edge: GraphEdge, age: AgeDB = Depends(get_age_helper)):
    try:
        repo = GraphRepository(age)
        repo.create_relationship(
            from_label="Node",
            from_match={"id": edge.from_node},
            rel_type=edge.relationship_type,
            to_label="Node",
            to_match={"id": edge.to_node},
            rel_props=edge.properties,
        )
        return edge
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create edge: {e}")


@router.delete("/edges/{edge_id}")
async def delete_edge(edge_id: str, age: AgeDB = Depends(get_age_helper)):
    try:
        repo = GraphRepository(age)
        repo.delete_edge(edge_id)
        return {"message": "Edge deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete edge: {e}")


@router.post("/search", response_model=NodeSearchResponse)
async def search_nodes(request: SearchRequest, age: AgeDB = Depends(get_age_helper)):
    try:
        repo = GraphRepository(age)
        rows = repo.search_nodes_raw(name=request.query, label="", limit=50)

        nodes = []
        for row in rows:
            parsed = GraphRepository.parse_node_from_row(row)
            if parsed:
                nodes.append(parsed)

        return NodeSearchResponse(nodes=nodes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search nodes: {e}")


@router.get("/search/nodes", response_model=NodeSearchResponse)
async def search_nodes_by_name_or_label(
    name: str = "", label: str = "", age: AgeDB = Depends(get_age_helper)
):
    try:
        if not name and not label:
            raise HTTPException(
                status_code=400, detail="At least name or label must be provided"
            )

        repo = GraphRepository(age)
        rows = repo.search_nodes_raw(name=name, label=label, limit=50)

        nodes = []
        for row in rows:
            parsed = GraphRepository.parse_node_from_row(row)
            if parsed:
                nodes.append(
                    {
                        "id": parsed.id,
                        "name": parsed.name,
                        "label": parsed.label,
                        "properties": parsed.properties,
                    }
                )

        return NodeSearchResponse(nodes=nodes)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search nodes: {e}")


@router.get("/neighbors", response_model=NodeNeighborsResponse)
async def get_node_neighbors(
    name: str = "",
    label: str = "",
    age: AgeDB = Depends(get_age_helper),
):
    try:
        if not name and not label:
            raise HTTPException(
                status_code=400, detail="At least name or label must be provided"
            )

        repo = GraphRepository(age)
        result = repo.get_neighbors_raw(name=name, label=label, limit=200)

        if not result:
            raise HTTPException(
                status_code=404, detail="No nodes found matching the criteria"
            )

        starting_node, neighbors = GraphRepository.parse_neighbor_rows(result)

        if not starting_node:
            raise HTTPException(
                status_code=404, detail="No starting node found matching the criteria"
            )

        return NodeNeighborsResponse(
            starting_node=starting_node,
            neighbors=neighbors,
            count=len(neighbors),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get node neighbors: {e}"
        )
