package com.cephalononni.repository;

import com.cephalononni.model.Arcane;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.Optional;

public interface ArcaneRepository extends JpaRepository<Arcane, Integer> {
    Optional<Arcane> findByUniqueName(String uniqueName);
    boolean existsByUniqueName(String uniqueName);

    /** Scalar-only projection for the public /api/builds/available/arcanes listing. */
    @Query("select a.uniqueName as uniqueName, a.name as name, a.rarity as rarity from Arcane a order by a.id")
    List<ArcaneBrief> findAllBrief();

    interface ArcaneBrief {
        String getUniqueName();
        String getName();
        String getRarity();
    }
}
