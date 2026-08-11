package com.cephalononni.model;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

/** From the `items` branch: arcanes, required by build validation (<=2 per warframe). */
@Entity
@Table(name = "arcanes")
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

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public String getUniqueName() { return uniqueName; }
    public void setUniqueName(String uniqueName) { this.uniqueName = uniqueName; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public Boolean getCodexSecret() { return codexSecret; }
    public void setCodexSecret(Boolean codexSecret) { this.codexSecret = codexSecret; }
    public String getRarity() { return rarity; }
    public void setRarity(String rarity) { this.rarity = rarity; }
    public JsonNode getLevelStats() { return levelStats; }
    public void setLevelStats(JsonNode levelStats) { this.levelStats = levelStats; }
}
