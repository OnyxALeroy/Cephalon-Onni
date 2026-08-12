package com.cephalononni.model;

import com.fasterxml.jackson.databind.JsonNode;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

@Entity
@Table(name = "missions")
@Getter
@Setter
public class Mission {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "unique_name", unique = true)
    private String uniqueName;

    @Column(name = "mission_name")
    private String missionName;

    @Column(name = "system_name")
    private String systemName;

    private String planet;

    @Column(name = "type")
    private String type;

    @Column(name = "node_type")
    private Integer nodeType;

    @Column(name = "faction_index")
    private Integer factionIndex;

    @Column(name = "mastery_req")
    private Integer masteryReq;

    @Column(name = "min_enemy_level")
    private Integer minEnemyLevel;

    @Column(name = "max_enemy_level")
    private Integer maxEnemyLevel;

    @Column(name = "mission_index")
    private Integer missionIndex;

    @Column(name = "system_index")
    private Integer systemIndex;

    @JdbcTypeCode(SqlTypes.JSON)
    private JsonNode drops;
}
