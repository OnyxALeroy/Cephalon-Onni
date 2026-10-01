package com.cephalononni.catalog;

import com.cephalononni.model.AppSetting;
import com.cephalononni.repository.AppSettingRepository;
import com.cephalononni.web.dto.CatalogDtos.SourceSetting;
import com.cephalononni.web.dto.CatalogDtos.UpdateSourcesRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * The catalog importer's source URLs: defaults from application.yml (app.catalog.defaults.*),
 * overridable at runtime from the admin page. Read at the start of every import, so a change
 * applies to the next run without a restart.
 */
@Service
public class CatalogSettingsService {

    public static final String EXPORT_INDEX_URL = "catalog.export-index-url";
    public static final String EXPORT_CONTENT_BASE_URL = "catalog.export-content-base-url";
    public static final String DROP_TABLES_URL = "catalog.drop-tables-url";

    private final AppSettingRepository appSettingRepository;
    private final Map<String, String> defaults = new LinkedHashMap<>();

    public CatalogSettingsService(AppSettingRepository appSettingRepository,
                                  @Value("${app.catalog.defaults.export-index-url}") String exportIndexUrl,
                                  @Value("${app.catalog.defaults.export-content-base-url}") String exportContentBaseUrl,
                                  @Value("${app.catalog.defaults.drop-tables-url}") String dropTablesUrl) {
        this.appSettingRepository = appSettingRepository;
        defaults.put(EXPORT_INDEX_URL, exportIndexUrl);
        defaults.put(EXPORT_CONTENT_BASE_URL, exportContentBaseUrl);
        defaults.put(DROP_TABLES_URL, dropTablesUrl);
    }

    @Transactional(readOnly = true)
    public CatalogUrls effectiveUrls() {
        return new CatalogUrls(effective(EXPORT_INDEX_URL), effective(EXPORT_CONTENT_BASE_URL), effective(DROP_TABLES_URL));
    }

    @Transactional(readOnly = true)
    public List<SourceSetting> sources() {
        return defaults.keySet().stream()
                .map(key -> {
                    Optional<String> override = override(key);
                    return new SourceSetting(key, override.orElse(defaults.get(key)), defaults.get(key), override.isPresent());
                })
                .toList();
    }

    /** Validates every non-blank URL first, so a bad value leaves all three settings untouched. */
    @Transactional
    public List<SourceSetting> updateSources(UpdateSourcesRequest request, Long adminId) {
        Map<String, String> requested = new LinkedHashMap<>();
        requested.put(EXPORT_INDEX_URL, request.exportIndexUrl());
        requested.put(EXPORT_CONTENT_BASE_URL, request.exportContentBaseUrl());
        requested.put(DROP_TABLES_URL, request.dropTablesUrl());

        requested.values().stream()
                .filter(value -> value != null && !value.isBlank())
                .forEach(SourceUrlGuard::requirePublicHttps);

        requested.forEach((key, value) -> {
            if (value == null || value.isBlank()) {
                appSettingRepository.deleteById(key);
                return;
            }
            AppSetting setting = appSettingRepository.findById(key).orElseGet(AppSetting::new);
            setting.setKey(key);
            setting.setValue(value.trim());
            setting.setUpdatedAt(Instant.now());
            setting.setUpdatedByUserId(adminId);
            appSettingRepository.save(setting);
        });
        return sources();
    }

    private String effective(String key) {
        return override(key).orElse(defaults.get(key));
    }

    private Optional<String> override(String key) {
        return appSettingRepository.findById(key).map(AppSetting::getValue);
    }
}
