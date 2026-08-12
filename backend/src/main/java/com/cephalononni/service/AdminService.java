package com.cephalononni.service;

import com.cephalononni.exception.ApiException;
import com.cephalononni.model.User;
import com.cephalononni.model.UserRole;
import com.cephalononni.repository.UserRepository;
import com.cephalononni.web.dto.AdminDtos.CreateAdminRequest;
import com.cephalononni.web.dto.AuthDtos.UserPublic;
import org.springframework.lang.NonNull;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Objects;

@Service
public class AdminService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public AdminService(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    /** Returns every user, ascending by id. */
    public List<UserPublic> listUsers() {
        return userRepository.findAllByOrderByIdAsc().stream().map(AuthService::toPublic).toList();
    }

    /** Sets the target user's role, rejecting self-demotion/self-promotion and unknown role values. */
    @Transactional
    public String updateRole(Long adminId, @NonNull Long targetUserId, String roleWireValue) {
        if (adminId.equals(targetUserId)) {
            throw ApiException.badRequest("Cannot modify your own role");
        }
        UserRole role;
        try {
            role = UserRole.fromWireValue(roleWireValue);
        } catch (IllegalArgumentException e) {
            throw ApiException.badRequest("Invalid role");
        }
        User target = requireUser(targetUserId);
        target.setRole(role);
        userRepository.save(target);
        return "User role updated to " + role.getWireValue();
    }

    /** Deletes the target user, rejecting an admin's attempt to delete their own account. */
    @Transactional
    public void deleteUser(Long adminId, @NonNull Long targetUserId) {
        if (adminId.equals(targetUserId)) {
            throw ApiException.badRequest("Cannot delete your own account");
        }
        userRepository.delete(requireUser(targetUserId));
    }

    /** Looks up a user by id, or throws a 404 {@link ApiException}. */
    @NonNull
    private User requireUser(@NonNull Long targetUserId) {
        User user = userRepository.findById(targetUserId)
                .orElseThrow(() -> ApiException.notFound("User not found"));
        return Objects.requireNonNull(user);
    }

    /** Creates a new user with the ADMINISTRATOR role directly, bypassing normal registration. */
    @Transactional
    public UserPublic createAdmin(CreateAdminRequest request) {
        if (userRepository.existsByEmail(request.email())) {
            throw ApiException.badRequest("User with this email already exists");
        }
        User user = new User();
        user.setEmail(request.email().trim());
        user.setUsername(request.username().trim());
        user.setHashedPassword(passwordEncoder.encode(request.password()));
        user.setRole(UserRole.ADMINISTRATOR);
        user = userRepository.save(user);
        return AuthService.toPublic(user);
    }
}
