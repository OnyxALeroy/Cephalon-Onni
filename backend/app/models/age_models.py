from typing import Any, Dict, Optional

from pydantic import BaseModel


class GraphNode(BaseModel):
    id: Optional[str] = None
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
