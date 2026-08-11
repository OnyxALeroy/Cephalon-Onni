package com.cephalononni.model;

import jakarta.persistence.*;

/** From the `items` branch: crafting resources. */
@Entity
@Table(name = "resources")
public class Resource {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "unique_name", unique = true)
    private String uniqueName;

    private String name;

    @Column(columnDefinition = "text")
    private String description;

    @Column(name = "codex_secret")
    private Boolean codexSecret;

    @Column(name = "parent_name")
    private String parentName;

    @Column(name = "exclude_from_codex")
    private Boolean excludeFromCodex;

    @Column(name = "show_in_inventory")
    private Boolean showInInventory;

    @Column(name = "prime_selling_price")
    private Integer primeSellingPrice;

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public String getUniqueName() { return uniqueName; }
    public void setUniqueName(String uniqueName) { this.uniqueName = uniqueName; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }
    public Boolean getCodexSecret() { return codexSecret; }
    public void setCodexSecret(Boolean codexSecret) { this.codexSecret = codexSecret; }
    public String getParentName() { return parentName; }
    public void setParentName(String parentName) { this.parentName = parentName; }
    public Boolean getExcludeFromCodex() { return excludeFromCodex; }
    public void setExcludeFromCodex(Boolean excludeFromCodex) { this.excludeFromCodex = excludeFromCodex; }
    public Boolean getShowInInventory() { return showInInventory; }
    public void setShowInInventory(Boolean showInInventory) { this.showInInventory = showInInventory; }
    public Integer getPrimeSellingPrice() { return primeSellingPrice; }
    public void setPrimeSellingPrice(Integer primeSellingPrice) { this.primeSellingPrice = primeSellingPrice; }
}
