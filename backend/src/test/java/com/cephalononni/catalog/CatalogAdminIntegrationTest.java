package com.cephalononni.catalog;

import com.cephalononni.model.UserRole;
import com.cephalononni.repository.AppSettingRepository;
import com.cephalononni.repository.UserRepository;
import jakarta.servlet.http.Cookie;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Primary;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

import static org.assertj.core.api.Assertions.assertThat;
import static org.hamcrest.Matchers.containsString;
import static org.hamcrest.Matchers.hasSize;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/** The admin catalog API: role guard, URL settings (incl. the SSRF guard) and import runs. */
@Testcontainers
@SpringBootTest
@AutoConfigureMockMvc
class CatalogAdminIntegrationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    /** Serves the fixture snapshot, records the URLs it was given, and can be held mid-import. */
    static class StubFetcher implements CatalogFetcher {
        final AtomicReference<CatalogUrls> lastUrls = new AtomicReference<>();
        volatile CountDownLatch gate;
        volatile RuntimeException failure;

        @Override
        public CatalogPayload fetch(CatalogUrls urls) {
            lastUrls.set(urls);
            if (failure != null) {
                throw failure;
            }
            CountDownLatch current = gate;
            if (current != null) {
                try {
                    current.await(10, TimeUnit.SECONDS);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            return CatalogFixtures.payload();
        }
    }

    @TestConfiguration
    static class StubFetcherConfig {
        @Bean
        @Primary
        StubFetcher stubFetcher() {
            return new StubFetcher();
        }
    }

    @Autowired
    private MockMvc mockMvc;
    @Autowired
    private UserRepository userRepository;
    @Autowired
    private AppSettingRepository appSettingRepository;
    @Autowired
    private StubFetcher stubFetcher;

    @BeforeEach
    void resetSettings() {
        appSettingRepository.deleteAll();
        stubFetcher.gate = null;
        stubFetcher.failure = null;
    }

    private Cookie userCookie(String email, boolean admin) throws Exception {
        if (userRepository.findByEmail(email).isEmpty()) {
            mockMvc.perform(post("/api/auth/register")
                            .contentType(MediaType.APPLICATION_JSON)
                            .content("{\"email\":\"" + email + "\",\"username\":\"" + email.split("@")[0]
                                    + "\",\"password\":\"hunter2\"}"))
                    .andExpect(status().isOk());
            if (admin) {
                userRepository.findByEmail(email).ifPresent(user -> {
                    user.setRole(UserRole.ADMINISTRATOR);
                    userRepository.save(user);
                });
            }
        }
        MvcResult result = mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"" + email + "\",\"password\":\"hunter2\"}"))
                .andExpect(status().isOk())
                .andReturn();
        return result.getResponse().getCookie("access_token");
    }

    private Cookie admin() throws Exception {
        return userCookie("catalog-admin@example.com", true);
    }

    private void awaitIdle(Cookie admin) throws Exception {
        for (int i = 0; i < 100; i++) {
            String body = mockMvc.perform(get("/api/admin/catalog/status").cookie(admin))
                    .andReturn().getResponse().getContentAsString();
            if (body.contains("\"running\":false")) {
                return;
            }
            Thread.sleep(100);
        }
        throw new AssertionError("catalog import did not finish");
    }

    @Test
    void catalogAdminEndpointsRequireTheAdministratorRole() throws Exception {
        Cookie tenno = userCookie("catalog-tenno@example.com", false);

        mockMvc.perform(get("/api/admin/catalog/settings").cookie(tenno)).andExpect(status().isForbidden());
        mockMvc.perform(post("/api/admin/catalog/import").cookie(tenno)).andExpect(status().isForbidden());
        mockMvc.perform(get("/api/admin/catalog/settings")).andExpect(status().isUnauthorized());
        mockMvc.perform(get("/api/admin/catalog/settings").cookie(admin())).andExpect(status().isOk());
    }

    @Test
    void settingsShowDefaultsUntilOverriddenAndBlankResets() throws Exception {
        Cookie admin = admin();

        mockMvc.perform(get("/api/admin/catalog/settings").cookie(admin))
                .andExpect(jsonPath("$[0].key").value(CatalogSettingsService.EXPORT_INDEX_URL))
                .andExpect(jsonPath("$[0].overridden").value(false))
                .andExpect(jsonPath("$[0].value").value("https://origin.warframe.com/PublicExport/index_en.txt.lzma"));

        mockMvc.perform(put("/api/admin/catalog/settings").cookie(admin)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"exportIndexUrl\":\"https://1.1.1.1/index_en.txt.lzma\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].value").value("https://1.1.1.1/index_en.txt.lzma"))
                .andExpect(jsonPath("$[0].overridden").value(true))
                .andExpect(jsonPath("$[1].overridden").value(false));

        mockMvc.perform(put("/api/admin/catalog/settings").cookie(admin)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"exportIndexUrl\":\"  \"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].overridden").value(false));
    }

    @Test
    void unsafeUrlsAreRejectedAndNothingIsSaved() throws Exception {
        Cookie admin = admin();
        for (String url : new String[] {"http://1.1.1.1/x", "https://localhost/x", "https://10.0.0.1/x", "nope"}) {
            mockMvc.perform(put("/api/admin/catalog/settings").cookie(admin)
                            .contentType(MediaType.APPLICATION_JSON)
                            .content("{\"exportIndexUrl\":\"https://1.1.1.1/ok\",\"dropTablesUrl\":\"" + url + "\"}"))
                    .andExpect(status().isBadRequest())
                    .andExpect(jsonPath("$.detail").isNotEmpty());
        }
        // The valid exportIndexUrl in the same request must not have been saved either.
        assertThat(appSettingRepository.count()).isZero();
    }

    @Test
    void importUsesTheOverriddenUrlsAndReportsItsOutcome() throws Exception {
        Cookie admin = admin();
        mockMvc.perform(put("/api/admin/catalog/settings").cookie(admin)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"dropTablesUrl\":\"https://1.1.1.1/droptables.html\"}"))
                .andExpect(status().isOk());

        mockMvc.perform(post("/api/admin/catalog/import").cookie(admin)).andExpect(status().isAccepted());
        awaitIdle(admin);

        assertThat(stubFetcher.lastUrls.get().dropTablesUrl()).isEqualTo("https://1.1.1.1/droptables.html");
        assertThat(stubFetcher.lastUrls.get().exportIndexUrl())
                .isEqualTo("https://origin.warframe.com/PublicExport/index_en.txt.lzma");
        mockMvc.perform(get("/api/admin/catalog/status").cookie(admin))
                .andExpect(jsonPath("$.lastRun.success").value(true))
                .andExpect(jsonPath("$.lastRun.trigger").value("admin"))
                .andExpect(jsonPath("$.lastRun.error").doesNotExist())
                .andExpect(jsonPath("$.lastRun.tables", hasSize(12)));
    }

    @Autowired
    private org.springframework.jdbc.core.JdbcTemplate jdbcTemplate;

    @Test
    void checkSourcesReportsCountsAndWritesNothing() throws Exception {
        jdbcTemplate.execute("TRUNCATE warframes, drop_sources");

        mockMvc.perform(post("/api/admin/catalog/check").cookie(admin()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.ok").value(true))
                .andExpect(jsonPath("$.exports.ExportWarframes").value(1))
                .andExpect(jsonPath("$.exports.ExportWeapons").value(4))
                .andExpect(jsonPath("$.dropsByType.mission").value(2))
                .andExpect(jsonPath("$.urls.dropTablesUrl").value("https://www.warframe.com/droptables"))
                .andExpect(jsonPath("$.tables", hasSize(12)));

        assertThat(jdbcTemplate.queryForObject("SELECT count(*) FROM warframes", Integer.class)).isZero();
        assertThat(jdbcTemplate.queryForObject("SELECT count(*) FROM drop_sources", Integer.class)).isZero();
    }

    @Test
    void checkSourcesReportsASourceFailureInsteadOfThrowing() throws Exception {
        stubFetcher.failure = new CatalogImportException("GET https://example.com/x returned HTTP 404");

        mockMvc.perform(post("/api/admin/catalog/check").cookie(admin()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.ok").value(false))
                .andExpect(jsonPath("$.error").value("GET https://example.com/x returned HTTP 404"));
    }

    @Test
    void checkSourcesIsAdminOnly() throws Exception {
        mockMvc.perform(post("/api/admin/catalog/check").cookie(userCookie("check-tenno@example.com", false)))
                .andExpect(status().isForbidden());
    }

    @Test
    void aSecondImportWhileOneIsRunningIsAConflict() throws Exception {
        Cookie admin = admin();
        CountDownLatch gate = new CountDownLatch(1);
        stubFetcher.gate = gate;
        try {
            mockMvc.perform(post("/api/admin/catalog/import").cookie(admin))
                    .andExpect(status().isAccepted())
                    .andExpect(jsonPath("$.running").value(true));
            mockMvc.perform(post("/api/admin/catalog/import?force=true").cookie(admin))
                    .andExpect(status().isConflict())
                    .andExpect(jsonPath("$.detail").value(containsString("already running")));
        } finally {
            gate.countDown();
        }
        awaitIdle(admin);
    }
}
