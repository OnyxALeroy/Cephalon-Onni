package com.cephalononni.repository;

import com.cephalononni.model.Warframe;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.Optional;

public interface WarframeRepository extends JpaRepository<Warframe, Integer> {
    Optional<Warframe> findByUniqueName(String uniqueName);
    boolean existsByUniqueName(String uniqueName);

    /** Scalar-only projection for the public /api/builds/available/warframes listing. */
    @Query("select w.uniqueName as uniqueName, w.name as name, w.masteryReq as masteryReq from Warframe w order by w.id")
    List<WarframeBrief> findAllBrief();

    interface WarframeBrief {
        String getUniqueName();
        String getName();
        Integer getMasteryReq();
    }
}
