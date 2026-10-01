package com.cephalononni.catalog;

import com.cephalononni.catalog.DropTableParser.DropRow;
import com.cephalononni.catalog.DropTableParser.MissionRef;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;

/** Fixture HTML mirrors the real drop-tables page's markup for each section type. */
class DropTableParserTest {

    private static final String HTML = """
            <html><body>
            <h3 id="missionRewards">Missions:</h3>
            <table>
            <tr><th colspan="2">Mercury/Apollodorus (Survival)</th></tr>
            <tr><th colspan="2">Rotation A</th></tr>
            <tr><td>Serration</td><td>Rare (7.69%)</td></tr>
            <tr><th colspan="2">Rotation B</th></tr>
            <tr><td>Serration</td><td>Rare (5.00%)</td></tr>
            <tr><th colspan="2">Venus/Tessera (Capture)</th></tr>
            <tr><td>Serration</td><td>Uncommon (11.06%)</td></tr>
            <tr><th colspan="2">Event: Venus/Vesper (Spy)</th></tr>
            <tr><td>Serration</td><td>Rare (8.60%)</td></tr>
            <tr><td>Serration</td><td>Rare (8.60%)</td></tr>
            </table>
            <h3 id="relicRewards">Relics:</h3>
            <table>
            <tr><th colspan="2">Axi A1 Relic (Intact)</th></tr>
            <tr><td>Nikana Prime Blueprint</td><td>Rare (2.00%)</td></tr>
            <tr class="blank-row"><td class="blank-row" colspan="2"></td></tr>
            <tr><th colspan="2">Axi A1 Relic (Radiant)</th></tr>
            <tr><td>Nikana Prime Blueprint</td><td>Rare (10.00%)</td></tr>
            </table>
            <h3 id="keyRewards">Keys:</h3>
            <table>
            <tr><th colspan="2">Recover The Orokin Archive</th></tr><tr><th colspan="2">Rotation A</th></tr>
            <tr><td>Vitality</td><td>Uncommon (15.18%)</td></tr>
            </table>
            <h3 id="transientRewards">Dynamic Location Rewards:</h3>
            <table>
            <tr><th colspan="2">Arbitrations</th></tr><tr><th>Rotation A</th><td></td></tr>
            <tr><td>Ayatan Sah Sculpture</td><td>Rare (9.00%)</td></tr>
            </table>
            <h3 id="sortieRewards">Sorties:</h3>
            <table><tr><th colspan="2">Sortie</th></tr><tr><td>Forma</td><td>Rare (2.50%)</td></tr></table>
            <h3 id="cetusRewards">Cetus Bounty Rewards:</h3>
            <table><tr><th colspan="3">Level 5 - 15 Cetus Bounty</th></tr><tr><th colspan="3">Rotation A</th></tr>
            <tr><td class="pad-cell"></td><th colspan="2">Stage 2, Stage 3 of 4, and Stage 3 of 5</th></tr>
            <tr><td></td><td>Redirection</td><td>Uncommon (15.49%)</td></tr>
            </table>
            <h3 id="modByAvatar">Mod Drops by Source:</h3>
            <table>
            <tr><th>Scaldra Screamer</th><th colspan="2">Mod Drop Chance: 100.00%</th></tr>
            <tr><td></td><td>Arcane Truculence</td><td>Uncommon (12.50%)</td></tr>
            <tr class="blank-row"><td class="blank-row" colspan="3"></td></tr>
            </table>
            <h3 id="modByDrop">Mod Drops by Mod:</h3>
            <table>
            <tr><th colspan="3">Target Acquired</th></tr>
            <tr><th>Source</th><th>Mod Drop Chance</th><th>Chance</th></tr>
            <tr><td>Tusk Thumper Bull</td><td>15.00%</td><td>Uncommon (12.50%)</td></tr>
            </table>
            </body></html>
            """;

    private final List<DropRow> rows = DropTableParser.parse(HTML);

    private List<DropRow> rowsFor(String item) {
        return rows.stream().filter(r -> r.name().equals(item)).toList();
    }

    @Test
    void anItemDroppingInSeveralMissionsAndRotationsKeepsOneRowEach() {
        // The legacy parser kept one row per item for the whole Missions section.
        assertThat(rowsFor("Serration"))
                .extracting(DropRow::source, DropRow::rotation, DropRow::chance)
                .containsExactly(
                        org.assertj.core.groups.Tuple.tuple("Mercury/Apollodorus (Survival)", "Rotation A", 7.69),
                        org.assertj.core.groups.Tuple.tuple("Mercury/Apollodorus (Survival)", "Rotation B", 5.0),
                        org.assertj.core.groups.Tuple.tuple("Venus/Tessera (Capture)", null, 11.06),
                        org.assertj.core.groups.Tuple.tuple("Event: Venus/Vesper (Spy)", null, 8.6));
    }

    @Test
    void missionHeadersAreParsedForTheMissionsTable() {
        assertThat(rowsFor("Serration").get(0).mission()).isEqualTo(new MissionRef("Mercury", "Apollodorus", "Survival"));
        assertThat(rowsFor("Serration").get(3).mission()).isEqualTo(new MissionRef("Venus", "Vesper", "Spy"));
    }

    @Test
    void relicRewardsAreKeptPerRefinement() {
        // The legacy seeder ignored the whole Relics section.
        assertThat(rowsFor("Nikana Prime Blueprint"))
                .extracting(DropRow::sourceType, DropRow::source, DropRow::rotation, DropRow::chance)
                .containsExactly(
                        org.assertj.core.groups.Tuple.tuple(DropTableParser.RELIC, "Axi A1 Relic", "Intact", 2.0),
                        org.assertj.core.groups.Tuple.tuple(DropTableParser.RELIC, "Axi A1 Relic", "Radiant", 10.0));
    }

    @Test
    void keysDynamicLocationsSortiesAndBountiesParse() {
        assertThat(rowsFor("Vitality")).singleElement()
                .satisfies(r -> {
                    assertThat(r.sourceType()).isEqualTo(DropTableParser.KEY);
                    assertThat(r.source()).isEqualTo("Recover The Orokin Archive");
                    assertThat(r.rotation()).isEqualTo("Rotation A");
                });
        assertThat(rowsFor("Ayatan Sah Sculpture")).singleElement()
                .satisfies(r -> assertThat(r.rotation()).isEqualTo("Rotation A"));
        assertThat(rowsFor("Forma")).singleElement()
                .satisfies(r -> assertThat(r.source()).isEqualTo("Sortie"));
        assertThat(rowsFor("Redirection")).singleElement()
                .satisfies(r -> {
                    assertThat(r.sourceType()).isEqualTo(DropTableParser.BOUNTY);
                    assertThat(r.source()).isEqualTo("Cetus Bounty Rewards Level 5 - 15 Cetus Bounty");
                    assertThat(r.rotation()).isEqualTo("Rotation A (Stage 2, Stage 3 of 4, and Stage 3 of 5)");
                    assertThat(r.chance()).isEqualTo(15.49);
                });
    }

    @Test
    void dropsBySourceAreParsedAndTheInvertedByDropTablesAreSkipped() {
        assertThat(rowsFor("Arcane Truculence")).singleElement()
                .satisfies(r -> assertThat(r.source()).isEqualTo("Scaldra Screamer (100.00%)"));
        // The legacy parser turned "Drops by Mod" rows into items named "15.00%".
        assertThat(rows).noneMatch(r -> r.name().endsWith("%") || r.source().contains("Tusk Thumper"));
    }
}
