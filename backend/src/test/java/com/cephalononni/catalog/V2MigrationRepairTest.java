package com.cephalononni.catalog;

import org.flywaydb.core.Flyway;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * V2 unwraps the legacy seeder's double-encoded JSON (a JSONB string holding "[...]") in place,
 * so a database seeded by the Python backend is readable by the Java one before any re-import.
 */
@Testcontainers
class V2MigrationRepairTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    private Flyway flyway(String target) {
        return Flyway.configure()
                .dataSource(postgres.getJdbcUrl(), postgres.getUsername(), postgres.getPassword())
                .locations("classpath:db/migration")
                .target(target)
                .load();
    }

    @Test
    void doubleEncodedJsonIsUnwrappedAndGenuineStringsAreKept() throws Exception {
        flyway("1").migrate();
        try (Connection con = DriverManager.getConnection(postgres.getJdbcUrl(), postgres.getUsername(), postgres.getPassword());
             Statement st = con.createStatement()) {
            // What json.dumps() into a SQLAlchemy JSON column produced:
            st.execute("INSERT INTO warframes (unique_name, abilities, exalted) VALUES "
                    + "('/Legacy', to_jsonb('[{\"abilityName\": \"Slash Dash\"}]'::text), to_jsonb('just text'::text))");

            flyway("2").migrate();

            try (ResultSet rs = st.executeQuery("SELECT jsonb_typeof(abilities), abilities->0->>'abilityName', "
                    + "jsonb_typeof(exalted) FROM warframes WHERE unique_name = '/Legacy'")) {
                assertThat(rs.next()).isTrue();
                assertThat(rs.getString(1)).isEqualTo("array");
                assertThat(rs.getString(2)).isEqualTo("Slash Dash");
                assertThat(rs.getString(3)).isEqualTo("string");
            }
        }
    }
}
