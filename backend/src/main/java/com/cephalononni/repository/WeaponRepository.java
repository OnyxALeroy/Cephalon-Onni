package com.cephalononni.repository;

import com.cephalononni.model.Weapon;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface WeaponRepository extends JpaRepository<Weapon, Integer> {
    Optional<Weapon> findByUniqueName(String uniqueName);
    boolean existsByUniqueName(String uniqueName);
}
