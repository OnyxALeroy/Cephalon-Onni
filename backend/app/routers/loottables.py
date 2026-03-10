import logging

from fastapi import APIRouter, Depends, HTTPException
from models.age_models import (
    GraphNode,
    NodeNeighbor,
    NodeNeighborsResponse,
    NodeSearchResponse,
)
from pymongo import MongoClient

from dependencies import get_static_db_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/loottables", tags=["loottables"])


@router.get("/search/nodes", response_model=NodeSearchResponse)
async def search_nodes_by_name_or_label(
    name: str = "",
    label: str = "",
    client: MongoClient = Depends(get_static_db_client),
) -> NodeSearchResponse:
    """Search for nodes by name and/or label (type)."""
    try:
        db = client["cephalon_onni"]
        
        nodes = []
        node_id_counter = 0

        if label:
            if label.lower() == "missions" or label.lower() == "mission":
                query = {"mission_name": {"$regex": f".*{name}.*", "$options": "i"}} if name else {}
                for mission in db["missions"].find(query).limit(50):
                    drops = mission.get("drops", [])
                    for drop in drops:
                        nodes.append(
                            {
                                "id": str(node_id_counter),
                                "name": drop.get("item", ""),
                                "type": "Mission",
                                "label": "Mission",
                                "properties": {
                                    "mission_name": mission.get("mission_name", ""),
                                    "mission_type": mission.get("type", ""),
                                    "planet": mission.get("planet", ""),
                                    "drop_chance": drop.get("chance", ""),
                                    "drop_rotation": drop.get("rotation"),
                                },
                            }
                        )
                        node_id_counter += 1
            else:
                query = {"source_type": label.lower()}
                if name:
                    query["name"] = {"$regex": f".*{name}.*", "$options": "i"}
                
                for item in db["drop_sources"].find(query).limit(50):
                    nodes.append(
                        {
                            "id": str(item.get("_id", node_id_counter)),
                            "name": item.get("name", ""),
                            "type": item.get("source_type", "Unknown"),
                            "label": item.get("source_type", "Unknown"),
                            "properties": {
                                "source": item.get("source", ""),
                                "chance": item.get("chance", ""),
                                "rotation": item.get("rotation"),
                            },
                        }
                    )
                    node_id_counter += 1
        else:
            if name:
                name_query = name
                
                for item in db["drop_sources"].find({"name": {"$regex": f".*{name_query}.*", "$options": "i"}}).limit(25):
                    nodes.append(
                        {
                            "id": str(item.get("_id", node_id_counter)),
                            "name": item.get("name", ""),
                            "type": item.get("source_type", "drop_source"),
                            "label": item.get("source_type", "drop_source"),
                            "properties": {
                                "source": item.get("source", ""),
                                "chance": item.get("chance", ""),
                                "rotation": item.get("rotation"),
                            },
                        }
                    )
                    node_id_counter += 1

                for mission in db["missions"].find(
                    {"mission_name": {"$regex": f".*{name_query}.*", "$options": "i"}}
                ).limit(25):
                    drops = mission.get("drops", [])
                    for drop in drops:
                        nodes.append(
                            {
                                "id": str(node_id_counter),
                                "name": drop.get("item", ""),
                                "type": "Mission",
                                "label": "Mission",
                                "properties": {
                                    "mission_name": mission.get("mission_name", ""),
                                    "mission_type": mission.get("type", ""),
                                    "planet": mission.get("planet", ""),
                                    "drop_chance": drop.get("chance", ""),
                                    "drop_rotation": drop.get("rotation"),
                                },
                            }
                        )
                        node_id_counter += 1

        graph_nodes = [
            GraphNode(
                id=node["id"],
                name=node["name"],
                type=node["type"],
                label=node["label"],
                properties=node["properties"],
            )
            for node in nodes
        ]

        return NodeSearchResponse(nodes=graph_nodes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search nodes: {e}")


@router.get("/neighbors", response_model=NodeNeighborsResponse)
async def get_node_neighbors(
    name: str = "",
    client: MongoClient = Depends(get_static_db_client),
):
    """Get the direct neighbors of a node using name."""
    if not name:
        raise HTTPException(status_code=400, detail="Name must be provided")

    try:
        db = client["cephalon_onni"]
        
        starting_node = None
        neighbors = []
        node_id = 0

        drop_sources = list(db["drop_sources"].find({"name": {"$regex": f".*{name}.*", "$options": "i"}}))
        
        if drop_sources:
            for drop_source in drop_sources:
                if starting_node is None:
                    starting_node = GraphNode(
                        id=str(drop_source.get("_id", "")),
                        name=drop_source.get("name", "Unknown"),
                        type=drop_source.get("source_type", "drop_source"),
                        label=drop_source.get("source_type", "drop_source"),
                        properties={
                            "source": drop_source.get("source", ""),
                            "chance": drop_source.get("chance", ""),
                            "rotation": drop_source.get("rotation"),
                        },
                    )

                neighbors.append(
                    NodeNeighbor(
                        id=str(drop_source.get("_id", "")),
                        name=drop_source.get("source", "Unknown"),
                        type=drop_source.get("source_type", "source"),
                        properties={},
                        relationship_type="DROPPED_BY",
                        relationship_properties={},
                        relationship_direction="incoming",
                    )
                )
        else:
            missions = list(db["missions"].find({
                "$or": [
                    {"mission_name": {"$regex": f".*{name}.*", "$options": "i"}},
                    {"drops.item": {"$regex": f".*{name}.*", "$options": "i"}},
                ]
            }))
            
            for mission in missions:
                starting_node = GraphNode(
                    id=str(mission.get("_id", "")),
                    name=mission.get("mission_name", "Unknown"),
                    type="Mission",
                    label="Mission",
                    properties={
                        "mission_type": mission.get("type", ""),
                        "planet": mission.get("planet", ""),
                    },
                )

                drops = mission.get("drops", [])
                for drop in drops:
                    neighbors.append(
                        NodeNeighbor(
                            id=str(node_id),
                            name=drop.get("item", "Unknown"),
                            type="Item",
                            properties={},
                            relationship_type="DROPS",
                            relationship_properties={
                                "chance": drop.get("chance", ""),
                                "rotation": drop.get("rotation"),
                            },
                            relationship_direction="outgoing",
                        )
                    )
                    node_id += 1
            
            if not starting_node:
                for mission in db["missions"].find({"drops.item": {"$regex": f".*{name}.*", "$options": "i"}}):
                    if starting_node is None:
                        starting_node = GraphNode(
                            id=str(mission.get("_id", "")),
                            name=name,
                            type="Item",
                            label="Item",
                            properties={},
                        )
                    
                    matching_drop = next(
                        (d for d in mission.get("drops", []) 
                         if d.get("item", "").lower() == name.lower()),
                        {}
                    )
                    
                    neighbors.append(
                        NodeNeighbor(
                            id=str(mission.get("_id", "")),
                            name=mission.get("mission_name", "Unknown"),
                            type="Mission",
                            properties={},
                            relationship_type="DROPPED_BY",
                            relationship_properties={
                                "chance": matching_drop.get("chance", ""),
                                "rotation": matching_drop.get("rotation"),
                            },
                            relationship_direction="incoming",
                        )
                    )

        if not starting_node:
            raise HTTPException(
                status_code=404, detail=f"No nodes found matching: {name}"
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
