package com.cephalononni.repository;

import com.cephalononni.model.Mod;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface ModRepository extends JpaRepository<Mod, Integer> {
    Optional<Mod> findByUniqueName(String uniqueName);
    boolean existsByUniqueName(String uniqueName);
}
