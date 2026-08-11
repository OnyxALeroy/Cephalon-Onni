package com.cephalononni.service;

import com.cephalononni.model.WorldstateCache;
import com.cephalononni.repository.WorldstateCacheRepository;
import com.cephalononni.web.dto.WorldstateDtos.WorldState;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.Optional;

/**
 * Redis-first, Postgres-fallback cache for the worldstate poller - mirrors the old backend's
 * Redis keys (worldstate:data / :etag / :fetched_at) and its Mongo `worldstate` doc, now a
 * single-row `worldstate_cache` table (see backend-rework-plan.md Phase 3). Redis is
 * best-effort everywhere, same as before: a Redis outage never surfaces to the API caller.
 */
@Service
public class WorldStateCacheService {

    private static final Logger log = LoggerFactory.getLogger(WorldStateCacheService.class);
    private static final String DATA_KEY = "worldstate:data";
    private static final String ETAG_KEY = "worldstate:etag";
    private static final String FETCHED_AT_KEY = "worldstate:fetched_at";
    private static final Long CACHE_ROW_ID = 1L;

    private final StringRedisTemplate redisTemplate;
    private final WorldstateCacheRepository worldstateCacheRepository;
    private final WorldStateParser parser;
    private final ObjectMapper objectMapper;

    public WorldStateCacheService(StringRedisTemplate redisTemplate,
                                   WorldstateCacheRepository worldstateCacheRepository,
                                   WorldStateParser parser, ObjectMapper objectMapper) {
        this.redisTemplate = redisTemplate;
        this.worldstateCacheRepository = worldstateCacheRepository;
        this.parser = parser;
        this.objectMapper = objectMapper;
    }

    public Optional<WorldState> get() {
        try {
            String json = redisTemplate.opsForValue().get(DATA_KEY);
            if (json != null) {
                return Optional.of(parser.parse(objectMapper.readTree(json)));
            }
        } catch (Exception e) {
            log.warn("Redis read for worldstate failed, falling back to DB: {}", e.getMessage());
        }

        Optional<WorldstateCache> dbCache = worldstateCacheRepository.findById(CACHE_ROW_ID);
        if (dbCache.isEmpty()) {
            return Optional.empty();
        }
        WorldstateCache cache = dbCache.get();
        backfillRedis(cache);
        return Optional.of(parser.parse(cache.getPayload()));
    }

    @Transactional
    public void update(JsonNode rawPayload, String etag) {
        writeRedis(rawPayload, etag);

        WorldstateCache cache = worldstateCacheRepository.findById(CACHE_ROW_ID).orElseGet(WorldstateCache::new);
        cache.setId(CACHE_ROW_ID);
        cache.setPayload(rawPayload);
        cache.setEtag(etag);
        cache.setFetchedAt(Instant.now());
        worldstateCacheRepository.save(cache);
    }

    private void writeRedis(JsonNode rawPayload, String etag) {
        try {
            redisTemplate.opsForValue().set(DATA_KEY, objectMapper.writeValueAsString(rawPayload));
            if (etag != null && !etag.isBlank()) {
                redisTemplate.opsForValue().set(ETAG_KEY, etag);
            }
            redisTemplate.opsForValue().set(FETCHED_AT_KEY, Instant.now().toString());
        } catch (Exception e) {
            log.warn("Redis write for worldstate failed (continuing on DB only): {}", e.getMessage());
        }
    }

    private void backfillRedis(WorldstateCache cache) {
        try {
            redisTemplate.opsForValue().set(DATA_KEY, objectMapper.writeValueAsString(cache.getPayload()));
            redisTemplate.opsForValue().set(ETAG_KEY, cache.getEtag() == null ? "" : cache.getEtag());
            redisTemplate.opsForValue().set(FETCHED_AT_KEY, cache.getFetchedAt().toString());
        } catch (Exception e) {
            log.warn("Redis backfill for worldstate failed: {}", e.getMessage());
        }
    }
}
