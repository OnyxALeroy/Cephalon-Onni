package com.cephalononni.repository;

import com.cephalononni.model.DropSource;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface DropSourceRepository extends JpaRepository<DropSource, Integer> {

    List<DropSource> findByNameContainingIgnoreCase(String name, Pageable pageable);

    List<DropSource> findBySourceTypeIgnoreCase(String sourceType, Pageable pageable);

    List<DropSource> findBySourceTypeIgnoreCaseAndNameContainingIgnoreCase(
            String sourceType, String name, Pageable pageable);
}
