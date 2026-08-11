package com.cephalononni.web;

import com.cephalononni.security.CurrentUser;
import com.cephalononni.service.BuildService;
import com.cephalononni.web.dto.BuildDtos.*;
import com.cephalononni.web.dto.WarframeDtos.*;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/builds")
public class BuildController {

    private final BuildService buildService;

    public BuildController(BuildService buildService) {
        this.buildService = buildService;
    }

    @PostMapping("/")
    @ResponseStatus(HttpStatus.CREATED)
    public BuildCreated createBuild(@AuthenticationPrincipal CurrentUser user, @Valid @RequestBody CreateRequest req) {
        return buildService.createBuild(user.id(), req);
    }

    @GetMapping({"", "/"})
    public List<BuildPublic> listBuilds(
            @AuthenticationPrincipal CurrentUser user,
            @RequestParam(defaultValue = "0") int skip,
            @RequestParam(defaultValue = "30") int limit,
            @RequestParam(name = "include_details", defaultValue = "false") boolean includeDetails) {
        return buildService.listBuilds(user.id(), skip, limit, includeDetails);
    }

    @GetMapping("/{buildId}")
    public BuildWithDetails getBuild(@AuthenticationPrincipal CurrentUser user, @PathVariable Long buildId) {
        return buildService.getBuild(user.id(), buildId);
    }

    @PutMapping("/{buildId}")
    public BuildWithDetails updateBuild(@AuthenticationPrincipal CurrentUser user, @PathVariable Long buildId,
                                         @Valid @RequestBody UpdateRequest req) {
        return buildService.updateBuild(user.id(), buildId, req);
    }

    @DeleteMapping("/{buildId}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deleteBuild(@AuthenticationPrincipal CurrentUser user, @PathVariable Long buildId) {
        buildService.deleteBuild(user.id(), buildId);
    }

    @GetMapping("/available/warframes")
    public List<AvailableWarframe> availableWarframes() {
        return buildService.availableWarframes();
    }

    @GetMapping("/available/weapons")
    public List<AvailableWeapon> availableWeapons() {
        return buildService.availableWeapons();
    }

    @GetMapping("/available/mods")
    public List<AvailableMod> availableMods() {
        return buildService.availableMods();
    }

    @GetMapping("/available/arcanes")
    public List<AvailableArcane> availableArcanes() {
        return buildService.availableArcanes();
    }
}
