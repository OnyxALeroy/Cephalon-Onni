package com.cephalononni.web;

import com.cephalononni.security.CurrentUser;
import com.cephalononni.service.InventoryService;
import com.cephalononni.web.dto.InventoryDtos.InventoryItemResponse;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/inventory")
public class InventoryController {

    private final InventoryService inventoryService;

    public InventoryController(InventoryService inventoryService) {
        this.inventoryService = inventoryService;
    }

    @GetMapping
    public List<InventoryItemResponse> listInventory(@AuthenticationPrincipal CurrentUser user) {
        return inventoryService.listInventory(user.id());
    }

    @GetMapping("/{itemId}")
    public InventoryItemResponse getItem(@AuthenticationPrincipal CurrentUser user, @PathVariable Long itemId) {
        return inventoryService.getItem(user.id(), itemId);
    }
}
