package com.cephalononni;

import jakarta.servlet.http.Cookie;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

/**
 * End-to-end auth/security flows through the real filter chain: public endpoints, the
 * {"detail": ...} error envelope the frontend parses, cookie-based login, and role rules.
 * These pin the exact 401/403 shapes the frontend's error handling depends on.
 */
@Testcontainers
@SpringBootTest
@AutoConfigureMockMvc
class AuthFlowIntegrationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @Autowired
    private MockMvc mockMvc;

    private MvcResult register(String email, String username) throws Exception {
        return mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"" + email + "\",\"username\":\"" + username
                                + "\",\"password\":\"hunter2\"}"))
                .andExpect(status().isOk())
                .andReturn();
    }

    private Cookie login(String email) throws Exception {
        MvcResult result = mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"" + email + "\",\"password\":\"hunter2\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.email").value(email))
                .andReturn();
        for (Cookie cookie : result.getResponse().getCookies()) {
            if ("access_token".equals(cookie.getName())) {
                return cookie;
            }
        }
        throw new AssertionError("login did not set the access_token cookie");
    }

    @Test
    void healthAndPublicCatalogEndpointsAreOpenWithoutAuthentication() throws Exception {
        mockMvc.perform(get("/health")).andExpect(status().isOk());
        mockMvc.perform(get("/api/warframes")).andExpect(status().isOk());
        mockMvc.perform(get("/api/builds/available/mods")).andExpect(status().isOk());
        mockMvc.perform(get("/api/worldstate")).andExpect(status().isServiceUnavailable());
    }

    @Test
    void registerLoginMeRoundTrip() throws Exception {
        register("round-trip@example.com", "roundtrip");

        Cookie cookie = login("round-trip@example.com");

        mockMvc.perform(get("/api/auth/me").cookie(cookie))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.username").value("roundtrip"))
                .andExpect(jsonPath("$.role").value("Tenno"))
                .andExpect(jsonPath("$.id").isNotEmpty());
    }

    @Test
    void registrationIgnoresAnyClientSuppliedRole() throws Exception {
        // No role field on RegisterRequest: a client trying "role": "Administrator" must not
        // get it (mass-assignment/role-escalation guard), and must still end up as Tenno.
        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"no-escalation@example.com\",\"username\":\"noesc\","
                                + "\"password\":\"hunter2\",\"role\":\"Administrator\"}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.role").value("Tenno"));

        mockMvc.perform(get("/api/admin/users").cookie(login("no-escalation@example.com")))
                .andExpect(status().isForbidden())
                .andExpect(jsonPath("$.detail").value("Administrator access required"));
    }

    @Test
    void registrationRejectsDuplicateEmailAndDuplicateUsername() throws Exception {
        register("duplicate@example.com", "dup-email");

        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"duplicate@example.com\",\"username\":\"other\","
                                + "\"password\":\"hunter2\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.detail").value("Email already used"));

        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"other@example.com\",\"username\":\"dup-email\","
                                + "\"password\":\"hunter2\"}"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.detail").value("Username already used"));
    }

    @Test
    void loginWithWrongPasswordOrUnknownEmailReturnsTheSameGeneric401() throws Exception {
        register("timing@example.com", "timing");
        login("timing@example.com");

        mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"timing@example.com\",\"password\":\"wrong\"}"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.detail").value("Invalid credentials"));

        mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"ghost@example.com\",\"password\":\"hunter2\"}"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.detail").value("Invalid credentials"));
    }

    @Test
    void protectedEndpointsWithoutACookieGetThe401Envelope() throws Exception {
        mockMvc.perform(get("/api/builds"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.detail").value("Not authenticated"));

        mockMvc.perform(get("/api/auth/me"))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.detail").value("Not authenticated"));
    }

    @Test
    void tamperedTokensAreRejectedAsUnauthenticated() throws Exception {
        register("tamper@example.com", "tamper");
        Cookie cookie = login("tamper@example.com");

        mockMvc.perform(get("/api/auth/me").cookie(cookie))
                .andExpect(status().isOk());

        String tampered = cookie.getValue() + "x";
        mockMvc.perform(get("/api/auth/me").cookie(new Cookie("access_token", tampered)))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.detail").value("Not authenticated"));
    }

    @Test
    void loginCookieIsAnHttpOnlyCookie() throws Exception {
        register("cookie-flags@example.com", "cookieflags");

        MvcResult result = mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"email\":\"cookie-flags@example.com\",\"password\":\"hunter2\"}"))
                .andExpect(status().isOk())
                .andReturn();

        String setCookie = result.getResponse().getHeader("Set-Cookie");
        org.assertj.core.api.Assertions.assertThat(setCookie).isNotNull();
        org.assertj.core.api.Assertions.assertThat(setCookie).startsWith("access_token=");
        org.assertj.core.api.Assertions.assertThat(setCookie).contains("HttpOnly");
        org.assertj.core.api.Assertions.assertThat(setCookie).contains("SameSite=Lax");
        org.assertj.core.api.Assertions.assertThat(setCookie).contains("Path=/");
    }

    @Test
    void logoutClearsTheCookie() throws Exception {
        register("logout@example.com", "logout");

        MvcResult result = mockMvc.perform(post("/api/auth/logout"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.message").value("Logged out successfully"))
                .andReturn();

        String setCookie = result.getResponse().getHeader("Set-Cookie");
        org.assertj.core.api.Assertions.assertThat(setCookie).startsWith("access_token=");
        org.assertj.core.api.Assertions.assertThat(setCookie).contains("Max-Age=0");
    }
}
