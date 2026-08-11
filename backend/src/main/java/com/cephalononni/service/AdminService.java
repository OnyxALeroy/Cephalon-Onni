package com.cephalononni.service;

import com.cephalononni.exception.ApiException;
import com.cephalononni.model.User;
import com.cephalononni.model.UserRole;
import com.cephalononni.repository.UserRepository;
import com.cephalononni.web.dto.AdminDtos.CreateAdminRequest;
import com.cephalononni.web.dto.AuthDtos.UserPublic;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class AdminService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public AdminService(UserRepository userRepository, PasswordEncoder passwordEncoder) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    public List<UserPublic> listUsers() {
        return userRepository.findAllByOrderByIdAsc().stream().map(AuthService::toPublic).toList();
    }

    @Transactional
    public String updateRole(Long adminId, Long targetUserId, String roleWireValue) {
        if (adminId.equals(targetUserId)) {
            throw ApiException.badRequest("Cannot modify your own role");
        }
        UserRole role;
        try {
            role = UserRole.fromWireValue(roleWireValue);
        } catch (IllegalArgumentException e) {
            throw ApiException.badRequest("Invalid role");
        }
        User target = userRepository.findById(targetUserId)
                .orElseThrow(() -> ApiException.notFound("User not found"));
        target.setRole(role);
        userRepository.save(target);
        return "User role updated to " + role.getWireValue();
    }

    @Transactional
    public void deleteUser(Long adminId, Long targetUserId) {
        if (adminId.equals(targetUserId)) {
            throw ApiException.badRequest("Cannot delete your own account");
        }
        User target = userRepository.findById(targetUserId)
                .orElseThrow(() -> ApiException.notFound("User not found"));
        userRepository.delete(target);
    }

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
