package com.cephalononni.security;

import com.cephalononni.model.UserRole;

/** Authenticated-principal payload attached to the SecurityContext by {@link JwtAuthFilter}. */
public record CurrentUser(Long id, String email, String username, UserRole role) {
}
