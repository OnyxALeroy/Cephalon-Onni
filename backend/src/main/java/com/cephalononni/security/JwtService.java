package com.cephalononni.security;

import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.time.Instant;
import java.util.Date;
import java.util.Objects;

import javax.crypto.SecretKey;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Component;

import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;

/**
 * HS256 JWT issuance/verification. Mirrors the old backend's contract: the only claim carried
 * is `sub` (the user id) plus the standard `exp`; every request re-resolves the user from the DB,
 * so the token itself carries no authorization info beyond identity.
 *
 * The secret MUST come from JWT_SECRET (the old backend hardcoded `"looking cool joker"` in
 * source — see backend-rework-plan.md "Risks"). We fail fast at startup rather than silently
 * falling back to a weak default, so a missing env var is caught in CI/deploy, not at 3am.
 */
@Component
public class JwtService {

    private final String secretRaw;
    private final long expirationMinutes;
    private SecretKey key;

    public JwtService(
            @Value("${app.jwt.secret}") String secretRaw,
            @Value("${app.jwt.expiration-minutes:60}") long expirationMinutes) {
        this.secretRaw = secretRaw;
        this.expirationMinutes = expirationMinutes;
    }

    @PostConstruct
    void init() {
        if (secretRaw == null || secretRaw.isBlank()) {
            throw new IllegalStateException(
                    "JWT_SECRET is not set. Refusing to start with no/weak signing key - "
                            + "set the JWT_SECRET environment variable (>= 32 bytes).");
        }
        byte[] bytes = secretRaw.getBytes(StandardCharsets.UTF_8);
        if (bytes.length < 32) {
            throw new IllegalStateException(
                    "JWT_SECRET is too short for HS256 (" + bytes.length
                            + " bytes; need >= 32). Use a longer random value.");
        }
        this.key = Keys.hmacShaKeyFor(bytes);
    }

    /**
     * Issues a signed HS256 JWT for the given user id: `sub` is the user id, `exp` is
     * {@code expirationMinutes} from now. No other claims are carried.
     */
    @NonNull
    public String issueToken(Long userId) {
        Instant now = Instant.now();
        String token = Jwts.builder()
                .subject(String.valueOf(userId))
                .issuedAt(Date.from(now))
                .expiration(Date.from(now.plus(Duration.ofMinutes(expirationMinutes))))
                .signWith(key)
                .compact();
        return Objects.requireNonNull(token);
    }

    /** Returns the user id from the token's `sub` claim, or empty if missing/expired/invalid. */
    public java.util.Optional<Long> parseUserId(String token) {
        try {
            String sub = Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload()
                    .getSubject();
            if (sub == null || sub.isBlank()) {
                return java.util.Optional.empty();
            }
            return java.util.Optional.of(Long.valueOf(sub));
        } catch (JwtException | NumberFormatException e) {
            return java.util.Optional.empty();
        }
    }

    public long getExpirationMinutes() {
        return expirationMinutes;
    }
}
