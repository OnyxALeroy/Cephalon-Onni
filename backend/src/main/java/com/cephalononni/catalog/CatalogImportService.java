package com.cephalononni.catalog;

import com.cephalononni.exception.ApiException;
import com.cephalononni.web.dto.CatalogDtos.ImportStatus;
import com.cephalononni.web.dto.CatalogDtos.LastRun;
import com.cephalononni.web.dto.CatalogDtos.SourceCheck;
import com.cephalononni.web.dto.CatalogDtos.TablePreview;
import com.cephalononni.web.dto.CatalogDtos.TableCounts;
import jakarta.annotation.PreDestroy;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Runs catalog imports: fetch (CatalogFetcher) then write (CatalogImporter), one at a time.
 *
 * Triggers: the admin page (POST /api/admin/catalog/import), startup when the catalog is empty
 * (app.catalog.import-if-empty), and an optional cron (app.catalog.refresh-cron, off by default).
 * Imports run on a dedicated background thread; the last run's outcome is kept in memory for the
 * admin page and logged.
 */
@Service
public class CatalogImportService {

    private static final Logger log = LoggerFactory.getLogger(CatalogImportService.class);

    private final CatalogSettingsService settingsService;
    private final CatalogFetcher fetcher;
    private final CatalogImporter importer;
    private final JdbcTemplate jdbcTemplate;
    private final boolean importIfEmpty;

    private final AtomicBoolean running = new AtomicBoolean(false);
    private final ExecutorService executor = Executors.newSingleThreadExecutor(runnable -> {
        Thread thread = new Thread(runnable, "catalog-import");
        thread.setDaemon(true);
        return thread;
    });
    private volatile LastRun lastRun;

    public CatalogImportService(CatalogSettingsService settingsService, CatalogFetcher fetcher,
                                CatalogImporter importer, JdbcTemplate jdbcTemplate,
                                @Value("${app.catalog.import-if-empty:true}") boolean importIfEmpty) {
        this.settingsService = settingsService;
        this.fetcher = fetcher;
        this.importer = importer;
        this.jdbcTemplate = jdbcTemplate;
        this.importIfEmpty = importIfEmpty;
    }

    public ImportStatus status() {
        return new ImportStatus(running.get(), lastRun);
    }

    /**
     * Dry run: fetches and parses every source with the current URLs and validates the result
     * the way an import would, without writing. Runs on the caller's thread (~10 s). Source
     * problems are reported in the result rather than thrown.
     */
    public SourceCheck checkSources() {
        Instant startedAt = Instant.now();
        CatalogUrls urls = settingsService.effectiveUrls();
        Map<String, String> urlMap = new LinkedHashMap<>();
        urlMap.put("exportIndexUrl", urls.exportIndexUrl());
        urlMap.put("exportContentBaseUrl", urls.exportContentBaseUrl());
        urlMap.put("dropTablesUrl", urls.dropTablesUrl());

        Map<String, Integer> exports = new LinkedHashMap<>();
        Map<String, Integer> dropsByType = new TreeMap<>();
        try {
            CatalogPayload payload = fetcher.fetch(urls);
            payload.exports().forEach((name, items) -> exports.put(name, items.size()));
            payload.drops().forEach(drop -> dropsByType.merge(drop.sourceType(), 1, Integer::sum));
            List<TablePreview> tables = importer.preview(payload);
            return new SourceCheck(true, null, startedAt, elapsedMs(startedAt), urlMap, exports, dropsByType, tables);
        } catch (RuntimeException e) {
            String message = e.getMessage() == null ? e.getClass().getSimpleName() : e.getMessage();
            log.warn("Catalog source check failed: {}", message);
            return new SourceCheck(false, message, startedAt, elapsedMs(startedAt), urlMap, exports, dropsByType, List.of());
        }
    }

    private static long elapsedMs(Instant startedAt) {
        return Instant.now().toEpochMilli() - startedAt.toEpochMilli();
    }

    /** Starts an import in the background; 409 if one is already running. */
    public void startAsync(boolean force, String trigger) {
        acquire();
        executor.submit(() -> {
            try {
                run(force, trigger);
            } catch (RuntimeException e) {
                // Already recorded in lastRun and logged by run().
            }
        });
    }

    /** Runs an import on the calling thread and rethrows its failure; 409 if one is already running. */
    public List<TableCounts> runNow(boolean force, String trigger) {
        acquire();
        return run(force, trigger);
    }

    @EventListener(ApplicationReadyEvent.class)
    public void importIfCatalogEmpty() {
        if (!importIfEmpty) {
            return;
        }
        Integer warframes = jdbcTemplate.queryForObject("SELECT count(*) FROM warframes", Integer.class);
        if (warframes != null && warframes == 0) {
            log.info("Static catalog is empty; starting the initial import");
            startIfIdle("bootstrap");
        }
    }

    @Scheduled(cron = "${app.catalog.refresh-cron:-}")
    public void scheduledRefresh() {
        startIfIdle("schedule");
    }

    @PreDestroy
    void shutdown() {
        executor.shutdownNow();
    }

    private void startIfIdle(String trigger) {
        try {
            startAsync(false, trigger);
        } catch (ApiException e) {
            log.info("Skipping {} catalog import: another import is running", trigger);
        }
    }

    private void acquire() {
        if (!running.compareAndSet(false, true)) {
            throw ApiException.conflict("A catalog import is already running");
        }
    }

    /** Caller must hold the running flag; releases it. */
    private List<TableCounts> run(boolean force, String trigger) {
        Instant startedAt = Instant.now();
        log.info("Catalog import started (trigger={}, force={})", trigger, force);
        try {
            CatalogPayload payload = fetcher.fetch(settingsService.effectiveUrls());
            List<TableCounts> counts = importer.importCatalog(payload, force);
            lastRun = new LastRun(trigger, force, startedAt, Instant.now(), true, null, counts);
            log.info("Catalog import finished in {} s", (Instant.now().toEpochMilli() - startedAt.toEpochMilli()) / 1000);
            return counts;
        } catch (RuntimeException e) {
            String message = e.getMessage() == null ? e.getClass().getSimpleName() : e.getMessage();
            lastRun = new LastRun(trigger, force, startedAt, Instant.now(), false, message, List.of());
            log.error("Catalog import failed (trigger={}); the catalog was left unchanged", trigger, e);
            throw e;
        } finally {
            running.set(false);
        }
    }
}
