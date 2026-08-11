package com.cephalononni.security;

import org.junit.jupiter.api.Test;

import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;

class JwtServiceTest {

    private JwtService newService(String secret) {
        JwtService service = new JwtService(secret, 60);
        service.init();
        return service;
    }

    @Test
    void issuesAndParsesATokenRoundTrip() {
        JwtService service = newService("test-secret-at-least-32-bytes-long-for-hs256");
        String token = service.issueToken(42L);

        Optional<Long> userId = service.parseUserId(token);

        assertThat(userId).contains(42L);
    }

    @Test
    void rejectsATamperedToken() {
        JwtService service = newService("test-secret-at-least-32-bytes-long-for-hs256");
        String token = service.issueToken(42L);
        String tampered = token.substring(0, token.length() - 1) + (token.endsWith("a") ? "b" : "a");

        assertThat(service.parseUserId(tampered)).isEmpty();
    }

    @Test
    void refusesToStartWithNoSecret() {
        JwtService service = new JwtService("", 60);
        assertThrows(IllegalStateException.class, service::init);
    }

    @Test
    void refusesToStartWithATooShortSecret() {
        JwtService service = new JwtService("too-short", 60);
        assertThrows(IllegalStateException.class, service::init);
    }
}
