package com.cephalononni.model;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
@Table(name = "mods")
@Getter
@Setter
public class Mod {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "unique_name", unique = true)
    private String uniqueName;

    private String name;
    private String polarity;
    private String rarity;

    @Column(name = "type")
    private String type;

    @Column(name = "subtype")
    private String subtype;

    @Column(name = "codex_secret")
    private Boolean codexSecret;

    @Column(name = "base_drain")
    private Integer baseDrain;

    @Column(name = "fusion_limit")
    private Integer fusionLimit;

    @Column(name = "compat_name")
    private String compatName;

    @Column(name = "mod_set")
    private String modSet;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "mod_set_values")
    private JsonNode modSetValues;

    @Column(name = "is_utility")
    private Boolean isUtility;

    /** JSON array of per-rank description strings. */
    @JdbcTypeCode(SqlTypes.JSON)
    private JsonNode description;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "level_stats")
    private JsonNode levelStats;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "upgrade_entries")
    private JsonNode upgradeEntries;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "available_challenges")
    private JsonNode availableChallenges;
}
