package com.cephalononni.catalog;

import com.cephalononni.catalog.DropTableParser.DropRow;
import com.fasterxml.jackson.databind.JsonNode;

import java.util.List;
import java.util.Map;

/**
 * Everything one import needs, already downloaded and parsed: each required PublicExport as its
 * item array (keyed by export name, e.g. "ExportWarframes"), plus the parsed drop tables.
 */
public record CatalogPayload(Map<String, JsonNode> exports, List<DropRow> drops) {

    public static final List<String> REQUIRED_EXPORTS = List.of(
            "ExportWarframes", "ExportWeapons", "ExportUpgrades", "ExportRegions", "ExportRelicArcane",
            "ExportRecipes", "ExportSentinels", "ExportResources", "ExportManifest");
}
