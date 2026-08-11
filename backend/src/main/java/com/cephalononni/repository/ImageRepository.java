package com.cephalononni.repository;

import com.cephalononni.model.Image;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface ImageRepository extends JpaRepository<Image, Integer> {
    Optional<Image> findByUniqueName(String uniqueName);
}
