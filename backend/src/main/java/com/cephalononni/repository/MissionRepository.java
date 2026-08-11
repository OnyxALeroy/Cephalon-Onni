package com.cephalononni.repository;

import com.cephalononni.model.Mission;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface MissionRepository extends JpaRepository<Mission, Integer> {

    List<Mission> findByMissionNameContainingIgnoreCase(String name, org.springframework.data.domain.Pageable pageable);
}
