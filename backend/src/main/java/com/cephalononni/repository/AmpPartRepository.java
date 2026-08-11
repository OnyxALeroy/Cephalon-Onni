package com.cephalononni.repository;

import com.cephalononni.model.AmpPart;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AmpPartRepository extends JpaRepository<AmpPart, Integer> {
    boolean existsByUniqueName(String uniqueName);
}
