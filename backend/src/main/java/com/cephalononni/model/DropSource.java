package com.cephalononni.model;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Table(name = "drop_sources", uniqueConstraints =
    @UniqueConstraint(name = "uq_drop_sources_name_source_rotation", columnNames = {"name", "source", "rotation"}))
@Getter
@Setter
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
}
