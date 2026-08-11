package com.cephalononni.model;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

/** Maps to the pre-existing `warframes` catalog table (seeded by the static data importer). */
@Entity
@Table(name = "warframes")
public class Warframe {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "unique_name", unique = true)
    private String uniqueName;

    private String name;

    @Column(name = "parent_name")
    private String parentName;

    @Column(columnDefinition = "text")
    private String description;

    private Integer health;
    private Integer shield;
    private Integer armor;
    private Integer stamina;
    private Integer power;

    @Column(name = "codex_secret")
    private Boolean codexSecret;

    @Column(name = "mastery_req")
    private Integer masteryReq;

    @Column(name = "sprint_speed")
    private Double sprintSpeed;

    @Column(name = "passive_description", columnDefinition = "text")
    private String passiveDescription;

    /** JSON array of exalted weapon unique names. */
    @JdbcTypeCode(SqlTypes.JSON)
    private JsonNode exalted;

    /** JSON array of {abilityUniqueName, abilityName, description}. */
    @JdbcTypeCode(SqlTypes.JSON)
    private JsonNode abilities;

    @Column(name = "product_category")
    private String productCategory;

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public String getUniqueName() { return uniqueName; }
    public void setUniqueName(String uniqueName) { this.uniqueName = uniqueName; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getParentName() { return parentName; }
    public void setParentName(String parentName) { this.parentName = parentName; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public Integer getHealth() { return health; }
    public void setHealth(Integer health) { this.health = health; }
    public Integer getShield() { return shield; }
    public void setShield(Integer shield) { this.shield = shield; }
    public Integer getArmor() { return armor; }
    public void setArmor(Integer armor) { this.armor = armor; }
    public Integer getStamina() { return stamina; }
    public void setStamina(Integer stamina) { this.stamina = stamina; }
    public Integer getPower() { return power; }
    public void setPower(Integer power) { this.power = power; }
    public Boolean getCodexSecret() { return codexSecret; }
    public void setCodexSecret(Boolean codexSecret) { this.codexSecret = codexSecret; }
    public Integer getMasteryReq() { return masteryReq; }
    public void setMasteryReq(Integer masteryReq) { this.masteryReq = masteryReq; }
    public Double getSprintSpeed() { return sprintSpeed; }
    public void setSprintSpeed(Double sprintSpeed) { this.sprintSpeed = sprintSpeed; }
    public String getPassiveDescription() { return passiveDescription; }
    public void setPassiveDescription(String passiveDescription) { this.passiveDescription = passiveDescription; }
    public JsonNode getExalted() { return exalted; }
    public void setExalted(JsonNode exalted) { this.exalted = exalted; }
    public JsonNode getAbilities() { return abilities; }
    public void setAbilities(JsonNode abilities) { this.abilities = abilities; }
    public String getProductCategory() { return productCategory; }
    public void setProductCategory(String productCategory) { this.productCategory = productCategory; }
}
