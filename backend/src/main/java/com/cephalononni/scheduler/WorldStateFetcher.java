package com.cephalononni.scheduler;

import java.util.concurrent.atomic.AtomicReference;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.HttpHeaders;
import org.springframework.lang.NonNull;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import com.cephalononni.service.WorldStateCacheService;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Polls the upstream Warframe worldstate feed and refreshes the cache. Uses If-None-Match/ETag
 * against upstream exactly like the old backend's WorldStateFetcher.
 *
 * One deliberate change: the old backend polled every 2 seconds (main.py's
 * `WorldStateFetcher(interval=2)`) and used a Redis lock to stop its 4 uvicorn workers from all
 * hammering upstream at once. Spring Boot here runs as a single process/scheduler, so there's no
 * multi-worker race to guard against, and hitting a third-party API every 2 seconds by default is
 * aggressive enough that we treat it as a bug to fix rather than preserve - default interval is
 * now 60s (app.worldstate.poll-interval-seconds), tune as needed.
 */
@Component
@ConditionalOnProperty(name = "app.worldstate.scheduler-enabled", matchIfMissing = true)
public class WorldStateFetcher {

    private static final Logger log = LoggerFactory.getLogger(WorldStateFetcher.class);

    private final WorldStateCacheService cacheService;
    private final ObjectMapper objectMapper;
    private final RestClient restClient;
    private final AtomicReference<String> lastEtag = new AtomicReference<>();

    public WorldStateFetcher(WorldStateCacheService cacheService, ObjectMapper objectMapper,
            @Value("${app.worldstate.url}") @NonNull String worldstateUrl) {
        this.cacheService = cacheService;
        this.objectMapper = objectMapper;
        this.restClient = RestClient.builder().baseUrl(worldstateUrl).build();
    }

    @Scheduled(fixedDelayString = "${app.worldstate.poll-interval-seconds:60}000", initialDelay = 0)
    public void fetchOnce() {
        try {
            String etagToSend = lastEtag.get();
            restClient.get()
                    .header("If-None-Match", etagToSend == null ? "" : etagToSend)
                    .exchange((request, response) -> {
                        if (response.getStatusCode().value() == 304) {
                            return null; // upstream unchanged, nothing to do
                        }
                        if (!response.getStatusCode().is2xxSuccessful()) {
                            log.warn("Worldstate upstream returned {}", response.getStatusCode());
                            return null;
                        }
                        JsonNode body = objectMapper.readTree(response.getBody());
                        if (!body.has("WorldSeed")) {
                            log.warn("Worldstate upstream payload missing WorldSeed, ignoring");
                            return null;
                        }
                        String etag = response.getHeaders().getFirst(HttpHeaders.ETAG);
                        cacheService.update(body, etag);
                        lastEtag.set(etag);
                        return null;
                    });
        } catch (Exception e) {
            log.warn("Worldstate fetch failed: {}", e.getMessage());
        }
    }
}
