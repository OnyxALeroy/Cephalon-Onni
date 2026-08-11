package com.cephalononni.web.dto;

import com.fasterxml.jackson.databind.JsonNode;

public final class InventoryDtos {

    private InventoryDtos() {}

    /**
     * Includes itemKey, unlike the old backend's InventoryPublic - there, `item_key` was
     * required by the Pydantic response model but never populated by the service, so this
     * endpoint 500'd on any non-empty inventory. Fixed here rather than ported (see
     * backend-rework-plan.md Phase 3's "fix inconsistencies" spirit).
     */
    public record InventoryItemResponse(
            String id,
            String itemKey,
            String name,
            String type,
            String rarity,
            Integer count,
            Integer rank,
            JsonNode polarity,
            JsonNode extra) {
    }
}
