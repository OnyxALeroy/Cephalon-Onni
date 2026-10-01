package com.cephalononni.catalog;

import com.cephalononni.web.dto.CatalogDtos.TableCounts;
import com.cephalononni.web.dto.CatalogDtos.TablePreview;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.jdbc.core.JdbcTemplate;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.util.List;
import java.util.Map;

import static com.cephalononni.catalog.CatalogFixtures.AMP_PART;
import static com.cephalononni.catalog.CatalogFixtures.OTHER_WEAPON;
import static com.cephalononni.catalog.CatalogFixtures.WARFRAME;
import static com.cephalononni.catalog.CatalogFixtures.WEAPON;
import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

/** Full-sync semantics of the importer against a real Postgres (Flyway V1 + V2 schema). */
@Testcontainers
@SpringBootTest
class CatalogImporterIntegrationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @Autowired
    private CatalogImporter importer;
    @Autowired
    private JdbcTemplate jdbc;

    @BeforeEach
    void emptyCatalog() {
        jdbc.execute("TRUNCATE warframes, weapons, amp_parts, mods, missions, relics, arcanes, recipes, "
                + "companions, resources, images, drop_sources");
    }

    private String scalar(String sql) {
        return jdbc.queryForObject(sql, String.class);
    }

    private TableCounts countsFor(List<TableCounts> counts, String table) {
        return counts.stream().filter(c -> c.table().equals(table)).findFirst().orElseThrow();
    }

    @Test
    void jsonColumnsHoldRealJsonNotEncodedStrings() {
        importer.importCatalog(CatalogFixtures.payload(), false);

        assertThat(scalar("SELECT jsonb_typeof(abilities) FROM warframes")).isEqualTo("array");
        assertThat(scalar("SELECT abilities->0->>'abilityName' FROM warframes")).isEqualTo("Slash Dash");
        assertThat(scalar("SELECT jsonb_typeof(damage_per_shot) FROM weapons WHERE unique_name = '" + WEAPON + "'"))
                .isEqualTo("array");
        assertThat(scalar("SELECT jsonb_typeof(level_stats) FROM mods")).isEqualTo("array");
        assertThat(scalar("SELECT jsonb_typeof(relic_rewards) FROM relics")).isEqualTo("array");
        assertThat(scalar("SELECT jsonb_typeof(ingredients) FROM recipes")).isEqualTo("array");
    }

    @Test
    void mapsEveryTableLikeTheLegacySeederWithItsBugsFixed() {
        List<TableCounts> counts = importer.importCatalog(CatalogFixtures.payload(), false);

        // Fractional totalDamage is rounded instead of failing the whole weapons table.
        assertThat(scalar("SELECT total_damage FROM weapons WHERE unique_name = '" + WEAPON + "'")).isEqualTo("46");
        // Amp parts go to amp_parts only; the row without a uniqueName is skipped, not stored as "".
        assertThat(scalar("SELECT component_type FROM amp_parts WHERE unique_name = '" + AMP_PART + "'")).isEqualTo("Prism");
        assertThat(scalar("SELECT count(*) FROM weapons")).isEqualTo("2");
        assertThat(countsFor(counts, "weapons").skipped()).isEqualTo(1);
        // ExportRelicArcane is split into relics and arcanes.
        assertThat(scalar("SELECT count(*) FROM relics")).isEqualTo("1");
        assertThat(scalar("SELECT name FROM arcanes")).isEqualTo("Arcane Guardian");
        assertThat(countsFor(counts, "warframes").inserted()).isEqualTo(1);
    }

    @Test
    void missionsGetPlanetTypeAndDropsFromTheDropTables() {
        importer.importCatalog(CatalogFixtures.payload(), false);

        assertThat(scalar("SELECT planet FROM missions WHERE unique_name = 'SolNode94'")).isEqualTo("Mercury");
        assertThat(scalar("SELECT type FROM missions WHERE unique_name = 'SolNode94'")).isEqualTo("Survival");
        assertThat(scalar("SELECT jsonb_array_length(drops) FROM missions")).isEqualTo("2");
        assertThat(scalar("SELECT drops->0->>'item' FROM missions")).isEqualTo("Serration");
        assertThat(scalar("SELECT drops->1->>'rotation' FROM missions")).isEqualTo("Rotation C");
        // Every (item, source, rotation) survives in drop_sources.
        assertThat(scalar("SELECT count(*) FROM drop_sources WHERE name = 'Serration'")).isEqualTo("3");
    }

    @Test
    void reimportUpdatesChangedRowsAndDeletesVanishedOnes() {
        importer.importCatalog(CatalogFixtures.payload(), false);

        Map<String, String> exports = CatalogFixtures.exports();
        exports.put("ExportWarframes", exports.get("ExportWarframes").replace("\"health\": 270", "\"health\": 300"));
        exports.put("ExportWeapons", """
                [{"uniqueName": "%s", "name": "Braton", "totalDamage": 50},
                 {"uniqueName": "%s", "name": "Pencha Prism"}]""".formatted(WEAPON, AMP_PART));
        List<TableCounts> counts = importer.importCatalog(CatalogFixtures.payload(exports, CatalogFixtures.drops()), false);

        assertThat(scalar("SELECT health FROM warframes WHERE unique_name = '" + WARFRAME + "'")).isEqualTo("300");
        assertThat(scalar("SELECT count(*) FROM weapons WHERE unique_name = '" + OTHER_WEAPON + "'")).isEqualTo("0");
        TableCounts weapons = countsFor(counts, "weapons");
        assertThat(weapons.inserted()).isZero();
        assertThat(weapons.updated()).isEqualTo(1);
        assertThat(weapons.deleted()).isEqualTo(1);
    }

    @Test
    void previewCountsIncomingRowsWithoutWritingAnything() {
        List<TablePreview> preview = importer.preview(CatalogFixtures.payload());

        TablePreview weapons = preview.stream().filter(p -> p.table().equals("weapons")).findFirst().orElseThrow();
        assertThat(weapons.current()).isZero();
        assertThat(weapons.incoming()).isEqualTo(2);
        assertThat(preview).noneMatch(TablePreview::wouldShrinkBelowGuard);
        assertThat(scalar("SELECT count(*) FROM weapons")).isEqualTo("0");
        assertThat(scalar("SELECT count(*) FROM drop_sources")).isEqualTo("0");
    }

    @Test
    void previewFlagsTablesAnImportWouldRefuseToShrink() {
        importer.importCatalog(CatalogFixtures.payload(), false);

        List<TablePreview> preview = importer.preview(
                CatalogFixtures.payload(CatalogFixtures.exports(), CatalogFixtures.drops().subList(0, 1)));

        assertThat(preview).filteredOn(TablePreview::wouldShrinkBelowGuard)
                .extracting(TablePreview::table).containsExactly("drop_sources");
        assertThat(scalar("SELECT count(*) FROM drop_sources")).isEqualTo("4");
    }

    @Test
    void aMissingExportIsRejectedBeforeAnythingIsWritten() {
        Map<String, String> exports = CatalogFixtures.exports();
        exports.remove("ExportRecipes");

        assertThatThrownBy(() -> importer.importCatalog(CatalogFixtures.payload(exports, CatalogFixtures.drops()), false))
                .isInstanceOf(CatalogImportException.class)
                .hasMessageContaining("ExportRecipes");
        assertThat(scalar("SELECT count(*) FROM warframes")).isEqualTo("0");
    }

    @Test
    void aLateFailureRollsBackTablesThatWereAlreadyWritten() {
        importer.importCatalog(CatalogFixtures.payload(), false);

        // warframes is synced first; the drop_sources shrink guard fails last (4 rows -> 1).
        Map<String, String> exports = CatalogFixtures.exports();
        exports.put("ExportWarframes", exports.get("ExportWarframes").replace("\"health\": 270", "\"health\": 999"));
        CatalogPayload shrunk = CatalogFixtures.payload(exports, CatalogFixtures.drops().subList(0, 1));

        assertThatThrownBy(() -> importer.importCatalog(shrunk, false))
                .isInstanceOf(CatalogImportException.class)
                .hasMessageContaining("drop_sources would shrink from 4 to 1");
        assertThat(scalar("SELECT health FROM warframes")).isEqualTo("270");
        assertThat(scalar("SELECT count(*) FROM drop_sources")).isEqualTo("4");

        importer.importCatalog(shrunk, true);
        assertThat(scalar("SELECT health FROM warframes")).isEqualTo("999");
        assertThat(scalar("SELECT count(*) FROM drop_sources")).isEqualTo("1");
    }
}
