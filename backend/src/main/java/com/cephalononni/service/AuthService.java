package com.cephalononni.service;

import com.cephalononni.exception.ApiException;
import com.cephalononni.model.User;
import com.cephalononni.model.UserRole;
import com.cephalononni.repository.UserRepository;
import com.cephalononni.security.JwtService;
import com.cephalononni.web.dto.AuthDtos.LoginRequest;
import com.cephalononni.web.dto.AuthDtos.RegisterRequest;
import com.cephalononni.web.dto.AuthDtos.UserPublic;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthService(UserRepository userRepository, PasswordEncoder passwordEncoder, JwtService jwtService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    @Transactional
    public UserPublic register(RegisterRequest request) {
        // Same (deliberately loose) check as the old backend: substring presence, not a real
        // email-format validator.
        String email = request.email().trim();
        if (!email.contains("@") || !email.contains(".")) {
            throw ApiException.badRequest("Invalid email format");
        }
        if (userRepository.existsByEmail(email)) {
            throw ApiException.badRequest("Email already used");
        }

        User user = new User();
        user.setEmail(email);
        user.setUsername(request.username().trim());
        user.setHashedPassword(passwordEncoder.encode(request.password()));
        user.setRole(UserRole.TENNO); // registration always creates a Tenno, same as before
        user = userRepository.save(user);

        return toPublic(user);
    }

    public record LoginResult(UserPublic user, String token) {
    }

    public LoginResult login(LoginRequest request) {
        String email = request.email() == null ? "" : request.email();
        String password = request.password() == null ? "" : request.password();

        User user = userRepository.findByEmail(email).orElse(null);
        if (user == null || !passwordEncoder.matches(password, user.getHashedPassword())) {
            throw ApiException.unauthorized("Invalid credentials");
        }
        String token = jwtService.issueToken(user.getId());
        return new LoginResult(toPublic(user), token);
    }

    public static UserPublic toPublic(User user) {
        return new UserPublic(String.valueOf(user.getId()), user.getEmail(), user.getUsername(), user.getRole().getWireValue());
    }
}
