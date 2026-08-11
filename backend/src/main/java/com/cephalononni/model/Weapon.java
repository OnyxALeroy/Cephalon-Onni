package com.cephalononni.model;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
@Table(name = "weapons")
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

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public String getUniqueName() { return uniqueName; }
    public void setUniqueName(String uniqueName) { this.uniqueName = uniqueName; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public Boolean getCodexSecret() { return codexSecret; }
    public void setCodexSecret(Boolean codexSecret) { this.codexSecret = codexSecret; }
    public Double getCriticalChance() { return criticalChance; }
    public void setCriticalChance(Double criticalChance) { this.criticalChance = criticalChance; }
    public Double getCriticalMultiplier() { return criticalMultiplier; }
    public void setCriticalMultiplier(Double criticalMultiplier) { this.criticalMultiplier = criticalMultiplier; }
    public JsonNode getDamagePerShot() { return damagePerShot; }
    public void setDamagePerShot(JsonNode damagePerShot) { this.damagePerShot = damagePerShot; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public Double getFireRate() { return fireRate; }
    public void setFireRate(Double fireRate) { this.fireRate = fireRate; }
    public Integer getMasteryReq() { return masteryReq; }
    public void setMasteryReq(Integer masteryReq) { this.masteryReq = masteryReq; }
    public Double getOmegaAttenuation() { return omegaAttenuation; }
    public void setOmegaAttenuation(Double omegaAttenuation) { this.omegaAttenuation = omegaAttenuation; }
    public Double getProcChance() { return procChance; }
    public void setProcChance(Double procChance) { this.procChance = procChance; }
    public String getProductCategory() { return productCategory; }
    public void setProductCategory(String productCategory) { this.productCategory = productCategory; }
    public Integer getTotalDamage() { return totalDamage; }
    public void setTotalDamage(Integer totalDamage) { this.totalDamage = totalDamage; }
    public Double getAccuracy() { return accuracy; }
    public void setAccuracy(Double accuracy) { this.accuracy = accuracy; }
    public Integer getBlockingAngle() { return blockingAngle; }
    public void setBlockingAngle(Integer blockingAngle) { this.blockingAngle = blockingAngle; }
    public Integer getComboDuration() { return comboDuration; }
    public void setComboDuration(Integer comboDuration) { this.comboDuration = comboDuration; }
    public Boolean getExcludeFromCodex() { return excludeFromCodex; }
    public void setExcludeFromCodex(Boolean excludeFromCodex) { this.excludeFromCodex = excludeFromCodex; }
    public Double getFollowThrough() { return followThrough; }
    public void setFollowThrough(Double followThrough) { this.followThrough = followThrough; }
    public Integer getHeavyAttackDamage() { return heavyAttackDamage; }
    public void setHeavyAttackDamage(Integer heavyAttackDamage) { this.heavyAttackDamage = heavyAttackDamage; }
    public Integer getHeavySlamAttack() { return heavySlamAttack; }
    public void setHeavySlamAttack(Integer heavySlamAttack) { this.heavySlamAttack = heavySlamAttack; }
    public Integer getHeavySlamRadialDamage() { return heavySlamRadialDamage; }
    public void setHeavySlamRadialDamage(Integer heavySlamRadialDamage) { this.heavySlamRadialDamage = heavySlamRadialDamage; }
    public Integer getHeavySlamRadius() { return heavySlamRadius; }
    public void setHeavySlamRadius(Integer heavySlamRadius) { this.heavySlamRadius = heavySlamRadius; }
    public Integer getMagazineSize() { return magazineSize; }
    public void setMagazineSize(Integer magazineSize) { this.magazineSize = magazineSize; }
    public Integer getMaxLevelCap() { return maxLevelCap; }
    public void setMaxLevelCap(Integer maxLevelCap) { this.maxLevelCap = maxLevelCap; }
    public Integer getMultishot() { return multishot; }
    public void setMultishot(Integer multishot) { this.multishot = multishot; }
    public String getNoise() { return noise; }
    public void setNoise(String noise) { this.noise = noise; }
    public Double getPrimeOmegaAttenuation() { return primeOmegaAttenuation; }
    public void setPrimeOmegaAttenuation(Double primeOmegaAttenuation) { this.primeOmegaAttenuation = primeOmegaAttenuation; }
    public Double getRange() { return range; }
    public void setRange(Double range) { this.range = range; }
    public Double getReloadTime() { return reloadTime; }
    public void setReloadTime(Double reloadTime) { this.reloadTime = reloadTime; }
    public Boolean getSentinel() { return sentinel; }
    public void setSentinel(Boolean sentinel) { this.sentinel = sentinel; }
    public Integer getSlamAttack() { return slamAttack; }
    public void setSlamAttack(Integer slamAttack) { this.slamAttack = slamAttack; }
    public Integer getSlamRadialDamage() { return slamRadialDamage; }
    public void setSlamRadialDamage(Integer slamRadialDamage) { this.slamRadialDamage = slamRadialDamage; }
    public Integer getSlamRadius() { return slamRadius; }
    public void setSlamRadius(Integer slamRadius) { this.slamRadius = slamRadius; }
    public Integer getSlideAttack() { return slideAttack; }
    public void setSlideAttack(Integer slideAttack) { this.slideAttack = slideAttack; }
    public Integer getSlot() { return slot; }
    public void setSlot(Integer slot) { this.slot = slot; }
    public String getTrigger() { return trigger; }
    public void setTrigger(String trigger) { this.trigger = trigger; }
    public Double getWindUp() { return windUp; }
    public void setWindUp(Double windUp) { this.windUp = windUp; }
}
