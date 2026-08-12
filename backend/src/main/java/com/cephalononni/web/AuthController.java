package com.cephalononni.web;

import com.cephalononni.security.CurrentUser;
import com.cephalononni.security.JwtService;
import com.cephalononni.service.AuthService;
import com.cephalononni.web.dto.AuthDtos.LoginRequest;
import com.cephalononni.web.dto.AuthDtos.MessageResponse;
import com.cephalononni.web.dto.AuthDtos.RegisterRequest;
import com.cephalononni.web.dto.AuthDtos.UserPublic;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseCookie;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.time.Duration;
import java.util.Objects;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private static final String COOKIE_NAME = "access_token";

    private final AuthService authService;
    private final JwtService jwtService;
    private final boolean cookieSecure;

    public AuthController(AuthService authService, JwtService jwtService,
                           @Value("${app.cookie.secure:false}") boolean cookieSecure) {
        this.authService = authService;
        this.jwtService = jwtService;
        this.cookieSecure = cookieSecure;
    }

    /** Creates a new Tenno account. */
    @PostMapping("/register")
    public UserPublic register(@Valid @RequestBody RegisterRequest request) {
        return authService.register(request);
    }

    /** Verifies credentials and sets the httponly access-token cookie, expiring with the JWT itself. */
    @PostMapping("/login")
    public ResponseEntity<UserPublic> login(@RequestBody LoginRequest request) {
        AuthService.LoginResult result = authService.login(request);
        ResponseCookie cookie = ResponseCookie.from(COOKIE_NAME, result.token())
                .httpOnly(true)
                .secure(cookieSecure)
                .sameSite("Lax")
                .path("/")
                .maxAge(Objects.requireNonNull(Duration.ofMinutes(jwtService.getExpirationMinutes())))
                .build();
        return ResponseEntity.ok().header(HttpHeaders.SET_COOKIE, cookie.toString()).body(result.user());
    }

    /** Returns the currently authenticated user, as resolved from the access-token cookie. */
    @GetMapping("/me")
    public UserPublic me(@AuthenticationPrincipal CurrentUser principal) {
        return new UserPublic(String.valueOf(principal.id()), principal.email(), principal.username(), principal.role().getWireValue());
    }

    /** Clears the access-token cookie. */
    @PostMapping("/logout")
    public ResponseEntity<MessageResponse> logout() {
        ResponseCookie cookie = ResponseCookie.from(COOKIE_NAME, "")
                .httpOnly(true)
                .secure(cookieSecure)
                .sameSite("Lax")
                .path("/")
                .maxAge(0)
                .build();
        return ResponseEntity.ok().header(HttpHeaders.SET_COOKIE, cookie.toString())
                .body(new MessageResponse("Logged out successfully"));
    }
}
