package com.cephalononni.service;

import com.cephalononni.web.dto.WorldstateDtos.*;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Ports parse_worldstate() from backend/app/models/worldstate.py: turns the raw upstream
 * https://api.warframe.com/cdn/worldState.php payload into our WorldState DTO. Field access is
 * deliberately defensive (upstream's shape drifts over time) - every getter below tolerates a
 * missing/null field the same way the Python `dict.get(key, default)` calls did.
 */
@Service
public class WorldStateParser {

    private final ObjectMapper objectMapper;

    public WorldStateParser(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    public WorldState parse(JsonNode ws) {
        Event currentEvent = parseEvent(firstEvent(ws));
        List<Alert> currentAlerts = arrayOf(ws, "Alerts").stream().map(this::parseAlert).toList();
        Sortie sortie = parseSortie(firstOrEmptyObject(ws, "Sorties"));
        List<SyndicateMission> syndicateMissions = arrayOf(ws, "SyndicateMissions").stream()
                .map(this::parseSyndicateMission).toList();
        List<VoidFissure> voidFissures = arrayOf(ws, "ActiveMissions").stream().map(this::parseVoidFissure).toList();
        List<String> globalBoosts = arrayOf(ws, "GlobalUpgrades").stream()
                .map((@NonNull JsonNode n) -> n.asText()).toList();
        List<VoidTrader> voidTraders = arrayOf(ws, "VoidTraders").stream().map(this::parseVoidTrader).toList();
        PrimeResurgence primeResurgence = parsePrimeResurgence(ws.get("PrimeResurgence"));
        List<DailyDeal> dailyDeals = arrayOf(ws, "DailyDeals").stream().map(this::parseDailyDeal).toList();
        List<ConclaveChallenge> pvpModes = arrayOf(ws, "PVPChallengeInstances").stream()
                .map(this::parseConclaveChallenge).toList();
        List<FeaturedDojo> featuredDojos = arrayOf(ws, "FeaturedGuilds").stream().map(this::parseFeaturedDojo).toList();

        double[] projectPct = doubleArrayOf(ws, "ProjectPct");

        return new WorldState(
                text(ws, "WorldSeed", ""),
                intOf(ws, "Version", 0),
                text(ws, "MobileVersion", ""),
                text(ws, "BuildLabel", ""),
                currentEvent,
                currentAlerts,
                sortie,
                syndicateMissions,
                voidFissures,
                globalBoosts,
                voidTraders,
                primeResurgence,
                boolOf(ws, "PrimeTokenAvailability", false),
                dailyDeals,
                pvpModes,
                List.of(projectPct[0], projectPct[1]),
                featuredDojos,
                parseSeasonInfo(objectOf(ws, "SeasonInfo")));
    }

    /** Returns the first entry of the `Events` array, falling back to the singular `Event` field. */
    private JsonNode firstEvent(JsonNode ws) {
        List<JsonNode> events = arrayOf(ws, "Events");
        if (!events.isEmpty()) {
            return events.get(0);
        }
        JsonNode single = ws.get("Event");
        return single != null && !single.isNull() ? single : null;
    }

    private Event parseEvent(JsonNode event) {
        if (event == null) {
            return null;
        }
        List<Message> messages = arrayOf(event, "Messages").stream()
                .map(m -> new Message(text(m, "LanguageCode", ""), text(m, "Message", "")))
                .toList();
        List<Link> links = arrayOf(event, "Links").stream()
                .map(l -> new Link(text(l, "LanguageCode", ""), text(l, "Link", "")))
                .toList();
        return new Event(
                messages,
                boolOf(event, "MobileOnly", false),
                boolOf(event, "Priority", false),
                text(event, "Prop", ""),
                boolOf(event, "Community", false),
                text(event, "Icon", ""),
                text(event, "ImageUrl", ""),
                parseDate(event.get("Date")),
                parseDate(event.get("EventStartDate")),
                parseDate(event.get("EventEndDate")),
                text(event, "EventLiveUrl", ""),
                boolOf(event, "HideEndDateModifier", true),
                links);
    }

    private Alert parseAlert(JsonNode alert) {
        JsonNode mi = objectOf(alert, "MissionInfo");
        MissionInfo missionInfo = new MissionInfo(
                text(mi, "location", ""),
                text(mi, "missionType", ""),
                text(mi, "faction", ""),
                intOf(mi, "difficulty", 0),
                mapOf(mi, "missionReward"),
                text(mi, "levelOverride", ""),
                text(mi, "enemySpec", ""),
                intOf(mi, "minEnemyLevel", 0),
                intOf(mi, "maxEnemyLevel", 0),
                text(mi, "descText", ""),
                intOf(mi, "maxWaveNum", 0));
        return new Alert(parseDate(alert.get("Activation")), parseDate(alert.get("Expiry")), missionInfo,
                text(alert, "Tag", ""), boolOf(alert, "ForceUnlock", false));
    }

    private Sortie parseSortie(JsonNode sortie) {
        List<SortieMission> missions = arrayOf(sortie, "Variants").stream()
                .map(v -> new SortieMission(text(v, "missionType", ""), text(v, "modifierType", ""),
                        text(v, "node", ""), text(v, "tileset", "")))
                .toList();
        return new Sortie(
                parseDate(sortie.get("Activation")), parseDate(sortie.get("Expiry")),
                text(sortie, "Boss", ""), text(sortie, "Reward", ""),
                listOf(sortie, "ExtraDrops"), longOf(sortie, "Seed", 0), missions);
    }

    private SyndicateMission parseSyndicateMission(JsonNode sm) {
        List<OpenWorldMission> jobs = sm.has("Jobs")
                ? arrayOf(sm, "Jobs").stream().map(job -> new OpenWorldMission(
                        text(job, "jobType", ""), intOf(job, "masteryReq", 0),
                        intOf(job, "maxEnemyLevel", 0), intOf(job, "minEnemyLevel", 0),
                        text(job, "rewards", ""), intListOf(job, "xpAmounts"))).toList()
                : null;
        return new SyndicateMission(parseDate(sm.get("Activation")), parseDate(sm.get("Expiry")),
                text(sm, "Tag", ""), listOf(sm, "Nodes"), jobs);
    }

    private VoidFissure parseVoidFissure(JsonNode fissure) {
        return new VoidFissure(parseDate(fissure.get("Activation")), parseDate(fissure.get("Expiry")),
                text(fissure, "MissionType", ""), text(fissure, "Node", ""),
                intOf(fissure, "Region", 0), longOf(fissure, "Seed", 0),
                relicEraFromTier(text(fissure, "Modifier", "")));
    }

    private VoidTrader parseVoidTrader(JsonNode trader) {
        return new VoidTrader(parseDate(trader.get("Activation")), parseDate(trader.get("Expiry")),
                text(trader, "Node", ""), text(trader, "Character", ""));
    }

    private PrimeResurgence parsePrimeResurgence(JsonNode raw) {
        if (raw == null || raw.isNull()) {
            return null;
        }
        JsonNode pr = raw.isArray() ? (raw.size() > 0 ? raw.get(0) : null) : raw;
        if (pr == null) {
            return null;
        }
        List<PrimeResurgenceItem> manifest = arrayOf(pr, "Manifest").stream()
                .map(pi -> new PrimeResurgenceItem(text(pi, "ItemType", ""), intOf(pi, "PrimePrice", 0))).toList();
        List<PrimeResurgenceItem> evergreen = arrayOf(pr, "EvergreenManifest").stream()
                .map(pi -> new PrimeResurgenceItem(text(pi, "ItemType", ""), intOf(pi, "PrimePrice", 0))).toList();
        List<PrimeResurgenceScheduleInfo> scheduleInfo = arrayOf(pr, "ScheduleInfo").stream()
                .map(info -> new PrimeResurgenceScheduleInfo(parseDate(info.get("Expiry")),
                        text(info, "FeaturedItem", ""), parseDate(info.get("PreviewHiddenUntil")))).toList();
        return new PrimeResurgence(parseDate(pr.get("Activation")), parseDate(pr.get("Expiry")),
                text(pr, "Node", ""), parseDate(pr.get("InitialStartDate")), manifest, evergreen, scheduleInfo);
    }

    private DailyDeal parseDailyDeal(JsonNode deal) {
        return new DailyDeal(parseDate(deal.get("Activation")), parseDate(deal.get("Expiry")),
                intOf(deal, "OriginalPrice", 0), intOf(deal, "SalePrice", 0), text(deal, "StoreItem", ""),
                intOf(deal, "AmountSold", 0), intOf(deal, "AmountTotal", 0));
    }

    private ConclaveChallenge parseConclaveChallenge(JsonNode challenge) {
        String pvpMode = text(challenge, "PVPMode", "").replace("PVPMODE_", "").toUpperCase();
        List<String> subChallenges = arrayOf(challenge, "subChallenges").stream()
                .map(sc -> text(sc, "$oid", "")).toList();
        return new ConclaveChallenge(parseDate(challenge.get("startDate")), parseDate(challenge.get("endDate")),
                text(challenge, "Category", ""), pvpMode, text(challenge, "challengeTypeRefID", ""), subChallenges);
    }

    private FeaturedDojo parseFeaturedDojo(JsonNode dojo) {
        JsonNode allianceId = dojo.get("AllianceId");
        Map<String, Boolean> platforms = new LinkedHashMap<>();
        JsonNode platformsNode = dojo.get("HiddenPlatforms");
        if (platformsNode != null && platformsNode.isObject()) {
            // fields() is deprecated in favor of properties() (added Jackson 2.17+, we're on 2.19).
            platformsNode.properties().forEach(e -> platforms.put(e.getKey(), e.getValue().asBoolean()));
        }
        return new FeaturedDojo(
                allianceId != null ? text(allianceId, "$oid", "") : "",
                boolOf(dojo, "Emblem", false), platforms, intOf(dojo, "IconOverride", 0),
                text(dojo, "Name", ""), intOf(dojo, "Tier", 0));
    }

    private SeasonInfo parseSeasonInfo(JsonNode si) {
        List<MissionChallenge> activeChallenges = arrayOf(si, "ActiveChallenges").stream()
                .map(c -> new MissionChallenge(parseDate(c.get("Activation")), text(c, "Challenge", ""),
                        boolOf(c, "Daily", false), parseDate(c.get("Expiry"))))
                .toList();
        return new SeasonInfo(parseDate(si.get("Activation")), parseDate(si.get("Expiry")),
                text(si, "AffiliationTag", ""), text(si, "Params", ""), intOf(si, "Phase", 0),
                intOf(si, "Season", 0), activeChallenges);
    }

    /**
     * Parses a date field from any of the shapes upstream sends: a Mongo extended-JSON object
     * ({@code $numberLong}/{@code $date}), a raw epoch number, or an epoch/ISO-8601 string.
     * Returns null if the field is missing or unrecognized. Ports {@code _parse_date}.
     */
    private Instant parseDate(JsonNode value) {
        if (value == null || value.isNull()) {
            return null;
        }
        if (value.isObject()) {
            if (value.has("$numberLong")) {
                return parseDate(value.get("$numberLong"));
            }
            if (value.has("$date")) {
                return parseDate(value.get("$date"));
            }
            return null;
        }
        if (value.isNumber()) {
            return epochToInstant(value.asDouble());
        }
        if (value.isTextual()) {
            String s = value.asText();
            try {
                return epochToInstant(Double.parseDouble(s));
            } catch (NumberFormatException e) {
                try {
                    return Instant.parse(s);
                } catch (Exception ignored) {
                    return null;
                }
            }
        }
        return null;
    }

    private Instant epochToInstant(double raw) {
        double seconds = raw > 1e12 ? raw / 1000.0 : raw;
        return Instant.ofEpochMilli(Math.round(seconds * 1000));
    }

    private String relicEraFromTier(String tier) {
        return switch (tier) {
            case "VoidT1" -> "Lith";
            case "VoidT2" -> "Meso";
            case "VoidT3" -> "Neo";
            case "VoidT4" -> "Axi";
            case "VoidT5" -> "Requiem";
            case "VoidT6" -> "Omnia";
            default -> null;
        };
    }

    /** Returns the array at `field`, or an empty list if missing/not an array. Mirrors `dict.get(key, default)`. */
    private List<JsonNode> arrayOf(JsonNode node, String field) {
        if (node == null) {
            return List.of();
        }
        JsonNode value = node.get(field);
        if (value == null || !value.isArray()) {
            return List.of();
        }
        List<JsonNode> result = new ArrayList<>();
        value.forEach(result::add);
        return result;
    }

    private JsonNode objectOf(JsonNode node, String field) {
        if (node == null) {
            return objectMapper.createObjectNode();
        }
        JsonNode value = node.get(field);
        return value != null && value.isObject() ? value : objectMapper.createObjectNode();
    }

    private JsonNode firstOrEmptyObject(JsonNode node, String field) {
        JsonNode value = node.get(field);
        if (value == null) {
            return objectMapper.createObjectNode();
        }
        if (value.isArray()) {
            return value.size() > 0 ? value.get(0) : objectMapper.createObjectNode();
        }
        return value.isObject() ? value : objectMapper.createObjectNode();
    }

    private String text(JsonNode node, String field, String fallback) {
        if (node == null) return fallback;
        JsonNode value = node.get(field);
        return value == null || value.isNull() ? fallback : value.asText();
    }

    private int intOf(JsonNode node, String field, int fallback) {
        if (node == null) return fallback;
        JsonNode value = node.get(field);
        return value == null || value.isNull() ? fallback : value.asInt();
    }

    private long longOf(JsonNode node, String field, long fallback) {
        if (node == null) return fallback;
        JsonNode value = node.get(field);
        return value == null || value.isNull() ? fallback : value.asLong();
    }

    private boolean boolOf(JsonNode node, String field, boolean fallback) {
        if (node == null) return fallback;
        JsonNode value = node.get(field);
        return value == null || value.isNull() ? fallback : value.asBoolean();
    }

    private List<Object> listOf(JsonNode node, String field) {
        if (node == null) return List.of();
        JsonNode value = node.get(field);
        if (value == null || !value.isArray()) return List.of();
        return objectMapper.convertValue(value, new TypeReference<List<Object>>() {});
    }

    private List<Integer> intListOf(JsonNode node, String field) {
        if (node == null) return List.of();
        JsonNode value = node.get(field);
        if (value == null || !value.isArray()) return List.of();
        List<Integer> result = new ArrayList<>();
        value.forEach(v -> result.add(v.asInt()));
        return result;
    }

    private Map<String, Object> mapOf(JsonNode node, String field) {
        if (node == null) return Map.of();
        JsonNode value = node.get(field);
        if (value == null || !value.isObject()) return Map.of();
        return objectMapper.convertValue(value, new TypeReference<Map<String, Object>>() {});
    }

    /** Returns the 2-element `[current, max]` pair at `field`, or `[0, 0]` if missing/malformed. */
    private double[] doubleArrayOf(JsonNode node, String field) {
        JsonNode value = node.get(field);
        if (value == null || !value.isArray() || value.size() < 2) {
            return new double[]{0.0, 0.0};
        }
        return new double[]{value.get(0).asDouble(), value.get(1).asDouble()};
    }
}
