from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class GraphNode(BaseModel):
    id: Optional[str] = None
    name: str
    type: str
    label: str
    properties: Dict[str, Any]


class GraphStats(BaseModel):
    totalNodes: int
    totalEdges: int
    nodeTypes: Dict[str, int]
    lastUpdated: str


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
