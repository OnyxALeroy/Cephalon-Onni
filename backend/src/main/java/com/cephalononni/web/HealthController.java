package com.cephalononni.web;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

/**
 * Mirrors the old backend's plain `GET /health` (not `/api/health`) - scripts/docker-common.sh's
 * check_service_health() curls this exact path for the backend container's health check.
 */
@RestController
public class HealthController {

    @GetMapping("/health")
    public Map<String, String> health() {
        return Map.of("status", "healthy", "message", "API is running");
    }
}
