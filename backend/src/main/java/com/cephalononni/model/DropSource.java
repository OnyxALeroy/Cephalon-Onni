package com.cephalononni.model;

import jakarta.persistence.*;

@Entity
@Table(name = "drop_sources", uniqueConstraints =
    @UniqueConstraint(name = "uq_drop_sources_name_source", columnNames = {"name", "source"}))
public class DropSource {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    private String name;

    @Column(name = "source_type")
    private String sourceType;

    private String source;

    private Double chance;

    private String rotation;

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public String getSourceType() { return sourceType; }
    public void setSourceType(String sourceType) { this.sourceType = sourceType; }
    public String getSource() { return source; }
    public void setSource(String source) { this.source = source; }
    public Double getChance() { return chance; }
    public void setChance(Double chance) { this.chance = chance; }
    public String getRotation() { return rotation; }
    public void setRotation(String rotation) { this.rotation = rotation; }
}
