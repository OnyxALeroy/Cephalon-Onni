from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class GraphNode(BaseModel):
    id: Optional[str] = None
    name: str
    type: str
    label: str
    properties: Dict[str, Any]


class GraphEdge(BaseModel):
    id: Optional[str] = None
    from_node: str
    to_node: str
    relationship_type: str
    properties: Dict[str, Any]


class GraphStats(BaseModel):
    totalNodes: int
    totalEdges: int
    nodeTypes: Dict[str, int]
    lastUpdated: str


class SearchRequest(BaseModel):
    query: str
    type: Optional[str] = "all"


class CypherRequest(BaseModel):
    query: str


class NodeSearchResponse(BaseModel):
    nodes: List[GraphNode]


class NodeNeighbor(BaseModel):
    id: str
    name: str
    type: str
    properties: Dict[str, Any]
    relationship_type: str
    relationship_properties: Dict[str, Any]
    relationship_direction: str  # "outgoing" or "incoming"


class NodeNeighborsResponse(BaseModel):
    starting_node: GraphNode
    neighbors: List[NodeNeighbor]
    count: int


class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
