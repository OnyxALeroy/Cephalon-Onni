package com.cephalononni.model;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
@Table(name = "recipes")
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

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public String getUniqueName() { return uniqueName; }
    public void setUniqueName(String uniqueName) { this.uniqueName = uniqueName; }
    public Integer getBuildPrice() { return buildPrice; }
    public void setBuildPrice(Integer buildPrice) { this.buildPrice = buildPrice; }
    public Integer getBuildTime() { return buildTime; }
    public void setBuildTime(Integer buildTime) { this.buildTime = buildTime; }
    public Integer getSkipBuildTimePrice() { return skipBuildTimePrice; }
    public void setSkipBuildTimePrice(Integer skipBuildTimePrice) { this.skipBuildTimePrice = skipBuildTimePrice; }
    public Boolean getConsumeOnUse() { return consumeOnUse; }
    public void setConsumeOnUse(Boolean consumeOnUse) { this.consumeOnUse = consumeOnUse; }
    public Integer getNum() { return num; }
    public void setNum(Integer num) { this.num = num; }
    public Boolean getCodexSecret() { return codexSecret; }
    public void setCodexSecret(Boolean codexSecret) { this.codexSecret = codexSecret; }
    public String getResultType() { return resultType; }
    public void setResultType(String resultType) { this.resultType = resultType; }
    public JsonNode getIngredients() { return ingredients; }
    public void setIngredients(JsonNode ingredients) { this.ingredients = ingredients; }
}
