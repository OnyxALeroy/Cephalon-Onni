package com.cephalononni.model;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

/** From the `items` branch: arcanes, required by build validation (<=2 per warframe). */
@Entity
@Table(name = "arcanes")
@Getter
@Setter
public class Arcane {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "unique_name", unique = true)
    private String uniqueName;

    private String name;

    @Column(name = "codex_secret")
    private Boolean codexSecret;

    private String rarity;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "level_stats")
    private JsonNode levelStats;
}
