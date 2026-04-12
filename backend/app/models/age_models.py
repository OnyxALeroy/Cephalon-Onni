from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class GraphNode(BaseModel):
    id: Optional[str] = None
    name: str
    type: str
    label: str
    properties: Dict[str, Any]


class GraphEdge(BaseModel):
    id: str
    from_node: str
    to_node: str
    relationship_type: str
    properties: Dict[str, Any]


class NodeNeighbor(BaseModel):
    id: str
    name: str
    type: str
    properties: Dict[str, Any]
    relationship_type: str
    relationship_properties: Dict[str, Any]
    relationship_direction: str


class NodeNeighborsResponse(BaseModel):
    starting_node: GraphNode
    neighbors: List[NodeNeighbor]
    count: int


class NodeSearchResponse(BaseModel):
    nodes: List[GraphNode]


class CypherRequest(BaseModel):
    query: str


class SearchRequest(BaseModel):
    name: Optional[str] = None
    label: Optional[str] = None
