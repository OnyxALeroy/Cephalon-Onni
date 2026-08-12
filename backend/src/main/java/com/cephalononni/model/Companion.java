package com.cephalononni.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

/** From the `items` branch: companions (sentinels/kubrows/kavats). */
@Entity
@Table(name = "companions")
@Getter
@Setter
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
}
