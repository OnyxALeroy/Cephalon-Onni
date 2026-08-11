package com.cephalononni.repository;

import com.cephalononni.model.Arcane;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface ArcaneRepository extends JpaRepository<Arcane, Integer> {
    Optional<Arcane> findByUniqueName(String uniqueName);
    boolean existsByUniqueName(String uniqueName);
}
