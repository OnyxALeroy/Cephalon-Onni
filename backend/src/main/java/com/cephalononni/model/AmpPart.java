package com.cephalononni.model;

import jakarta.persistence.*;

/** From the `items` branch: amp parts (Operator amps). */
@Entity
@Table(name = "amp_parts")
public class AmpPart {

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

    @Column(name = "component_type")
    private String componentType;

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
    public String getComponentType() { return componentType; }
    public void setComponentType(String componentType) { this.componentType = componentType; }
}
