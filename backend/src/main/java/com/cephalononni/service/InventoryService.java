package com.cephalononni.service;

import com.cephalononni.exception.ApiException;
import com.cephalononni.model.InventoryItem;
import com.cephalononni.repository.InventoryItemRepository;
import com.cephalononni.web.dto.InventoryDtos.InventoryItemResponse;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class InventoryService {

    private final InventoryItemRepository inventoryItemRepository;

    public InventoryService(InventoryItemRepository inventoryItemRepository) {
        this.inventoryItemRepository = inventoryItemRepository;
    }

    public List<InventoryItemResponse> listInventory(Long userId) {
        return inventoryItemRepository.findByUserId(userId).stream().map(this::toResponse).toList();
    }

    public InventoryItemResponse getItem(Long userId, Long itemId) {
        InventoryItem item = inventoryItemRepository.findByIdAndUserId(itemId, userId)
                .orElseThrow(() -> ApiException.notFound("Not Found"));
        return toResponse(item);
    }

    private InventoryItemResponse toResponse(InventoryItem item) {
        return new InventoryItemResponse(
                String.valueOf(item.getId()), item.getItemKey(), item.getName(), item.getType(), item.getRarity(),
                item.getCount(), item.getRank(), item.getPolarity(), item.getExtra());
    }
}
