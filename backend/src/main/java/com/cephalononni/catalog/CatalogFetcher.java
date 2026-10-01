package com.cephalononni.catalog;

/** Downloads and parses one full catalog snapshot. Any failure throws: nothing is partial. */
public interface CatalogFetcher {

    CatalogPayload fetch(CatalogUrls urls);
}
