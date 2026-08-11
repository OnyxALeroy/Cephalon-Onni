package com.cephalononni.web.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;
import java.util.Map;

/** Kept graph-node-shaped to match the existing (working, Postgres-backed) frontend contract. */
public final class LoottableDtos {

    private LoottableDtos() {}

    public record GraphNode(String id, String name, String type, String label, Map<String, Object> properties) {
    }

    public record NodeSearchResponse(List<GraphNode> nodes) {
    }

    public record NodeNeighbor(
            String id,
            String name,
            String type,
            Map<String, Object> properties,
            @JsonProperty("relationship_type") String relationshipType,
            @JsonProperty("relationship_properties") Map<String, Object> relationshipProperties,
            @JsonProperty("relationship_direction") String relationshipDirection) {
    }

    public record NodeNeighborsResponse(
            @JsonProperty("starting_node") GraphNode startingNode,
            List<NodeNeighbor> neighbors,
            int count) {
    }
}
