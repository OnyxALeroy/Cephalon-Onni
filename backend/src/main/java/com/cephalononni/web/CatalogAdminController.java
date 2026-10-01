package com.cephalononni.web;

import com.cephalononni.catalog.CatalogImportService;
import com.cephalononni.catalog.CatalogSettingsService;
import com.cephalononni.security.CurrentUser;
import com.cephalononni.web.dto.CatalogDtos.ImportStatus;
import com.cephalononni.web.dto.CatalogDtos.SourceCheck;
import com.cephalononni.web.dto.CatalogDtos.SourceSetting;
import com.cephalononni.web.dto.CatalogDtos.UpdateSourcesRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * Static catalog administration: the importer's source URLs and manual imports. Guarded by
 * SecurityConfig's `hasRole("ADMINISTRATOR")` on /api/admin/**, like AdminController.
 */
@RestController
@RequestMapping("/api/admin/catalog")
public class CatalogAdminController {

    private final CatalogSettingsService settingsService;
    private final CatalogImportService importService;

    public CatalogAdminController(CatalogSettingsService settingsService, CatalogImportService importService) {
        this.settingsService = settingsService;
        this.importService = importService;
    }

    @GetMapping("/settings")
    public List<SourceSetting> getSettings() {
        return settingsService.sources();
    }

    /** A null or blank URL resets it to its default; any invalid URL rejects the whole update. */
    @PutMapping("/settings")
    public List<SourceSetting> updateSettings(@AuthenticationPrincipal CurrentUser admin,
                                              @RequestBody UpdateSourcesRequest request) {
        return settingsService.updateSources(request, admin.id());
    }

    /** Starts an import in the background (202); poll GET /status for the outcome. */
    @PostMapping("/import")
    public ResponseEntity<ImportStatus> startImport(@RequestParam(defaultValue = "false") boolean force) {
        importService.startAsync(force, "admin");
        return ResponseEntity.accepted().body(importService.status());
    }

    /** Dry run: fetch + parse + validate every source with the current URLs; writes nothing. */
    @PostMapping("/check")
    public SourceCheck checkSources() {
        return importService.checkSources();
    }

    @GetMapping("/status")
    public ImportStatus status() {
        return importService.status();
    }
}
