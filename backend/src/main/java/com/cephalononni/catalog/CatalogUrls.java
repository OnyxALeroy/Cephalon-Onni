package com.cephalononni.catalog;

/** The three upstream locations one catalog import reads from (see CatalogSettingsService). */
public record CatalogUrls(String exportIndexUrl, String exportContentBaseUrl, String dropTablesUrl) {
}
