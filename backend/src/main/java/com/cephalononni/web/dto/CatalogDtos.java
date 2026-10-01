package com.cephalononni.web.dto;

import java.time.Instant;
import java.util.List;
import java.util.Map;

public final class CatalogDtos {

    private CatalogDtos() {}

    /** One catalog source URL as shown on the admin page. */
    public record SourceSetting(String key, String value, String defaultValue, boolean overridden) {
    }

    /** A null or blank field resets that URL to its default. */
    public record UpdateSourcesRequest(String exportIndexUrl, String exportContentBaseUrl, String dropTablesUrl) {
    }

    public record TableCounts(String table, int inserted, int updated, int deleted, int skipped) {
    }

    public record LastRun(String trigger, boolean force, Instant startedAt, Instant finishedAt,
                          boolean success, String error, List<TableCounts> tables) {
    }

    public record ImportStatus(boolean running, LastRun lastRun) {
    }

    /** One table in a dry run: rows now, rows an import would leave, and whether the guard trips. */
    public record TablePreview(String table, int current, int incoming, boolean wouldShrinkBelowGuard) {
    }

    /**
     * Result of fetching and validating all catalog sources without writing anything. {@code ok}
     * false means an import would fail right now; {@code error} says why.
     */
    public record SourceCheck(boolean ok, String error, Instant checkedAt, long durationMs,
                              Map<String, String> urls, Map<String, Integer> exports,
                              Map<String, Integer> dropsByType, List<TablePreview> tables) {
    }
}
