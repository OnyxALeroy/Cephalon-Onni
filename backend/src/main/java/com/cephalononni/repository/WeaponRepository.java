package com.cephalononni.repository;

import com.cephalononni.model.Weapon;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;
import java.util.Optional;

public interface WeaponRepository extends JpaRepository<Weapon, Integer> {
    Optional<Weapon> findByUniqueName(String uniqueName);
    boolean existsByUniqueName(String uniqueName);

    /** Scalar-only projection for the public /api/builds/available/weapons listing. */
    @Query("select w.uniqueName as uniqueName, w.name as name, w.masteryReq as masteryReq, w.productCategory as productCategory from Weapon w order by w.id")
    List<WeaponBrief> findAllBrief();

    interface WeaponBrief {
        String getUniqueName();
        String getName();
        Integer getMasteryReq();
        String getProductCategory();
    }
}
