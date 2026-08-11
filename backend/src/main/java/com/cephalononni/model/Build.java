package com.cephalononni.model;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.Instant;

/**
 * A saved loadout. warframe_mods/warframe_arcanes and the three weapon slots are stored as JSON
 * (mirroring the current Mongo document shape) rather than normalized junction tables, per the
 * rework plan's recommendation — the API's JSON contract for these fields does not change.
 */
@Entity
@Table(name = "builds")
public class Build {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(nullable = false)
    private String name;

    @Column(name = "warframe_unique_name", nullable = false)
    private String warframeUniqueName;

    /** JSON array of {uniqueName, level} — max 10 enforced in the service layer. */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "warframe_mods", nullable = false)
    private JsonNode warframeMods;

    /** JSON array of arcane unique-name strings — max 2 enforced in the service layer. */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "warframe_arcanes", nullable = false)
    private JsonNode warframeArcanes;

    /** JSON object {weapon_uniqueName, mods:[{uniqueName,level}] (max 9), arcane_uniqueName} or null. */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "primary_weapon")
    private JsonNode primaryWeapon;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "secondary_weapon")
    private JsonNode secondaryWeapon;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "melee_weapon")
    private JsonNode meleeWeapon;

    @Column(name = "created_at", nullable = false)
    private Instant createdAt = Instant.now();

    @Column(name = "updated_at", nullable = false)
    private Instant updatedAt = Instant.now();

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    public Long getUserId() { return userId; }
    public void setUserId(Long userId) { this.userId = userId; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getWarframeUniqueName() { return warframeUniqueName; }
    public void setWarframeUniqueName(String warframeUniqueName) { this.warframeUniqueName = warframeUniqueName; }
    public JsonNode getWarframeMods() { return warframeMods; }
    public void setWarframeMods(JsonNode warframeMods) { this.warframeMods = warframeMods; }
    public JsonNode getWarframeArcanes() { return warframeArcanes; }
    public void setWarframeArcanes(JsonNode warframeArcanes) { this.warframeArcanes = warframeArcanes; }
    public JsonNode getPrimaryWeapon() { return primaryWeapon; }
    public void setPrimaryWeapon(JsonNode primaryWeapon) { this.primaryWeapon = primaryWeapon; }
    public JsonNode getSecondaryWeapon() { return secondaryWeapon; }
    public void setSecondaryWeapon(JsonNode secondaryWeapon) { this.secondaryWeapon = secondaryWeapon; }
    public JsonNode getMeleeWeapon() { return meleeWeapon; }
    public void setMeleeWeapon(JsonNode meleeWeapon) { this.meleeWeapon = meleeWeapon; }
    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
    public Instant getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(Instant updatedAt) { this.updatedAt = updatedAt; }
}
