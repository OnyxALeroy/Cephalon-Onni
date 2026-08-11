package com.cephalononni.web.dto;

import com.fasterxml.jackson.databind.JsonNode;

public final class WarframeDtos {

    private WarframeDtos() {}

    /**
     * Superset of the old backend's list vs. single-get contracts (list omitted
     * passiveDescription/exalted/abilities) - both endpoints now return every field; extra
     * fields on the list response are harmless to a frontend that reads by name.
     */
    public record WarframeResponse(
            Integer id,
            String uniqueName,
            String name,
            String parentName,
            String description,
            Integer health,
            Integer shield,
            Integer armor,
            Integer stamina,
            Integer power,
            Boolean codexSecret,
            Integer masteryReq,
            Double sprintSpeed,
            String passiveDescription,
            JsonNode exalted,
            JsonNode abilities,
            String productCategory) {
    }

    public record AvailableWarframe(String uniqueName, String name, Integer masteryReq) {
    }

    public record AvailableWeapon(String uniqueName, String name, Integer masteryReq, String productCategory) {
    }

    public record AvailableMod(String uniqueName, String name, String type, String rarity, String polarity) {
    }

    public record AvailableArcane(String uniqueName, String name, String rarity) {
    }
}
