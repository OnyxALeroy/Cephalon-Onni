import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from models.loot_tables import (
    GraphNode,
    NodeNeighbor,
    NodeNeighborsResponse,
    NodeSearchResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_postgres_session
from repositories.mission_repository import MissionRepository
from repositories.drop_source_repository import DropSourceRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/loottables", tags=["loottables"])


def _parse_json(value):
    if value is None:
        return []
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return []
    return value if isinstance(value, list) else []


@router.get("/search/nodes", response_model=NodeSearchResponse)
async def search_nodes_by_name_or_label(
    name: str = "",
    label: str = "",
    session: AsyncSession = Depends(get_postgres_session),
) -> NodeSearchResponse:
    try:
        nodes = []
        node_id_counter = 0

        if not name and not label:
            return NodeSearchResponse(nodes=[])

        if label:
            if label.lower() in ("missions", "mission"):
                missions = await MissionRepository.search_by_name(
                    session, name, limit=50
                ) if name else await MissionRepository.find_all(session)

                for mission in missions[:50]:
                    drops = _parse_json(mission.drops)
                    for drop in drops:
                        nodes.append(
                            {
                                "id": str(node_id_counter),
                                "name": drop.get("item", ""),
                                "type": "Mission",
                                "label": "Mission",
                                "properties": {
                                    "mission_name": mission.mission_name,
                                    "mission_type": mission.type,
                                    "planet": mission.planet,
                                    "drop_chance": drop.get("chance", ""),
                                    "drop_rotation": drop.get("rotation"),
                                },
                            }
                        )
                        node_id_counter += 1
            else:
                items = await DropSourceRepository.find_by_source_type(
                    session, label, name, limit=50
                )

                for item in items:
                    nodes.append(
                        {
                            "id": str(item.id),
                            "name": item.name,
                            "type": item.source_type,
                            "label": item.source_type,
                            "properties": {
                                "source": item.source,
                                "chance": item.chance,
                                "rotation": item.rotation,
                            },
                        }
                    )
        else:
            if name:
                items = await DropSourceRepository.search_by_name(
                    session, name, limit=25
                )

                for item in items:
                    nodes.append(
                        {
                            "id": str(item.id),
                            "name": item.name,
                            "type": item.source_type,
                            "label": item.source_type,
                            "properties": {
                                "source": item.source,
                                "chance": item.chance,
                                "rotation": item.rotation,
                            },
                        }
                    )

                missions = await MissionRepository.search_by_name(
                    session, name, limit=25
                )

                for mission in missions:
                    drops = _parse_json(mission.drops)
                    for drop in drops:
                        nodes.append(
                            {
                                "id": str(node_id_counter),
                                "name": drop.get("item", ""),
                                "type": "Mission",
                                "label": "Mission",
                                "properties": {
                                    "mission_name": mission.mission_name,
                                    "mission_type": mission.type,
                                    "planet": mission.planet,
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
        logger.error(f"Failed to search nodes: {e}")
        return NodeSearchResponse(nodes=[])


@router.get("/neighbors", response_model=NodeNeighborsResponse)
async def get_node_neighbors(
    name: str = "",
    session: AsyncSession = Depends(get_postgres_session),
):
    if not name:
        raise HTTPException(status_code=400, detail="Name must be provided")

    try:
        starting_node = None
        neighbors = []
        node_id = 0

        drop_sources = await DropSourceRepository.search_by_name(session, name, limit=50)

        if drop_sources:
            drop_source = drop_sources[0]
            starting_node = GraphNode(
                id=str(drop_source.id),
                name=drop_source.name,
                type=drop_source.source_type,
                label=drop_source.source_type,
                properties={
                    "source": drop_source.source,
                    "chance": drop_source.chance,
                    "rotation": drop_source.rotation,
                },
            )

            for ds in drop_sources:
                neighbors.append(
                    NodeNeighbor(
                        id=str(ds.id),
                        name=ds.source,
                        type=ds.source_type,
                        properties={},
                        relationship_type="DROPPED_BY",
                        relationship_properties={
                            "chance": ds.chance,
                            "rotation": ds.rotation,
                        },
                        relationship_direction="incoming",
                    )
                )
        else:
            missions = await MissionRepository.search_by_name(session, name, limit=50)

            for mission in missions:
                drops = mission.drops or []
                for drop in drops:
                    if drop.get("item", "").lower() == name.lower():
                        if starting_node is None:
                            starting_node = GraphNode(
                                id=str(mission.id),
                                name=mission.mission_name,
                                type="Mission",
                                label="Mission",
                                properties={
                                    "mission_type": mission.type,
                                    "planet": mission.planet,
                                },
                            )

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
                for mission in missions:
                    if starting_node is None:
                        starting_node = GraphNode(
                            id=str(mission.id),
                            name=mission.mission_name,
                            type="Mission",
                            label="Mission",
                            properties={
                                "mission_type": mission.type,
                                "planet": mission.planet,
                            },
                        )

                    drops = mission.drops or []
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
                for mission in missions:
                    drops = _parse_json(mission.drops)
                    for drop in drops:
                        if name.lower() in drop.get("item", "").lower():
                            if starting_node is None:
                                starting_node = GraphNode(
                                    id=str(node_id),
                                    name=name,
                                    type="Item",
                                    label="Item",
                                    properties={},
                                )

                            neighbors.append(
                                NodeNeighbor(
                                    id=str(mission.id),
                                    name=mission.mission_name,
                                    type="Mission",
                                    properties={},
                                    relationship_type="DROPPED_BY",
                                    relationship_properties={
                                        "chance": drop.get("chance", ""),
                                        "rotation": drop.get("rotation"),
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
        logger.error(f"Failed to get node neighbors: {e}")
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}"
        )
