package com.cephalononni.service;

import com.cephalononni.web.dto.WorldstateDtos.WorldState;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;

import java.time.Instant;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Unit tests for the defensive parser: the upstream worldstate payload drifts over time, so
 * the contract that matters is "known fields parse correctly, unknown/missing fields default
 * instead of throwing" - which is exactly what the old Python dict.get()-based parser did.
 */
class WorldStateParserTest {

    private final ObjectMapper objectMapper = new ObjectMapper();
    private final WorldStateParser parser = new WorldStateParser(objectMapper);

    @Test
    void parsesKnownFieldsIntoTheWireShape() throws Exception {
        String raw = """
                {
                  "WorldSeed": "seed-42",
                  "Version": 189,
                  "MobileVersion": "1.0",
                  "BuildLabel": "2024.01.01.00.00",
                  "ProjectPct": [111.5, 4.2, 0.0],
                  "Events": [
                    {
                      "Messages": [{"LanguageCode": "en", "Message": "Update!"}],
                      "Links": [{"LanguageCode": "en", "Link": "https://example.com"}],
                      "Date": {"$date": {"$numberLong": "1790000000000"}},
                      "EventStartDate": 1790000000,
                      "EventEndDate": "2030-01-01T00:00:00Z"
                    }
                  ],
                  "Alerts": [
                    {
                      "Activation": {"$date": {"$numberLong": "1790000000000"}},
                      "Expiry": {"$date": {"$numberLong": "1790003600000"}},
                      "MissionInfo": {"location": "Earth/Lith", "missionType": "Capture", "faction": "Grineer"}
                    }
                  ],
                  "ActiveMissions": [
                    {"MissionType": "Sabotage", "Node": "Mithril", "Modifier": "VoidT3", "Activation": 1790000000, "Expiry": "2030-01-01T00:00:00Z"},
                    {"MissionType": "Capture", "Node": "Sirocco", "Modifier": "VoidT9"}
                  ]
                }
                """;

        WorldState worldState = parser.parse(objectMapper.readTree(raw));

        assertThat(worldState.worldSeed()).isEqualTo("seed-42");
        assertThat(worldState.apiVersion()).isEqualTo(189);
        assertThat(worldState.buildLabel()).isEqualTo("2024.01.01.00.00");
        assertThat(worldState.invasionConstructionStatuses()).containsExactly(111.5, 4.2);

        assertThat(worldState.currentEvent()).isNotNull();
        assertThat(worldState.currentEvent().messages()).hasSize(1);
        assertThat(worldState.currentEvent().messages().get(0).message()).isEqualTo("Update!");
        assertThat(worldState.currentEvent().startDate())
                .isEqualTo(Instant.ofEpochMilli(1790000000000L));

        assertThat(worldState.currentAlerts()).hasSize(1);
        assertThat(worldState.currentAlerts().get(0).missionInfo().location()).isEqualTo("Earth/Lith");
        assertThat(worldState.currentAlerts().get(0).activation())
                .isEqualTo(Instant.ofEpochMilli(1790000000000L));

        assertThat(worldState.voidFissures()).hasSize(2);
        // known tier -> era, epoch-seconds activation, ISO-string expiry
        assertThat(worldState.voidFissures().get(0).era()).isEqualTo("Neo");
        assertThat(worldState.voidFissures().get(0).activation())
                .isEqualTo(Instant.ofEpochMilli(1790000000000L));
        assertThat(worldState.voidFissures().get(0).expiry()).isEqualTo(Instant.parse("2030-01-01T00:00:00Z"));
        // unknown tier -> null era instead of failing the whole parse (old backend raised)
        assertThat(worldState.voidFissures().get(1).era()).isNull();
    }

    @Test
    void toleratesAnEmptyOrUnknownPayload() {
        WorldState worldState = parser.parse(objectMapper.createObjectNode());

        assertThat(worldState.worldSeed()).isEmpty();
        assertThat(worldState.apiVersion()).isZero();
        assertThat(worldState.currentEvent()).isNull();
        assertThat(worldState.currentAlerts()).isEmpty();
        assertThat(worldState.voidFissures()).isEmpty();
        assertThat(worldState.invasionConstructionStatuses()).containsExactly(0.0, 0.0);
        assertThat(worldState.sortie()).isNotNull();
        assertThat(worldState.sortie().missions()).isEmpty();
        assertThat(worldState.seasonInfo()).isNotNull();
        assertThat(worldState.seasonInfo().activeChallenges()).isEmpty();
    }

    @Test
    void toleratesAMalformedProjectPct() throws Exception {
        String raw = """
                {"WorldSeed": "seed-42", "ProjectPct": [1.0]}
                """;

        WorldState worldState = parser.parse(objectMapper.readTree(raw));

        // old backend raised IndexError on a short ProjectPct and never cached; this returns the default
        assertThat(worldState.invasionConstructionStatuses()).containsExactly(0.0, 0.0);
    }

    @Test
    void parsesDatesFromEveryUpstreamShape() throws Exception {
        String raw = """
                {
                  "Events": [{
                    "Date": {"$date": {"$numberLong": "1790000000000"}},
                    "EventStartDate": 1790000000000,
                    "EventEndDate": "1790000000"
                  }]
                }
                """;

        WorldState worldState = parser.parse(objectMapper.readTree(raw));

        Instant expected = Instant.ofEpochMilli(1790000000000L);
        assertThat(worldState.currentEvent().date()).isEqualTo(expected);
        assertThat(worldState.currentEvent().startDate()).isEqualTo(expected);
        assertThat(worldState.currentEvent().endDate()).isEqualTo(expected);
    }
}
