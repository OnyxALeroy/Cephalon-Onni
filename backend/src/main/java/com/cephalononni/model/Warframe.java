package com.cephalononni.model;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

/** Maps to the pre-existing `warframes` catalog table (seeded by the static data importer). */
@Entity
@Table(name = "warframes")
@Getter
@Setter
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
}
