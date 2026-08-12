package com.cephalononni.model;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.Instant;

@Entity
@Table(name = "inventory_items")
@Getter
@Setter
public class InventoryItem {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "item_key", nullable = false)
    private String itemKey;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private String type;

    @Column(nullable = false)
    private String rarity;

    @Column(nullable = false)
    private Integer count = 1;

    private Integer rank;

    /** JSON array of polarity strings. */
    @JdbcTypeCode(SqlTypes.JSON)
    private JsonNode polarity;

    /** Free-form JSON bag for item-type-specific extra fields. */
    @JdbcTypeCode(SqlTypes.JSON)
    private JsonNode extra;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();
}
