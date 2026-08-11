package com.cephalononni.service;

import com.cephalononni.exception.ApiException;
import com.cephalononni.model.DropSource;
import com.cephalononni.model.Mission;
import com.cephalononni.repository.DropSourceRepository;
import com.cephalononni.repository.MissionRepository;
import com.cephalononni.web.dto.LoottableDtos.GraphNode;
import com.cephalononni.web.dto.LoottableDtos.NodeNeighbor;
import com.cephalononni.web.dto.LoottableDtos.NodeNeighborsResponse;
import com.cephalononni.web.dto.LoottableDtos.NodeSearchResponse;
import com.fasterxml.jackson.databind.JsonNode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * "SQL-based" loot-table search: this was never backed by a graph DB (Apache AGE was already
 * gone on this branch), it queries `missions`/`drop_sources` directly and synthesizes a
 * graph-node/edge shape in code, purely to keep the existing (working) frontend contract - see
 * backend-rework-plan.md Phase 3 ("LoottableController ... SQL-based, same logic as today").
 */
@Service
public class LoottableService {

    private static final Logger log = LoggerFactory.getLogger(LoottableService.class);

    private final MissionRepository missionRepository;
    private final DropSourceRepository dropSourceRepository;

    public LoottableService(MissionRepository missionRepository, DropSourceRepository dropSourceRepository) {
        this.missionRepository = missionRepository;
        this.dropSourceRepository = dropSourceRepository;
    }

    public NodeSearchResponse searchNodes(String name, String label) {
        String n = name == null ? "" : name.trim();
        String l = label == null ? "" : label.trim();
        if (n.isEmpty() && l.isEmpty()) {
            return new NodeSearchResponse(List.of());
        }

        try {
            AtomicInteger counter = new AtomicInteger(1);
            List<GraphNode> nodes = new ArrayList<>();

            if (!l.isEmpty()) {
                if (l.equalsIgnoreCase("missions") || l.equalsIgnoreCase("mission")) {
                    List<Mission> missions = n.isEmpty()
                            ? missionRepository.findAll()
                            : missionRepository.findByMissionNameContainingIgnoreCase(n, PageRequest.of(0, 50));
                    missions.stream().limit(50).forEach(m -> nodes.addAll(missionDropNodes(m, counter)));
                } else {
                    List<DropSource> rows = n.isEmpty()
                            ? dropSourceRepository.findBySourceTypeIgnoreCase(l, PageRequest.of(0, 50))
                            : dropSourceRepository.findBySourceTypeIgnoreCaseAndNameContainingIgnoreCase(
                                    l, n, PageRequest.of(0, 50));
                    rows.forEach(row -> nodes.add(dropSourceNode(row)));
                }
            } else {
                dropSourceRepository.findByNameContainingIgnoreCase(n, PageRequest.of(0, 25))
                        .forEach(row -> nodes.add(dropSourceNode(row)));
                missionRepository.findByMissionNameContainingIgnoreCase(n, PageRequest.of(0, 25))
                        .forEach(m -> nodes.addAll(missionDropNodes(m, counter)));
            }

            return new NodeSearchResponse(nodes);
        } catch (Exception e) {
            log.warn("Loot-table node search failed for name='{}' label='{}': {}", n, l, e.getMessage());
            return new NodeSearchResponse(List.of());
        }
    }

    public NodeNeighborsResponse neighbors(String name) {
        String n = name == null ? "" : name.trim();
        if (n.isEmpty()) {
            throw ApiException.badRequest("Name must be provided");
        }

        try {
            List<DropSource> dropSourceRows = dropSourceRepository.findByNameContainingIgnoreCase(
                    n, PageRequest.of(0, 50));

            GraphNode startingNode;
            List<NodeNeighbor> neighbors = new ArrayList<>();

            if (!dropSourceRows.isEmpty()) {
                startingNode = dropSourceNode(dropSourceRows.get(0));
                for (DropSource row : dropSourceRows) {
                    neighbors.add(new NodeNeighbor(
                            String.valueOf(row.getId()), row.getSource(), row.getSourceType(), Map.of(),
                            "DROPPED_BY", dropSourceProperties(row), "incoming"));
                }
            } else {
                startingNode = fallbackFromMissions(n, neighbors);
            }

            if (startingNode == null) {
                throw ApiException.notFound("No nodes found matching: " + n);
            }
            return new NodeNeighborsResponse(startingNode, neighbors, neighbors.size());
        } catch (ApiException e) {
            throw e;
        } catch (Exception e) {
            throw ApiException.internal("Database error: " + e.getMessage());
        }
    }

    /** Ports the three sequential fallback passes over `missions` the old handler ran. */
    private GraphNode fallbackFromMissions(String name, List<NodeNeighbor> neighbors) {
        List<Mission> missions = missionRepository.findByMissionNameContainingIgnoreCase(name, PageRequest.of(0, 50));
        if (missions.isEmpty()) {
            return null;
        }
        AtomicInteger counter = new AtomicInteger(1);

        // Pass 1: exact (case-insensitive) match of a drop's item name.
        GraphNode startingNode = null;
        for (Mission mission : missions) {
            for (JsonNode drop : dropsOf(mission)) {
                String item = textOrEmpty(drop, "item");
                if (item.equalsIgnoreCase(name)) {
                    if (startingNode == null) {
                        startingNode = missionNode(mission);
                    }
                    neighbors.add(new NodeNeighbor(
                            String.valueOf(counter.getAndIncrement()), item, "Item", Map.of(),
                            "DROPS", dropProperties(drop), "outgoing"));
                }
            }
        }
        if (startingNode != null) {
            return startingNode;
        }

        // Pass 2: no exact match anywhere - fall back to the first mission, all drops as edges.
        startingNode = missionNode(missions.get(0));
        for (Mission mission : missions) {
            for (JsonNode drop : dropsOf(mission)) {
                neighbors.add(new NodeNeighbor(
                        String.valueOf(counter.getAndIncrement()), textOrEmpty(drop, "item"), "Item", Map.of(),
                        "DROPS", dropProperties(drop), "outgoing"));
            }
        }
        return startingNode;

        // (Pass 3 in the old handler - substring match producing a synthetic Item starting node -
        // is unreachable in practice: pass 2 above always finds a starting node once `missions`
        // is non-empty, and `missions` being empty already returns null before pass 3 would run.
        // Preserved intentionally as dead-code-for-dead-code parity rather than ported.)
    }

    private List<JsonNode> dropsOf(Mission mission) {
        List<JsonNode> result = new ArrayList<>();
        JsonNode drops = mission.getDrops();
        if (drops != null && drops.isArray()) {
            drops.forEach(result::add);
        }
        return result;
    }

    private String textOrEmpty(JsonNode node, String field) {
        JsonNode value = node.get(field);
        return value == null || value.isNull() ? "" : value.asText();
    }

    private GraphNode missionNode(Mission mission) {
        Map<String, Object> properties = new HashMap<>();
        properties.put("mission_type", mission.getType());
        properties.put("planet", mission.getPlanet());
        return new GraphNode(String.valueOf(mission.getId()), mission.getMissionName(), "Mission", "Mission", properties);
    }

    private List<GraphNode> missionDropNodes(Mission mission, AtomicInteger counter) {
        List<GraphNode> nodes = new ArrayList<>();
        for (JsonNode drop : dropsOf(mission)) {
            Map<String, Object> properties = new HashMap<>();
            properties.put("mission_name", mission.getMissionName());
            properties.put("mission_type", mission.getType());
            properties.put("planet", mission.getPlanet());
            properties.put("drop_chance", drop.has("chance") ? drop.get("chance").asDouble() : null);
            properties.put("drop_rotation", drop.has("rotation") ? textOrEmpty(drop, "rotation") : null);
            nodes.add(new GraphNode(String.valueOf(counter.getAndIncrement()), textOrEmpty(drop, "item"),
                    "Mission", "Mission", properties));
        }
        return nodes;
    }

    private GraphNode dropSourceNode(DropSource row) {
        return new GraphNode(String.valueOf(row.getId()), row.getName(), row.getSourceType(), row.getSourceType(),
                dropSourceProperties(row));
    }

    private Map<String, Object> dropSourceProperties(DropSource row) {
        Map<String, Object> properties = new HashMap<>();
        properties.put("source", row.getSource());
        properties.put("chance", row.getChance());
        properties.put("rotation", row.getRotation());
        return properties;
    }

    private Map<String, Object> dropProperties(JsonNode drop) {
        Map<String, Object> properties = new HashMap<>();
        properties.put("chance", drop.has("chance") ? drop.get("chance").asDouble() : null);
        properties.put("rotation", drop.has("rotation") ? textOrEmpty(drop, "rotation") : null);
        return properties;
    }
}
