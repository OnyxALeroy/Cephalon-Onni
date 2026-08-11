package com.cephalononni.repository;

import com.cephalononni.model.Build;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface BuildRepository extends JpaRepository<Build, Long> {
    long countByUserId(Long userId);
    List<Build> findByUserIdOrderByCreatedAtDesc(Long userId, Pageable pageable);
    Optional<Build> findByIdAndUserId(Long id, Long userId);
    long deleteByIdAndUserId(Long id, Long userId);
}
