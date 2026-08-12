package com.cephalononni.model;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.Instant;

/**
 * DB fallback for the worldstate poller. Redis holds the hot copy; this single-row table
 * (id is always 1) is what the scheduler falls back to reading on startup / Redis outage,
 * mirroring the Mongo `worldstate` collection's role today.
 */
@Entity
@Table(name = "worldstate_cache")
@Getter
@Setter
public class WorldstateCache {

    @Id
    private Long id = 1L;

    @Column(name = "etag")
    private String etag;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(nullable = false)
    private JsonNode payload;

    @Column(name = "fetched_at", nullable = false)
    private Instant fetchedAt = Instant.now();
}
