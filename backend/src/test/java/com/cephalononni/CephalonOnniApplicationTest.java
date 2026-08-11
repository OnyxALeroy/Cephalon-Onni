package com.cephalononni;

import com.cephalononni.model.Warframe;
import com.cephalononni.repository.WarframeRepository;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Boots the full Spring context against a real Postgres container and lets Flyway run V1 for
 * real - this is exactly the "Testcontainers instead of relying on manual smoke tests to catch
 * entity-mapping issues" gap called out during planning. It would have caught, for example, the
 * catalog tables' Integer-vs-Long id mismatch and the Lombok/JDK annotation-processing failure
 * that manual `mvn compile` runs surfaced during development.
 */
@Testcontainers
@SpringBootTest
class CephalonOnniApplicationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @DynamicPropertySource
    static void redisProperties(DynamicPropertyRegistry registry) {
        // No Redis container here - WorldStateCacheService treats Redis as best-effort and the
        // scheduler is disabled in tests (see src/test/resources/application.yml), so nothing in
        // this test touches it. Left as the default (localhost:6379); Spring Data Redis connects
        // lazily and only on first command.
    }

    @org.springframework.beans.factory.annotation.Autowired
    private WarframeRepository warframeRepository;

    @Test
    void contextLoadsAndFlywayMigratesCleanly() {
        // If V1__init_schema.sql didn't apply cleanly, or an entity didn't validate against the
        // resulting schema (ddl-auto=validate), the context would have failed to start already.
        assertThat(warframeRepository.count()).isZero();
    }

    @Test
    void catalogTableAcceptsAndReturnsARow() {
        Warframe warframe = new Warframe();
        warframe.setUniqueName("/Lotus/Powersuits/Excalibur/Excalibur");
        warframe.setName("Excalibur");
        warframe.setHealth(100);
        warframe.setShield(50);
        warframe.setArmor(65);
        warframe.setStamina(100);
        warframe.setPower(100);
        warframe.setMasteryReq(0);
        warframe.setSprintSpeed(1.0);

        Warframe saved = warframeRepository.save(warframe);

        assertThat(saved.getId()).isNotNull();
        assertThat(warframeRepository.findByUniqueName("/Lotus/Powersuits/Excalibur/Excalibur"))
                .isPresent()
                .get()
                .extracting(Warframe::getName)
                .isEqualTo("Excalibur");
    }
}
