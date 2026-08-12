package com.cephalononni.service;

import java.time.Instant;
import java.util.Objects;
import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataAccessException;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.lang.NonNull;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.cephalononni.model.WorldstateCache;
import com.cephalononni.repository.WorldstateCacheRepository;
import com.cephalononni.web.dto.WorldstateDtos.WorldState;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

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
    @NonNull
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

    /**
     * Returns the cached worldstate, preferring Redis and falling back to the DB row if Redis
     * is empty or unreachable. Empty only if neither has ever been populated.
     */
    public Optional<WorldState> get() {
        try {
            String json = redisTemplate.opsForValue().get(DATA_KEY);
            if (json != null) {
                return Optional.of(parser.parse(objectMapper.readTree(json)));
            }
        } catch (JsonProcessingException | DataAccessException e) {
            // DataAccessException covers a Redis connection failure; JsonProcessingException
            // covers a corrupt cached payload. Either way, fall back to the DB.
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

    /** Writes the freshly-fetched payload to both Redis (best-effort) and the DB row of record. */
    @Transactional
    public void update(JsonNode rawPayload, String etag) {
        writeRedis(rawPayload, etag);

        WorldstateCache cache = loadOrCreateCache();
        cache.setId(CACHE_ROW_ID);
        cache.setPayload(rawPayload);
        cache.setEtag(etag);
        cache.setFetchedAt(Instant.now());
        worldstateCacheRepository.save(cache);
    }

    /** Best-effort mirror of a freshly-fetched payload into Redis; a failure here never propagates. */
    private void writeRedis(JsonNode rawPayload, String etag) {
        try {
            redisTemplate.opsForValue().set(DATA_KEY, toJson(rawPayload));
            if (etag != null && !etag.isBlank()) {
                redisTemplate.opsForValue().set(ETAG_KEY, etag);
            }
            redisTemplate.opsForValue().set(FETCHED_AT_KEY, instantToString(Instant.now()));
        } catch (JsonProcessingException | DataAccessException e) {
            log.warn("Redis write for worldstate failed (continuing on DB only): {}", e.getMessage());
        }
    }

    /** Re-populates Redis from the DB row after a cache miss, so the next read hits Redis again. */
    private void backfillRedis(WorldstateCache cache) {
        try {
            redisTemplate.opsForValue().set(DATA_KEY, toJson(cache.getPayload()));
            String etag = cache.getEtag();
            redisTemplate.opsForValue().set(ETAG_KEY, etag == null ? "" : etag);
            redisTemplate.opsForValue().set(FETCHED_AT_KEY, instantToString(cache.getFetchedAt()));
        } catch (JsonProcessingException | DataAccessException e) {
            log.warn("Redis backfill for worldstate failed: {}", e.getMessage());
        }
    }

    /** Loads the single cache row, or a fresh (unsaved) one if it doesn't exist yet. */
    @NonNull
    private WorldstateCache loadOrCreateCache() {
        WorldstateCache cache = worldstateCacheRepository.findById(CACHE_ROW_ID).orElseGet(WorldstateCache::new);
        return Objects.requireNonNull(cache);
    }

    /** Serializes a value to JSON for storage in Redis. */
    @NonNull
    private String toJson(Object value) throws com.fasterxml.jackson.core.JsonProcessingException {
        String json = objectMapper.writeValueAsString(value);
        return Objects.requireNonNull(json);
    }

    /** Formats an instant for storage in Redis. */
    @NonNull
    private String instantToString(Instant instant) {
        return Objects.requireNonNull(instant.toString());
    }
}
