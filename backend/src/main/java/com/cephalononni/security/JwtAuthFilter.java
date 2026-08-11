package com.cephalononni.security;

import com.cephalononni.model.User;
import com.cephalononni.repository.UserRepository;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

/**
 * Stateless JWT auth reading the httponly `access_token` cookie (same name/shape as the old
 * backend). Centralizes what used to be duplicated across dependencies.py / builds.py / several
 * routers inline (see backend-rework-plan.md Phase 3).
 */
@Component
public class JwtAuthFilter extends OncePerRequestFilter {

    private static final String COOKIE_NAME = "access_token";

    private final JwtService jwtService;
    private final UserRepository userRepository;

    public JwtAuthFilter(JwtService jwtService, UserRepository userRepository) {
        this.jwtService = jwtService;
        this.userRepository = userRepository;
    }

    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain filterChain) throws ServletException, IOException {

        if (SecurityContextHolder.getContext().getAuthentication() == null) {
            readCookie(request).ifPresent(token -> jwtService.parseUserId(token).ifPresent(userId -> {
                Optional<User> user = userRepository.findById(userId);
                user.ifPresent(u -> {
                    CurrentUser principal = new CurrentUser(u.getId(), u.getEmail(), u.getUsername(), u.getRole());
                    List<GrantedAuthority> authorities =
                            List.of(new SimpleGrantedAuthority("ROLE_" + u.getRole().name()));
                    var authentication =
                            new UsernamePasswordAuthenticationToken(principal, null, authorities);
                    SecurityContextHolder.getContext().setAuthentication(authentication);
                });
            }));
        }

        filterChain.doFilter(request, response);
    }

    private Optional<String> readCookie(HttpServletRequest request) {
        Cookie[] cookies = request.getCookies();
        if (cookies == null) {
            return Optional.empty();
        }
        for (Cookie cookie : cookies) {
            if (COOKIE_NAME.equals(cookie.getName())) {
                return Optional.ofNullable(cookie.getValue());
            }
        }
        return Optional.empty();
    }
}
