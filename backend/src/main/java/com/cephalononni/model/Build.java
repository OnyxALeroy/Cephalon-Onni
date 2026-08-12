package com.cephalononni.model;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
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
@Getter
@Setter
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
}
