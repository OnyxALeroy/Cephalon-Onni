package com.cephalononni.model;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
@Table(name = "missions")
public class Mission {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "unique_name", unique = true)
    private String uniqueName;

    @Column(name = "mission_name")
    private String missionName;

    @Column(name = "system_name")
    private String systemName;

    private String planet;

    @Column(name = "type")
    private String type;

    @Column(name = "node_type")
    private Integer nodeType;

    @Column(name = "faction_index")
    private Integer factionIndex;

    @Column(name = "mastery_req")
    private Integer masteryReq;

    @Column(name = "min_enemy_level")
    private Integer minEnemyLevel;

    @Column(name = "max_enemy_level")
    private Integer maxEnemyLevel;

    @Column(name = "mission_index")
    private Integer missionIndex;

    @Column(name = "system_index")
    private Integer systemIndex;

    @JdbcTypeCode(SqlTypes.JSON)
    private JsonNode drops;

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public String getUniqueName() { return uniqueName; }
    public void setUniqueName(String uniqueName) { this.uniqueName = uniqueName; }
    public String getMissionName() { return missionName; }
    public void setMissionName(String missionName) { this.missionName = missionName; }
    public String getSystemName() { return systemName; }
    public void setSystemName(String systemName) { this.systemName = systemName; }
    public String getPlanet() { return planet; }
    public void setPlanet(String planet) { this.planet = planet; }
    public String getType() { return type; }
    public void setType(String type) { this.type = type; }
    public Integer getNodeType() { return nodeType; }
    public void setNodeType(Integer nodeType) { this.nodeType = nodeType; }
    public Integer getFactionIndex() { return factionIndex; }
    public void setFactionIndex(Integer factionIndex) { this.factionIndex = factionIndex; }
    public Integer getMasteryReq() { return masteryReq; }
    public void setMasteryReq(Integer masteryReq) { this.masteryReq = masteryReq; }
    public Integer getMinEnemyLevel() { return minEnemyLevel; }
    public void setMinEnemyLevel(Integer minEnemyLevel) { this.minEnemyLevel = minEnemyLevel; }
    public Integer getMaxEnemyLevel() { return maxEnemyLevel; }
    public void setMaxEnemyLevel(Integer maxEnemyLevel) { this.maxEnemyLevel = maxEnemyLevel; }
    public Integer getMissionIndex() { return missionIndex; }
    public void setMissionIndex(Integer missionIndex) { this.missionIndex = missionIndex; }
    public Integer getSystemIndex() { return systemIndex; }
    public void setSystemIndex(Integer systemIndex) { this.systemIndex = systemIndex; }
    public JsonNode getDrops() { return drops; }
    public void setDrops(JsonNode drops) { this.drops = drops; }
}
