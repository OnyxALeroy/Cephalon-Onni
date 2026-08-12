package com.cephalononni.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

/** From the `items` branch: amp parts (Operator amps). */
@Entity
@Table(name = "amp_parts")
@Getter
@Setter
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
}
