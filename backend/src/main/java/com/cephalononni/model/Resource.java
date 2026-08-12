package com.cephalononni.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

/** From the `items` branch: crafting resources. */
@Entity
@Table(name = "resources")
@Getter
@Setter
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
}
