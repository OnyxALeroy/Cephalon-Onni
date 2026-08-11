package com.cephalononni.model;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
@Table(name = "mods")
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

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public String getUniqueName() { return uniqueName; }
    public void setUniqueName(String uniqueName) { this.uniqueName = uniqueName; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getPolarity() { return polarity; }
    public void setPolarity(String polarity) { this.polarity = polarity; }
    public String getRarity() { return rarity; }
    public void setRarity(String rarity) { this.rarity = rarity; }
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    public String getSubtype() { return subtype; }
    public void setSubtype(String subtype) { this.subtype = subtype; }
    public Boolean getCodexSecret() { return codexSecret; }
    public void setCodexSecret(Boolean codexSecret) { this.codexSecret = codexSecret; }
    public Integer getBaseDrain() { return baseDrain; }
    public void setBaseDrain(Integer baseDrain) { this.baseDrain = baseDrain; }
    public Integer getFusionLimit() { return fusionLimit; }
    public void setFusionLimit(Integer fusionLimit) { this.fusionLimit = fusionLimit; }
    public String getCompatName() { return compatName; }
    public void setCompatName(String compatName) { this.compatName = compatName; }
    public String getModSet() { return modSet; }
    public void setModSet(String modSet) { this.modSet = modSet; }
    public JsonNode getModSetValues() { return modSetValues; }
    public void setModSetValues(JsonNode modSetValues) { this.modSetValues = modSetValues; }
    public Boolean getIsUtility() { return isUtility; }
    public void setIsUtility(Boolean isUtility) { this.isUtility = isUtility; }
    public JsonNode getDescription() { return description; }
    public void setDescription(JsonNode description) { this.description = description; }
    public JsonNode getLevelStats() { return levelStats; }
    public void setLevelStats(JsonNode levelStats) { this.levelStats = levelStats; }
    public JsonNode getUpgradeEntries() { return upgradeEntries; }
    public void setUpgradeEntries(JsonNode upgradeEntries) { this.upgradeEntries = upgradeEntries; }
    public JsonNode getAvailableChallenges() { return availableChallenges; }
    public void setAvailableChallenges(JsonNode availableChallenges) { this.availableChallenges = availableChallenges; }
}
