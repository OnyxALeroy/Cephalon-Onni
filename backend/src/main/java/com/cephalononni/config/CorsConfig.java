package com.cephalononni.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.List;

/**
 * The old backend ran `allow_origins=["*"]` with credentials implicitly disabled - it only
 * "worked" because both nginx (prod) and the Vite dev server (dev) proxy `/api/*` same-origin,
 * so the browser never actually made a cross-origin request (see backend-rework-plan.md Phase 5
 * - "confirm CORS behaves the same"). We keep that same-origin deployment shape, but configure
 * CORS properly (explicit origins + allowCredentials) rather than a wildcard, since a wildcard
 * origin cannot be combined with credentials at all under the CORS spec.
 */
@Configuration
public class CorsConfig {

    @Value("${app.cors.allowed-origins:http://localhost:3000}")
    private List<String> allowedOrigins;

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.setAllowedOrigins(allowedOrigins);
        configuration.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        configuration.setAllowedHeaders(List.of("*"));
        configuration.setAllowCredentials(true);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
