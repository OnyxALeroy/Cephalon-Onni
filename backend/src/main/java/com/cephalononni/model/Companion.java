package com.cephalononni.model;

import jakarta.persistence.*;

/** From the `items` branch: companions (sentinels/kubrows/kavats). */
@Entity
@Table(name = "companions")
public class Companion {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "unique_name", unique = true)
    private String uniqueName;

    private String name;

    @Column(columnDefinition = "text")
    private String description;

    private Integer health;
    private Integer shield;
    private Integer armor;
    private Integer stamina;
    private Integer power;

    @Column(name = "codex_secret")
    private Boolean codexSecret;

    @Column(name = "exclude_from_codex")
    private Boolean excludeFromCodex;

    @Column(name = "product_category")
    private String productCategory;

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public String getUniqueName() { return uniqueName; }
    public void setUniqueName(String uniqueName) { this.uniqueName = uniqueName; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
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
    public Boolean getExcludeFromCodex() { return excludeFromCodex; }
    public void setExcludeFromCodex(Boolean excludeFromCodex) { this.excludeFromCodex = excludeFromCodex; }
    public String getProductCategory() { return productCategory; }
    public void setProductCategory(String productCategory) { this.productCategory = productCategory; }
}
