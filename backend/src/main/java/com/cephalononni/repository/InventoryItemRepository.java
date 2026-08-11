package com.cephalononni.repository;

import com.cephalononni.model.InventoryItem;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface InventoryItemRepository extends JpaRepository<InventoryItem, Long> {
    List<InventoryItem> findByUserId(Long userId);
    Optional<InventoryItem> findByIdAndUserId(Long id, Long userId);
}
