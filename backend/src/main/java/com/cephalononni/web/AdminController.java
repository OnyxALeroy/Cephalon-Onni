package com.cephalononni.web;

import com.cephalononni.security.CurrentUser;
import com.cephalononni.service.AdminService;
import com.cephalononni.web.dto.AdminDtos.CreateAdminRequest;
import com.cephalononni.web.dto.AdminDtos.UpdateRoleRequest;
import com.cephalononni.web.dto.AuthDtos.MessageResponse;
import com.cephalononni.web.dto.AuthDtos.UserPublic;
import jakarta.validation.Valid;
import org.springframework.lang.NonNull;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Guarded by SecurityConfig's `hasRole("ADMINISTRATOR")` on /api/admin/**, not per-method here.
 *
 * Two contract fixes vs. the old backend (see backend-rework-plan.md Phase 3):
 *  - updateRole takes a JSON body {"role": "..."}, not a query parameter - the old FastAPI
 *    handler declared `role: UserRole` as a bare scalar with no Body(...), so FastAPI bound it
 *    as a query param even though the existing frontend (UserManagement.vue) already sends it
 *    as a JSON body. That mismatch meant this endpoint never actually worked end-to-end before.
 *  - createAdmin likewise takes a JSON body instead of query params, for the same reason and
 *    because no frontend call site currently exists for it (nothing to stay bug-compatible with).
 */
@RestController
@RequestMapping("/api/admin")
public class AdminController {

    private final AdminService adminService;

    public AdminController(AdminService adminService) {
        this.adminService = adminService;
    }

    /** Lists every user. {@code search} is accepted for wire compatibility but not applied. */
    @GetMapping("/users")
    public List<UserPublic> listUsers(@RequestParam(required = false) String search) {
        return adminService.listUsers();
    }

    /** Sets a user's role. An admin cannot change their own role. */
    @PutMapping("/users/{userId}/role")
    public MessageResponse updateRole(@AuthenticationPrincipal CurrentUser admin,
                                       @PathVariable @NonNull Long userId,
                                       @Valid @RequestBody UpdateRoleRequest request) {
        return new MessageResponse(adminService.updateRole(admin.id(), userId, request.role()));
    }

    /** Deletes a user. An admin cannot delete their own account. */
    @DeleteMapping("/users/{userId}")
    public MessageResponse deleteUser(@AuthenticationPrincipal CurrentUser admin, @PathVariable @NonNull Long userId) {
        adminService.deleteUser(admin.id(), userId);
        return new MessageResponse("User deleted successfully");
    }

    /** Creates a new user with the ADMINISTRATOR role directly. */
    @PostMapping("/create-admin")
    public UserPublic createAdmin(@Valid @RequestBody CreateAdminRequest request) {
        return adminService.createAdmin(request);
    }
}
