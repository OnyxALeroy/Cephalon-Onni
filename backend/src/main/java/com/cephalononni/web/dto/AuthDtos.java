package com.cephalononni.web.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

/**
 * Auth/user DTOs. Registration always creates a "Tenno" user regardless of any role field the
 * client might send - same rule as the old backend (AuthService.register ignored the incoming
 * role), so RegisterRequest deliberately has no role field at all.
 */
public final class AuthDtos {

    private AuthDtos() {}

    public record RegisterRequest(
            @NotBlank @Email String email,
            @NotBlank String username,
            @NotBlank String password) {
    }

    public record LoginRequest(String email, String password) {
    }

    /**
     * `id` is a String here (Long.toString()), not the raw Postgres bigint - the old backend's
     * Mongo _id was always a hex-string on the wire, and the frontend still treats ids as
     * strings in a couple of places (e.g. useBuilds.ts's `id.startsWith("local_")` check for
     * locally-stored builds) that a raw JSON number would break at runtime.
     */
    public record UserPublic(String id, String email, String username, String role) {
    }

    public record MessageResponse(String message) {
    }
}
