package com.cephalononni.web;

import com.cephalononni.exception.ApiException;
import com.cephalononni.service.WorldStateCacheService;
import com.cephalononni.web.dto.WorldstateDtos.WorldState;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/worldstate")
public class WorldstateController {

    private final WorldStateCacheService cacheService;

    public WorldstateController(WorldStateCacheService cacheService) {
        this.cacheService = cacheService;
    }

    @GetMapping
    public WorldState getWorldstate() {
        return cacheService.get().orElseThrow(() -> ApiException.serviceUnavailable("WorldState data not available yet"));
    }
}
