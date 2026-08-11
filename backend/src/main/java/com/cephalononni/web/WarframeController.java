package com.cephalononni.web;

import com.cephalononni.service.WarframeService;
import com.cephalononni.web.dto.WarframeDtos.WarframeResponse;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/warframes")
public class WarframeController {

    private final WarframeService warframeService;

    public WarframeController(WarframeService warframeService) {
        this.warframeService = warframeService;
    }

    @GetMapping({"", "/"})
    public List<WarframeResponse> listWarframes() {
        return warframeService.listWarframes();
    }

    @GetMapping("/{uniqueName}")
    public WarframeResponse getWarframe(@PathVariable String uniqueName) {
        return warframeService.getWarframe(uniqueName);
    }
}
