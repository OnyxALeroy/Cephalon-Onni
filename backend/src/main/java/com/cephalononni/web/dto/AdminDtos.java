package com.cephalononni.web.dto;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

public final class AdminDtos {

    private AdminDtos() {}

    public record UpdateRoleRequest(@NotBlank String role) {
    }

    public record CreateAdminRequest(
            @NotBlank @Email String email,
            @NotBlank String username,
            @NotBlank String password) {
    }
}
