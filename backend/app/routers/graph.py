from database.static.age_helper import AgeDB
from fastapi import APIRouter, Depends, HTTPException
from models.age_models import (
    CypherRequest,
    GraphEdge,
    GraphNode,
    GraphStats,
    SearchRequest,
)
from typing import List
from datetime import datetime

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
        node_result = age.cypher("loot_tables", node_query)
        total_nodes = node_result[0]["total"] if node_result else 0
        
        # Get total edges  
        edge_query = "MATCH ()-[r]->() RETURN COUNT(r) as total"
        edge_result = age.cypher("loot_tables", edge_query)
        total_edges = edge_result[0]["total"] if edge_result else 0
        
        # Get node types
        types_query = "MATCH (n) RETURN labels(n) as labels, COUNT(n) as count"
        types_result = age.cypher("loot_tables", types_query)
        node_types = {}
        for row in types_result:
            if row["labels"]:
                label = row["labels"][0] if isinstance(row["labels"], list) else row["labels"]
                node_types[label] = row["count"]
        
        return GraphStats(
            totalNodes=total_nodes,
            totalEdges=total_edges,
            nodeTypes=node_types,
            lastUpdated=datetime.now().isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get graph stats: {e}")
    finally:
        age.close()


@router.get("/nodes", response_model=List[GraphNode])
async def get_nodes(age: AgeDB = Depends(get_age_helper), limit: int = 100, offset: int = 0):
    """Get all nodes with pagination."""
    try:
        query = f"MATCH (n) RETURN n SKIP {offset} LIMIT {limit}"
        result = age.cypher("loot_tables", query)
        
        nodes = []
        for row in result:
            node_data = row["n"]
            if isinstance(node_data, dict) and "properties" in node_data:
                nodes.append(GraphNode(
                    id=str(node_data.get("id")),
                    type=node_data.get("labels", ["Unknown"])[0] if node_data.get("labels") else "Unknown",
                    label=node_data.get("labels", ["Unknown"])[0] if node_data.get("labels") else "Unknown",
                    properties=node_data.get("properties", {})
                ))
        
        return nodes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get nodes: {e}")
    finally:
        age.close()


@router.get("/edges", response_model=List[GraphEdge])
async def get_edges(age: AgeDB = Depends(get_age_helper), limit: int = 100, offset: int = 0):
    """Get all edges with pagination."""
    try:
        query = f"MATCH (n)-[r]->(m) RETURN r, n, m SKIP {offset} LIMIT {limit}"
        result = age.cypher("loot_tables", query)
        
        edges = []
        for row in result:
            edge_data = row["r"]
            from_node = row["n"]
            to_node = row["m"]
            
            if isinstance(edge_data, dict):
                from_id = str(from_node.get("id", "")) if isinstance(from_node, dict) else ""
                to_id = str(to_node.get("id", "")) if isinstance(to_node, dict) else ""
                
                edges.append(GraphEdge(
                    id=str(edge_data.get("id")),
                    from_node=from_id,
                    to_node=to_id,
                    relationship_type=edge_data.get("label", "RELATED_TO"),
                    properties=edge_data.get("properties", {})
                ))
        
        return edges
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get edges: {e}")
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
            result = age.cypher("loot_tables", query)
            
            nodes = []
            for row in result:
                node_data = row["n"]
                if isinstance(node_data, dict):
                    nodes.append(GraphNode(
                        id=str(node_data.get("id")),
                        type=node_data.get("labels", ["Unknown"])[0] if node_data.get("labels") else "Unknown",
                        label=node_data.get("labels", ["Unknown"])[0] if node_data.get("labels") else "Unknown",
                        properties=node_data.get("properties", node_data)
                    ))
            
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
        result = age.cypher("loot_tables", request.query)
        return {"results": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to execute Cypher query: {e}")
    finally:
        age.close()


@router.post("/nodes", response_model=GraphNode)
async def create_node(node: GraphNode, age: AgeDB = Depends(get_age_helper)):
    """Create a new node."""
    try:
        # Create node properties
        properties = {"name": node.label, **node.properties}
        
        result = age.create_node(
            graph="loot_tables",
            label=node.type,
            properties=properties,
            return_node=True
        )
        
        if result and result.get("n"):
            created_node = result["n"]
            return GraphNode(
                id=str(created_node.get("id")),
                type=node.type,
                label=node.label,
                properties=properties
            )
        
        raise HTTPException(status_code=500, detail="Failed to create node")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create node: {e}")
    finally:
        age.close()


@router.put("/nodes/{node_id}", response_model=GraphNode)
async def update_node(node_id: str, node: GraphNode, age: AgeDB = Depends(get_age_helper)):
    """Update an existing node."""
    try:
        # Build update query
        set_clauses = []
        for key, value in node.properties.items():
            set_clauses.append(f"n.{key} = '{value}'")
        
        if set_clauses:
            query = f"""
            MATCH (n) WHERE id(n) = {node_id}
            SET {', '.join(set_clauses)}
            RETURN n
            """
            result = age.cypher("loot_tables", query)
            
            if result and result[0].get("n"):
                updated_node = result[0]["n"]
                return GraphNode(
                    id=node_id,
                    type=node.type,
                    label=node.label,
                    properties=node.properties
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
        age.cypher("loot_tables", query)
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
            to_label="Node",    # Generic, would need proper label matching
            to_match={"id": edge.to_node},
            rel_props=edge.properties
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
        age.cypher("loot_tables", query)
        return {"message": "Edge deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete edge: {e}")
    finally:
        age.close()


@router.get("/explore", response_model=dict)
async def explore_graph(age: AgeDB = Depends(get_age_helper)):
    """Get a graph exploration dataset for visualization."""
    try:
        # Get sample nodes and edges for visualization
        nodes_query = "MATCH (n) RETURN n LIMIT 50"
        edges_query = "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100"
        
        nodes_result = age.cypher("loot_tables", nodes_query)
        edges_result = age.cypher("loot_tables", edges_query)
        
        nodes = []
        for row in nodes_result:
            node_data = row["n"]
            if isinstance(node_data, dict):
                nodes.append({
                    "id": str(node_data.get("id")),
                    "label": node_data.get("name", "Unknown"),
                    "type": node_data.get("labels", ["Unknown"])[0] if node_data.get("labels") else "Unknown",
                    "properties": node_data.get("properties", {})
                })
        
        edges = []
        for row in edges_result:
            edge_data = row["r"]
            from_node = row["n"]
            to_node = row["m"]
            
            if isinstance(edge_data, dict):
                from_id = str(from_node.get("id", "")) if isinstance(from_node, dict) else ""
                to_id = str(to_node.get("id", "")) if isinstance(to_node, dict) else ""
                
                edges.append({
                    "id": str(edge_data.get("id")),
                    "source": from_id,
                    "target": to_id,
                    "type": edge_data.get("label", "RELATED_TO"),
                    "properties": edge_data.get("properties", {})
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "totalNodes": len(nodes),
                "totalEdges": len(edges)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to explore graph: {e}")
    finally:
        age.close()