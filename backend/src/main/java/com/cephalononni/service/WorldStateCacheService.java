package com.cephalononni.service;

import java.time.Instant;
import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.dao.DataAccessException;
import org.springframework.data.redis.core.StringRedisTemplate;
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
 *
 * The parsed {@link WorldState} is kept in memory once parsed (the raw payload is ~1 MB of
 * JSON and the public /api/worldstate endpoint would otherwise re-parse it on every request).
 * It is single-process safe by construction: the only writer is the single-threaded
 * scheduler in WorldStateFetcher.
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

    private volatile WorldState cachedWorldState;

    public WorldStateCacheService(StringRedisTemplate redisTemplate,
                                   WorldstateCacheRepository worldstateCacheRepository,
                                   WorldStateParser parser, ObjectMapper objectMapper) {
        this.redisTemplate = redisTemplate;
        this.worldstateCacheRepository = worldstateCacheRepository;
        this.parser = parser;
        this.objectMapper = objectMapper;
    }

    /**
     * Returns the cached worldstate, preferring the in-memory parsed copy, then Redis, then the
     * DB row if Redis is empty or unreachable. Empty only if nothing has ever been populated.
     */
    public Optional<WorldState> get() {
        WorldState cached = cachedWorldState;
        if (cached != null) {
            return Optional.of(cached);
        }

        Optional<JsonNode> rawPayload = rawPayloadFromRedis().or(this::rawPayloadFromDb);
        if (rawPayload.isEmpty()) {
            return Optional.empty();
        }
        WorldState worldState = parser.parse(rawPayload.get());
        cachedWorldState = worldState;
        return Optional.of(worldState);
    }

    /** Writes the freshly-fetched payload to both Redis (best-effort) and the DB row of record. */
    @Transactional
    public void update(JsonNode rawPayload, String etag) {
        writeRedis(rawPayload, etag);

        WorldstateCache cache = worldstateCacheRepository.findById(CACHE_ROW_ID)
                .orElseGet(WorldstateCache::new);
        cache.setId(CACHE_ROW_ID);
        cache.setPayload(rawPayload);
        cache.setEtag(etag);
        cache.setFetchedAt(Instant.now());
        worldstateCacheRepository.save(cache);

        cachedWorldState = parser.parse(rawPayload);
    }

    /**
     * The etag of record, used by the poller to seed its in-memory etag after a restart so the
     * first poll can get a cheap 304. Prefers the DB row (what {@link #update} persisted);
     * falls back to the Redis mirror if the row is missing.
     */
    public Optional<String> persistedEtag() {
        Optional<WorldstateCache> dbCache = worldstateCacheRepository.findById(CACHE_ROW_ID);
        if (dbCache.isPresent() && dbCache.get().getEtag() != null && !dbCache.get().getEtag().isBlank()) {
            return Optional.of(dbCache.get().getEtag());
        }
        try {
            return Optional.ofNullable(redisTemplate.opsForValue().get(ETAG_KEY))
                    .filter(etag -> !etag.isBlank());
        } catch (DataAccessException e) {
            log.debug("Redis read for worldstate etag failed: {}", e.getMessage());
            return Optional.empty();
        }
    }

    private Optional<JsonNode> rawPayloadFromRedis() {
        try {
            String json = redisTemplate.opsForValue().get(DATA_KEY);
            if (json == null) {
                return Optional.empty();
            }
            return Optional.of(objectMapper.readTree(json));
        } catch (JsonProcessingException | DataAccessException e) {
            // DataAccessException covers a Redis connection failure; JsonProcessingException
            // covers a corrupt cached payload. Either way, fall back to the DB.
            log.warn("Redis read for worldstate failed, falling back to DB: {}", e.getMessage());
            return Optional.empty();
        }
    }

    private Optional<JsonNode> rawPayloadFromDb() {
        Optional<WorldstateCache> dbCache = worldstateCacheRepository.findById(CACHE_ROW_ID);
        if (dbCache.isEmpty()) {
            return Optional.empty();
        }
        WorldstateCache cache = dbCache.get();
        backfillRedis(cache);
        return Optional.of(cache.getPayload());
    }

    /** Best-effort mirror of a freshly-fetched payload into Redis; a failure here never propagates. */
    private void writeRedis(JsonNode rawPayload, String etag) {
        try {
            redisTemplate.opsForValue().set(DATA_KEY, toJson(rawPayload));
            if (etag != null && !etag.isBlank()) {
                redisTemplate.opsForValue().set(ETAG_KEY, etag);
            }
            redisTemplate.opsForValue().set(FETCHED_AT_KEY, Instant.now().toString());
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
            redisTemplate.opsForValue().set(FETCHED_AT_KEY, cache.getFetchedAt().toString());
        } catch (JsonProcessingException | DataAccessException e) {
            log.warn("Redis backfill for worldstate failed: {}", e.getMessage());
        }
    }

    /** Serializes a value to JSON for storage in Redis. */
    private String toJson(Object value) throws JsonProcessingException {
        return objectMapper.writeValueAsString(value);
    }
}
