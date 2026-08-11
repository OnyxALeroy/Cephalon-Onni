package com.cephalononni.repository;

import com.cephalononni.model.Resource;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ResourceRepository extends JpaRepository<Resource, Integer> {
    boolean existsByUniqueName(String uniqueName);
}
