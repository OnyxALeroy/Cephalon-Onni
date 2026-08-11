package com.cephalononni.repository;

import com.cephalononni.model.Warframe;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface WarframeRepository extends JpaRepository<Warframe, Integer> {
    Optional<Warframe> findByUniqueName(String uniqueName);
    boolean existsByUniqueName(String uniqueName);
}
