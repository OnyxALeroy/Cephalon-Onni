package com.cephalononni.model;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
@Table(name = "recipes")
@Getter
@Setter
public class Recipe {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "unique_name", unique = true)
    private String uniqueName;

    @Column(name = "build_price")
    private Integer buildPrice;

    @Column(name = "build_time")
    private Integer buildTime;

    @Column(name = "skip_build_time_price")
    private Integer skipBuildTimePrice;

    @Column(name = "consume_on_use")
    private Boolean consumeOnUse;

    private Integer num;

    @Column(name = "codex_secret")
    private Boolean codexSecret;

    @Column(name = "result_type")
    private String resultType;

    @JdbcTypeCode(SqlTypes.JSON)
    private JsonNode ingredients;
}
