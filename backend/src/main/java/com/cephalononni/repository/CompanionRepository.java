package com.cephalononni.repository;

import com.cephalononni.model.Companion;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CompanionRepository extends JpaRepository<Companion, Integer> {
    boolean existsByUniqueName(String uniqueName);
}
