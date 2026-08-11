package com.cephalononni.web;

import com.cephalononni.service.LoottableService;
import com.cephalononni.web.dto.LoottableDtos.NodeNeighborsResponse;
import com.cephalononni.web.dto.LoottableDtos.NodeSearchResponse;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/loottables")
public class LoottableController {

    private final LoottableService loottableService;

    public LoottableController(LoottableService loottableService) {
        this.loottableService = loottableService;
    }

    @GetMapping("/search/nodes")
    public NodeSearchResponse searchNodes(
            @RequestParam(defaultValue = "") String name,
            @RequestParam(defaultValue = "") String label) {
        return loottableService.searchNodes(name, label);
    }

    @GetMapping("/neighbors")
    public NodeNeighborsResponse neighbors(@RequestParam(defaultValue = "") String name) {
        return loottableService.neighbors(name);
    }
}
