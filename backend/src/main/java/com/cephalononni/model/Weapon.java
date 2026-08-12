package com.cephalononni.model;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
@Table(name = "weapons")
@Getter
@Setter
public class Weapon {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "unique_name", unique = true)
    private String uniqueName;

    private String name;

    @Column(name = "codex_secret")
    private Boolean codexSecret;

    @Column(name = "critical_chance")
    private Double criticalChance;

    @Column(name = "critical_multiplier")
    private Double criticalMultiplier;

    /** JSON array of per-shot damage-by-type ints. */
    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "damage_per_shot")
    private JsonNode damagePerShot;

    @Column(columnDefinition = "text")
    private String description;

    @Column(name = "fire_rate")
    private Double fireRate;

    @Column(name = "mastery_req")
    private Integer masteryReq;

    @Column(name = "omega_attenuation")
    private Double omegaAttenuation;

    @Column(name = "proc_chance")
    private Double procChance;

    @Column(name = "product_category")
    private String productCategory;

    @Column(name = "total_damage")
    private Integer totalDamage;

    private Double accuracy;

    @Column(name = "blocking_angle")
    private Integer blockingAngle;

    @Column(name = "combo_duration")
    private Integer comboDuration;

    @Column(name = "exclude_from_codex")
    private Boolean excludeFromCodex;

    @Column(name = "follow_through")
    private Double followThrough;

    @Column(name = "heavy_attack_damage")
    private Integer heavyAttackDamage;

    @Column(name = "heavy_slam_attack")
    private Integer heavySlamAttack;

    @Column(name = "heavy_slam_radial_damage")
    private Integer heavySlamRadialDamage;

    @Column(name = "heavy_slam_radius")
    private Integer heavySlamRadius;

    @Column(name = "magazine_size")
    private Integer magazineSize;

    @Column(name = "max_level_cap")
    private Integer maxLevelCap;

    private Integer multishot;

    private String noise;

    @Column(name = "prime_omega_attenuation")
    private Double primeOmegaAttenuation;

    private Double range;

    @Column(name = "reload_time")
    private Double reloadTime;

    private Boolean sentinel;

    @Column(name = "slam_attack")
    private Integer slamAttack;

    @Column(name = "slam_radial_damage")
    private Integer slamRadialDamage;

    @Column(name = "slam_radius")
    private Integer slamRadius;

    @Column(name = "slide_attack")
    private Integer slideAttack;

    private Integer slot;

    private String trigger;

    @Column(name = "wind_up")
    private Double windUp;
}
