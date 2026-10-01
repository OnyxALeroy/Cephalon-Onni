package com.cephalononni.catalog;

import com.cephalononni.catalog.DropTableParser.DropRow;
import com.cephalononni.web.dto.CatalogDtos.TableCounts;
import com.cephalononni.web.dto.CatalogDtos.TablePreview;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.TextNode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.sql.Array;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Types;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.function.Predicate;
import java.util.stream.Collectors;

/**
 * Writes one {@link CatalogPayload} to the static catalog tables as a full sync, in a single
 * transaction: every table is upserted by unique_name, rows that vanished upstream are deleted,
 * and drop_sources (no natural key) is replaced wholesale. Any failure rolls everything back.
 *
 * Column mappings follow the legacy seeder's init_*.py files, with its bugs fixed: JSON columns
 * get real JSON (the legacy json.dumps() into SQLAlchemy JSON double-encoded them as strings),
 * integer columns are rounded (ExportWeapons ships totalDamage values like 45.999996, which the
 * legacy asyncpg insert rejected - rolling back the whole weapons table), and rows without a
 * uniqueName are skipped instead of collapsing into one "" row.
 */
@Service
public class CatalogImporter {

    private static final Logger log = LoggerFactory.getLogger(CatalogImporter.class);
    private static final JsonNodeFactory JSON = JsonNodeFactory.instance;
    private static final int BATCH_SIZE = 1000;
    /** Abort (unless forced) if a table would drop below this fraction of its current rows. */
    static final double MIN_KEPT_FRACTION = 0.5;

    private static final Map<String, String> AMP_COMPONENTS = Map.of(
            "/Barrel/", "Prism",
            "/Chassis/", "Scaffold",
            "/Grip/", "Brace");

    private final JdbcTemplate jdbcTemplate;

    public CatalogImporter(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    private enum ColumnType { TEXT, INT, DOUBLE, BOOL, JSON }

    private record Column(String name, ColumnType type, Function<JsonNode, JsonNode> value) {
    }

    private record Table(String name, String export, Predicate<JsonNode> filter, List<Column> columns) {
    }

    @Transactional
    public List<TableCounts> importCatalog(CatalogPayload payload, boolean force) {
        validate(payload);

        List<TableCounts> counts = new ArrayList<>();
        for (Table table : tables(payload.drops())) {
            counts.add(syncTable(table, payload.exports().get(table.export()), force));
        }
        counts.add(replaceDropSources(payload.drops(), force));
        counts.forEach(c -> log.info("Catalog {}: {} inserted, {} updated, {} deleted, {} skipped",
                c.table(), c.inserted(), c.updated(), c.deleted(), c.skipped()));
        return counts;
    }

    /**
     * Dry run of {@link #importCatalog}: the same validation and per-table row selection, compared
     * against the current row counts, without writing anything. Throws like an import would for an
     * invalid payload.
     */
    @Transactional(readOnly = true)
    public List<TablePreview> preview(CatalogPayload payload) {
        validate(payload);
        List<TablePreview> previews = new ArrayList<>();
        for (Table table : tables(payload.drops())) {
            int incoming = incomingRows(table, payload.exports().get(table.export())).rows().size();
            previews.add(preview(table.name(), countRows(table.name()), incoming));
        }
        previews.add(preview("drop_sources", countRows("drop_sources"), payload.drops().size()));
        return previews;
    }

    private static TablePreview preview(String table, int current, int incoming) {
        return new TablePreview(table, current, incoming, wouldShrinkBelowGuard(current, incoming));
    }

    private int countRows(String table) {
        Integer count = jdbcTemplate.queryForObject("SELECT count(*) FROM " + table, Integer.class);
        return count == null ? 0 : count;
    }

    private static void validate(CatalogPayload payload) {
        for (String export : CatalogPayload.REQUIRED_EXPORTS) {
            JsonNode items = payload.exports().get(export);
            if (items == null || !items.isArray() || items.isEmpty()) {
                throw new CatalogImportException(export + " is missing or empty");
            }
        }
        if (payload.drops().isEmpty()) {
            throw new CatalogImportException("The drop tables page yielded no drop rows (page layout changed?)");
        }
    }

    private record IncomingRows(Map<String, JsonNode> rows, int skipped) {
    }

    /** The table's rows by uniqueName: filtered, blank uniqueNames skipped, last duplicate wins. */
    private static IncomingRows incomingRows(Table table, JsonNode items) {
        Map<String, JsonNode> rows = new LinkedHashMap<>();
        int skipped = 0;
        for (JsonNode item : items) {
            if (!table.filter().test(item)) {
                continue;
            }
            String uniqueName = item.path("uniqueName").asText("");
            if (uniqueName.isBlank()) {
                skipped++;
                continue;
            }
            rows.put(uniqueName, item);
        }
        return new IncomingRows(rows, skipped);
    }

    private TableCounts syncTable(Table table, JsonNode items, boolean force) {
        IncomingRows selected = incomingRows(table, items);
        Map<String, JsonNode> incoming = selected.rows();
        int skipped = selected.skipped();

        Set<String> existing = new HashSet<>(jdbcTemplate.queryForList(
                "SELECT unique_name FROM " + table.name() + " WHERE unique_name IS NOT NULL", String.class));
        guardShrink(table.name(), existing.size(), incoming.size(), force);

        List<Column> columns = table.columns();
        String columnList = columns.stream().map(Column::name).collect(Collectors.joining(", "));
        String placeholders = columns.stream()
                .map(c -> c.type() == ColumnType.JSON ? "?::jsonb" : "?")
                .collect(Collectors.joining(", "));
        String updates = columns.stream()
                .filter(c -> !c.name().equals("unique_name"))
                .map(c -> c.name() + " = EXCLUDED." + c.name())
                .collect(Collectors.joining(", "));
        String sql = "INSERT INTO " + table.name() + " (" + columnList + ") VALUES (" + placeholders + ")"
                + " ON CONFLICT (unique_name) DO UPDATE SET " + updates;

        jdbcTemplate.batchUpdate(sql, List.copyOf(incoming.values()), BATCH_SIZE, (ps, item) -> {
            for (int i = 0; i < columns.size(); i++) {
                bind(ps, i + 1, columns.get(i), columns.get(i).value().apply(item));
            }
        });

        Set<String> vanished = new LinkedHashSet<>(existing);
        vanished.removeAll(incoming.keySet());
        if (!vanished.isEmpty()) {
            jdbcTemplate.update(con -> {
                PreparedStatement ps = con.prepareStatement("DELETE FROM " + table.name() + " WHERE unique_name = ANY(?)");
                Array array = con.createArrayOf("varchar", vanished.toArray());
                ps.setArray(1, array);
                return ps;
            });
        }

        int updated = (int) incoming.keySet().stream().filter(existing::contains).count();
        return new TableCounts(table.name(), incoming.size() - updated, updated, vanished.size(), skipped);
    }

    private TableCounts replaceDropSources(List<DropRow> drops, boolean force) {
        int existingCount = countRows("drop_sources");
        guardShrink("drop_sources", existingCount, drops.size(), force);

        jdbcTemplate.update("DELETE FROM drop_sources");
        jdbcTemplate.batchUpdate(
                "INSERT INTO drop_sources (name, source_type, source, chance, rotation) VALUES (?, ?, ?, ?, ?)"
                        + " ON CONFLICT ON CONSTRAINT uq_drop_sources_name_source_rotation DO NOTHING",
                drops, BATCH_SIZE, (ps, drop) -> {
                    ps.setString(1, drop.name());
                    ps.setString(2, drop.sourceType());
                    ps.setString(3, drop.source());
                    ps.setDouble(4, drop.chance());
                    ps.setString(5, drop.rotation());
                });
        // Replaced wholesale, so there's no per-row insert/update split to report.
        return new TableCounts("drop_sources", drops.size(), 0, existingCount, 0);
    }

    private static boolean wouldShrinkBelowGuard(int existing, int incoming) {
        return existing > 0 && incoming < existing * MIN_KEPT_FRACTION;
    }

    private static void guardShrink(String table, int existing, int incoming, boolean force) {
        if (!force && wouldShrinkBelowGuard(existing, incoming)) {
            throw new CatalogImportException(String.format(
                    "%s would shrink from %d to %d rows; aborting (run with force to apply anyway)",
                    table, existing, incoming));
        }
    }

    private static void bind(PreparedStatement ps, int index, Column column, JsonNode value) throws SQLException {
        boolean missing = value == null || value.isNull() || value.isMissingNode();
        switch (column.type()) {
            case TEXT -> {
                if (missing) {
                    ps.setNull(index, Types.VARCHAR);
                } else {
                    ps.setString(index, value.isTextual() ? value.asText() : value.toString());
                }
            }
            case INT -> {
                if (missing || !value.isNumber()) {
                    ps.setNull(index, Types.INTEGER);
                } else {
                    ps.setInt(index, (int) Math.round(value.asDouble()));
                }
            }
            case DOUBLE -> {
                if (missing || !value.isNumber()) {
                    ps.setNull(index, Types.DOUBLE);
                } else {
                    ps.setDouble(index, value.asDouble());
                }
            }
            case BOOL -> {
                if (missing) {
                    ps.setNull(index, Types.BOOLEAN);
                } else {
                    ps.setBoolean(index, value.asBoolean());
                }
            }
            case JSON -> {
                if (missing) {
                    ps.setNull(index, Types.VARCHAR);
                } else {
                    ps.setString(index, value.toString());
                }
            }
        }
    }

    // --- column helpers: read a field, falling back to the legacy seeder's default ---------------

    private static Column text(String column, String field, String fallback) {
        return new Column(column, ColumnType.TEXT, item -> orDefault(item.get(field), fallback == null ? null : TextNode.valueOf(fallback)));
    }

    private static Column text(String column, String field) {
        return text(column, field, null);
    }

    private static Column integer(String column, String field, Integer fallback) {
        return new Column(column, ColumnType.INT, item -> orDefault(item.get(field), fallback == null ? null : JSON.numberNode(fallback)));
    }

    private static Column decimal(String column, String field, Double fallback) {
        return new Column(column, ColumnType.DOUBLE, item -> orDefault(item.get(field), fallback == null ? null : JSON.numberNode(fallback)));
    }

    private static Column bool(String column, String field, boolean fallback) {
        return new Column(column, ColumnType.BOOL, item -> orDefault(item.get(field), JSON.booleanNode(fallback)));
    }

    /** JSON columns default to [] like the legacy seeder, except where it stored null. */
    private static Column json(String column, String field, boolean emptyArrayIfMissing) {
        return new Column(column, ColumnType.JSON, item -> orDefault(item.get(field), emptyArrayIfMissing ? JSON.arrayNode() : null));
    }

    private static JsonNode orDefault(JsonNode value, JsonNode fallback) {
        return value == null || value.isNull() ? fallback : value;
    }

    private static boolean isAmpPart(JsonNode item) {
        return item.path("uniqueName").asText("").contains("/OperatorAmplifiers/");
    }

    // --- table definitions ------------------------------------------------------------------------

    private List<Table> tables(List<DropRow> drops) {
        Map<String, MissionDrops> missionDrops = missionDrops(drops);
        return List.of(
                new Table("warframes", "ExportWarframes", item -> true, List.of(
                        text("unique_name", "uniqueName"),
                        text("name", "name", ""),
                        text("parent_name", "parentName", ""),
                        text("description", "description", ""),
                        integer("health", "health", 0),
                        integer("shield", "shield", 0),
                        integer("armor", "armor", 0),
                        integer("stamina", "stamina", 0),
                        integer("power", "power", 0),
                        bool("codex_secret", "codexSecret", false),
                        integer("mastery_req", "masteryReq", 0),
                        decimal("sprint_speed", "sprintSpeed", 1.0),
                        text("passive_description", "passiveDescription"),
                        json("exalted", "exalted", true),
                        json("abilities", "abilities", true),
                        text("product_category", "productCategory", "Suits"))),
                new Table("weapons", "ExportWeapons", item -> !isAmpPart(item), List.of(
                        text("unique_name", "uniqueName"),
                        text("name", "name", ""),
                        bool("codex_secret", "codexSecret", false),
                        decimal("critical_chance", "criticalChance", 0.0),
                        decimal("critical_multiplier", "criticalMultiplier", 0.0),
                        json("damage_per_shot", "damagePerShot", true),
                        text("description", "description", ""),
                        decimal("fire_rate", "fireRate", 0.0),
                        integer("mastery_req", "masteryReq", 0),
                        decimal("omega_attenuation", "omegaAttenuation", 0.0),
                        decimal("proc_chance", "procChance", 0.0),
                        text("product_category", "productCategory", ""),
                        integer("total_damage", "totalDamage", 0),
                        decimal("accuracy", "accuracy", null),
                        integer("blocking_angle", "blockingAngle", null),
                        integer("combo_duration", "comboDuration", null),
                        bool("exclude_from_codex", "excludeFromCodex", false),
                        decimal("follow_through", "followThrough", null),
                        integer("heavy_attack_damage", "heavyAttackDamage", null),
                        integer("heavy_slam_attack", "heavySlamAttack", null),
                        integer("heavy_slam_radial_damage", "heavySlamRadialDamage", null),
                        integer("heavy_slam_radius", "heavySlamRadius", null),
                        integer("magazine_size", "magazineSize", null),
                        integer("max_level_cap", "maxLevelCap", null),
                        integer("multishot", "multishot", null),
                        text("noise", "noise"),
                        decimal("prime_omega_attenuation", "primeOmegaAttenuation", null),
                        decimal("range", "range", null),
                        decimal("reload_time", "reloadTime", null),
                        bool("sentinel", "sentinel", false),
                        integer("slam_attack", "slamAttack", null),
                        integer("slam_radial_damage", "slamRadialDamage", null),
                        integer("slam_radius", "slamRadius", null),
                        integer("slide_attack", "slideAttack", null),
                        integer("slot", "slot", null),
                        text("trigger", "trigger"),
                        decimal("wind_up", "windUp", null))),
                new Table("amp_parts", "ExportWeapons", CatalogImporter::isAmpPart, List.of(
                        text("unique_name", "uniqueName"),
                        text("name", "name", ""),
                        text("description", "description", ""),
                        bool("codex_secret", "codexSecret", false),
                        new Column("component_type", ColumnType.TEXT, item -> {
                            String uniqueName = item.path("uniqueName").asText("");
                            return TextNode.valueOf(AMP_COMPONENTS.entrySet().stream()
                                    .filter(e -> uniqueName.contains(e.getKey()))
                                    .map(Map.Entry::getValue)
                                    .findFirst()
                                    .orElse("Unknown"));
                        }))),
                new Table("mods", "ExportUpgrades", item -> true, List.of(
                        text("unique_name", "uniqueName"),
                        text("name", "name", ""),
                        text("polarity", "polarity", ""),
                        text("rarity", "rarity", ""),
                        text("type", "type", ""),
                        text("subtype", "subtype"),
                        bool("codex_secret", "codexSecret", false),
                        integer("base_drain", "baseDrain", 0),
                        integer("fusion_limit", "fusionLimit", 0),
                        text("compat_name", "compatName"),
                        text("mod_set", "modSet"),
                        json("mod_set_values", "modSetValues", true),
                        bool("is_utility", "isUtility", false),
                        json("description", "description", false),
                        json("level_stats", "levelStats", true),
                        json("upgrade_entries", "upgradeEntries", true),
                        json("available_challenges", "availableChallenges", true))),
                missionsTable(missionDrops),
                new Table("relics", "ExportRelicArcane", item -> item.has("relicRewards"), List.of(
                        text("unique_name", "uniqueName"),
                        text("name", "name", ""),
                        bool("codex_secret", "codexSecret", false),
                        text("description", "description", ""),
                        json("relic_rewards", "relicRewards", true))),
                new Table("arcanes", "ExportRelicArcane",
                        item -> !item.has("relicRewards") && (item.has("rarity") || item.has("levelStats")), List.of(
                        text("unique_name", "uniqueName"),
                        text("name", "name", ""),
                        bool("codex_secret", "codexSecret", false),
                        text("rarity", "rarity"),
                        json("level_stats", "levelStats", true))),
                new Table("recipes", "ExportRecipes", item -> true, List.of(
                        text("unique_name", "uniqueName"),
                        integer("build_price", "buildPrice", 0),
                        integer("build_time", "buildTime", 0),
                        integer("skip_build_time_price", "skipBuildTimePrice", 0),
                        bool("consume_on_use", "consumeOnUse", true),
                        integer("num", "num", 1),
                        bool("codex_secret", "codexSecret", false),
                        text("result_type", "resultType", ""),
                        json("ingredients", "ingredients", true))),
                new Table("companions", "ExportSentinels", item -> true, List.of(
                        text("unique_name", "uniqueName"),
                        text("name", "name", ""),
                        text("description", "description", ""),
                        integer("health", "health", 0),
                        integer("shield", "shield", 0),
                        integer("armor", "armor", 0),
                        integer("stamina", "stamina", 0),
                        integer("power", "power", 0),
                        bool("codex_secret", "codexSecret", false),
                        bool("exclude_from_codex", "excludeFromCodex", false),
                        text("product_category", "productCategory", ""))),
                new Table("resources", "ExportResources", item -> true, List.of(
                        text("unique_name", "uniqueName"),
                        text("name", "name", ""),
                        text("description", "description", ""),
                        bool("codex_secret", "codexSecret", false),
                        text("parent_name", "parentName", ""),
                        bool("exclude_from_codex", "excludeFromCodex", false),
                        bool("show_in_inventory", "showInInventory", false),
                        integer("prime_selling_price", "primeSellingPrice", null))),
                new Table("images", "ExportManifest", item -> true, List.of(
                        text("unique_name", "uniqueName"),
                        text("texture_location", "textureLocation", ""))));
    }

    // --- missions: ExportRegions + the drop tables --------------------------------------------------

    /** Drops and mission type(s) for one "System/Node" pair, taken from the drop tables. */
    private record MissionDrops(Set<String> types, ArrayNode drops) {
    }

    /**
     * ExportRegions has no drops, planet or mission type at all (the legacy seeder read keys that
     * don't exist, so missions.drops was always []). Both come from the drop tables' mission
     * headers ("Mercury/Apollodorus (Survival)"), matched on systemName + node name. Nodes that
     * appear with several types (e.g. Skirmish and Caches) keep all of them.
     */
    private static Map<String, MissionDrops> missionDrops(List<DropRow> drops) {
        Map<String, MissionDrops> byNode = new HashMap<>();
        for (DropRow drop : drops) {
            if (drop.mission() == null) {
                continue;
            }
            String key = drop.mission().systemName() + "/" + drop.mission().nodeName();
            MissionDrops entry = byNode.computeIfAbsent(key, k -> new MissionDrops(new LinkedHashSet<>(), JSON.arrayNode()));
            entry.types().add(drop.mission().missionType());
            ObjectNode node = entry.drops().addObject();
            node.put("item", drop.name());
            node.put("chance", drop.chance());
            if (drop.rotation() == null) {
                node.putNull("rotation");
            } else {
                node.put("rotation", drop.rotation());
            }
            node.put("mission_type", drop.mission().missionType());
        }
        return byNode;
    }

    private static Table missionsTable(Map<String, MissionDrops> missionDrops) {
        Function<JsonNode, MissionDrops> dropsFor = item ->
                missionDrops.get(item.path("systemName").asText("") + "/" + item.path("name").asText(""));
        return new Table("missions", "ExportRegions", item -> true, List.of(
                text("unique_name", "uniqueName"),
                text("mission_name", "name", ""),
                text("system_name", "systemName", ""),
                text("planet", "systemName", ""),
                new Column("type", ColumnType.TEXT, item -> {
                    MissionDrops entry = dropsFor.apply(item);
                    return TextNode.valueOf(entry == null ? "" : String.join(" / ", entry.types()));
                }),
                integer("node_type", "nodeType", 0),
                integer("faction_index", "factionIndex", 0),
                integer("mastery_req", "masteryReq", 0),
                integer("min_enemy_level", "minEnemyLevel", 0),
                integer("max_enemy_level", "maxEnemyLevel", 0),
                integer("mission_index", "missionIndex", 0),
                integer("system_index", "systemIndex", 0),
                new Column("drops", ColumnType.JSON, item -> {
                    MissionDrops entry = dropsFor.apply(item);
                    return entry == null ? JSON.arrayNode() : entry.drops();
                })));
    }
}
