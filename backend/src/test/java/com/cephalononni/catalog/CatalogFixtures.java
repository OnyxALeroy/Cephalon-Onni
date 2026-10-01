package com.cephalononni.catalog;

import com.cephalononni.catalog.DropTableParser.DropRow;
import com.cephalononni.catalog.DropTableParser.MissionRef;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** A tiny but complete catalog snapshot, shaped like the real PublicExport files. */
final class CatalogFixtures {

    static final String WARFRAME = "/Lotus/Powersuits/Excalibur/Excalibur";
    static final String WEAPON = "/Lotus/Weapons/Tenno/Rifle/Braton";
    static final String OTHER_WEAPON = "/Lotus/Weapons/Tenno/Pistol/Lato";
    static final String AMP_PART = "/Lotus/Weapons/Operator/OperatorAmplifiers/Set1/Barrel/Barrel1";

    private static final ObjectMapper MAPPER = new ObjectMapper();

    private CatalogFixtures() {}

    static Map<String, String> exports() {
        Map<String, String> exports = new LinkedHashMap<>();
        exports.put("ExportWarframes", """
                [{"uniqueName": "%s", "name": "Excalibur", "health": 270, "masteryReq": 0,
                  "abilities": [{"abilityName": "Slash Dash"}], "productCategory": "Suits"}]""".formatted(WARFRAME));
        exports.put("ExportWeapons", """
                [{"uniqueName": "%s", "name": "Braton", "totalDamage": 45.999996, "damagePerShot": [7.9, 7.9],
                  "productCategory": "LongGuns", "masteryReq": 0},
                 {"uniqueName": "%s", "name": "Lato", "totalDamage": 20, "productCategory": "Pistols"},
                 {"uniqueName": "%s", "name": "Pencha Prism"},
                 {"name": "No unique name"}]""".formatted(WEAPON, OTHER_WEAPON, AMP_PART));
        exports.put("ExportUpgrades", """
                [{"uniqueName": "/Lotus/Upgrades/Mods/Rifle/WeaponDamageAmountMod", "name": "Serration",
                  "polarity": "AP_ATTACK", "rarity": "UNCOMMON", "baseDrain": 4, "fusionLimit": 10,
                  "description": ["+165% Damage"], "levelStats": [{"stats": ["+15% Damage"]}]}]""");
        exports.put("ExportRegions", """
                [{"uniqueName": "SolNode94", "name": "Apollodorus", "systemName": "Mercury", "nodeType": 0,
                  "missionIndex": 2, "systemIndex": 0, "factionIndex": 2, "minEnemyLevel": 6, "maxEnemyLevel": 11}]""");
        exports.put("ExportRelicArcane", """
                [{"uniqueName": "/Lotus/Types/Game/Projections/T1VoidProjectionA", "name": "Lith A1 Relic",
                  "relicRewards": [{"rewardName": "/Lotus/StoreItems/Types/Items/MiscItems/Forma", "rarity": "COMMON"}]},
                 {"uniqueName": "/Lotus/Upgrades/CosmeticEnhancers/Defensive/ArmourOnDamage", "name": "Arcane Guardian",
                  "rarity": "UNCOMMON", "levelStats": [{"stats": ["+150 Armor"]}]}]""");
        exports.put("ExportRecipes", """
                [{"uniqueName": "/Lotus/Types/Recipes/Weapons/BratonBlueprint", "resultType": "%s",
                  "buildPrice": 1000, "ingredients": [{"ItemType": "/Lotus/Types/Items/MiscItems/Ferrite", "ItemCount": 50}]}]"""
                .formatted(WEAPON));
        exports.put("ExportSentinels", """
                [{"uniqueName": "/Lotus/Types/Sentinels/SentinelPowersuits/TaxonPowerSuit", "name": "Taxon"}]""");
        exports.put("ExportResources", """
                [{"uniqueName": "/Lotus/Types/Items/MiscItems/Ferrite", "name": "Ferrite"}]""");
        exports.put("ExportManifest", """
                [{"uniqueName": "%s", "textureLocation": "/Lotus/Interface/Icons/Excalibur.png"}]""".formatted(WARFRAME));
        return exports;
    }

    static List<DropRow> drops() {
        MissionRef apollodorus = new MissionRef("Mercury", "Apollodorus", "Survival");
        List<DropRow> drops = new ArrayList<>();
        drops.add(new DropRow("Serration", DropTableParser.MISSION, "Mercury/Apollodorus (Survival)", 7.69, "Rotation B", apollodorus));
        drops.add(new DropRow("Serration", DropTableParser.MISSION, "Mercury/Apollodorus (Survival)", 3.76, "Rotation C", apollodorus));
        drops.add(new DropRow("Serration", DropTableParser.KEY, "Recover The Orokin Archive", 2.21, "Rotation A", null));
        drops.add(new DropRow("Forma", DropTableParser.SORTIE, "Sortie", 2.5, null, null));
        return drops;
    }

    static CatalogPayload payload() {
        return payload(exports(), drops());
    }

    static CatalogPayload payload(Map<String, String> exports, List<DropRow> drops) {
        Map<String, JsonNode> parsed = new LinkedHashMap<>();
        exports.forEach((name, json) -> {
            try {
                parsed.put(name, MAPPER.readTree(json));
            } catch (Exception e) {
                throw new IllegalArgumentException(name, e);
            }
        });
        return new CatalogPayload(parsed, drops);
    }
}
