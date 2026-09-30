package com.cephalononni.scheduler;

import java.time.Duration;
import java.util.concurrent.atomic.AtomicReference;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.HttpHeaders;
import org.springframework.http.ResponseEntity;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
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
 * Differences vs the old backend, deliberate:
 * - the old one polled every 2 seconds with a Redis lock to stop its 4 uvicorn workers from all
 *   hammering upstream at once; Spring Boot here runs as a single process/scheduler, so there is
 *   no multi-worker race, and the default is 10s (app.worldstate.poll-interval-ms), tune as needed;
 * - the persisted etag (DB row of record) is used to seed the in-memory one on the first poll
 *   after a restart, so a restart immediately gets a cheap 304 instead of re-downloading the
 *   full ~1 MB payload;
 * - the HTTP client has explicit connect/read timeouts (the old one used requests' timeout=5;
 *   without them a hung upstream would block the scheduler thread indefinitely).
 */
@Component
@ConditionalOnProperty(name = "app.worldstate.scheduler-enabled", matchIfMissing = true)
public class WorldStateFetcher {

    private static final Logger log = LoggerFactory.getLogger(WorldStateFetcher.class);
    private static final Duration CONNECT_TIMEOUT = Duration.ofSeconds(5);
    private static final Duration READ_TIMEOUT = Duration.ofSeconds(15);

    private final WorldStateCacheService cacheService;
    private final ObjectMapper objectMapper;
    private final RestClient restClient;
    private final AtomicReference<String> lastEtag = new AtomicReference<>();

    public WorldStateFetcher(WorldStateCacheService cacheService, ObjectMapper objectMapper,
            @Value("${app.worldstate.url}") @NonNull String worldstateUrl) {
        this.cacheService = cacheService;
        this.objectMapper = objectMapper;
        SimpleClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory();
        requestFactory.setConnectTimeout(CONNECT_TIMEOUT);
        requestFactory.setReadTimeout(READ_TIMEOUT);
        this.restClient = RestClient.builder()
                .baseUrl(worldstateUrl)
                .requestFactory(requestFactory)
                .build();
    }

    @Scheduled(fixedDelayString = "${app.worldstate.poll-interval-ms:10000}", initialDelay = 0)
    public void fetchOnce() {
        try {
            if (lastEtag.get() == null) {
                seedEtagFromCache();
            }
            String etagToSend = lastEtag.get();
            RestClient.RequestHeadersSpec<?> request = restClient.get();
            if (etagToSend != null && !etagToSend.isBlank()) {
                request = request.header("If-None-Match", etagToSend);
            }
            request.exchange((req, response) -> {
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

    /**
     * Seeds the in-memory etag from the persisted cache so the first conditional request after a
     * restart can get a 304 instead of re-downloading the full payload. Best-effort: on any
     * failure the first poll just downloads the full payload like before.
     */
    private void seedEtagFromCache() {
        try {
            cacheService.persistedEtag()
                    .filter(etag -> etag != null && !etag.isBlank())
                    .ifPresent(lastEtag::set);
        } catch (Exception e) {
            log.debug("Could not seed worldstate etag from cache: {}", e.getMessage());
        }
    }
}
