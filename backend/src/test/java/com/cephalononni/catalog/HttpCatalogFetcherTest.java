package com.cephalononni.catalog;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.Test;
import org.tukaani.xz.LZMA2Options;
import org.tukaani.xz.LZMAOutputStream;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class HttpCatalogFetcherTest {

    private static byte[] json(String text) {
        return text.getBytes(StandardCharsets.UTF_8);
    }

    @Test
    void exportParsingToleratesRawControlCharactersInStrings() {
        JsonNode items = HttpCatalogFetcher.parseExport("ExportWarframes",
                json("{\"ExportWarframes\": [{\"uniqueName\": \"/A\", \"description\": \"line\r\nbreak\"}]}"));
        assertThat(items.get(0).get("description").asText()).isEqualTo("line\r\nbreak");
    }

    @Test
    void exportIsUnwrappedByNameEvenNextToSiblingArrays() {
        JsonNode items = HttpCatalogFetcher.parseExport("ExportWeapons",
                json("{\"ExportWeapons\": [{\"uniqueName\": \"/W\"}], \"ExportRailjackWeapons\": [{}, {}]}"));
        assertThat(items).hasSize(1);
    }

    @Test
    void manifestIsUnwrappedFromItsSingleKey() {
        JsonNode items = HttpCatalogFetcher.parseExport("ExportManifest", json("{\"Manifest\": [{}, {}]}"));
        assertThat(items).hasSize(2);
    }

    @Test
    void anExportWithoutAnItemArrayFails() {
        assertThatThrownBy(() -> HttpCatalogFetcher.parseExport("ExportRegions", json("{\"a\": 1, \"b\": 2}")))
                .isInstanceOf(CatalogImportException.class);
        assertThatThrownBy(() -> HttpCatalogFetcher.parseExport("ExportRegions", json("not json")))
                .isInstanceOf(CatalogImportException.class);
    }

    @Test
    void indexIsDecompressedAndLooksUpHashedFileNames() throws IOException {
        String index = "ExportWarframes_en.json!00_4rhgqA3T\r\nExportManifest.json!00_Zz-GsBro\r\n\r\n";
        ByteArrayOutputStream compressed = new ByteArrayOutputStream();
        try (LZMAOutputStream out = new LZMAOutputStream(compressed, new LZMA2Options(), -1)) {
            out.write(index.getBytes(StandardCharsets.UTF_8));
        }

        List<String> lines = HttpCatalogFetcher.parseIndex(compressed.toByteArray());

        assertThat(lines).containsExactly("ExportWarframes_en.json!00_4rhgqA3T", "ExportManifest.json!00_Zz-GsBro");
        assertThat(HttpCatalogFetcher.findInIndex(lines, "ExportWarframes")).isEqualTo("ExportWarframes_en.json!00_4rhgqA3T");
        assertThat(HttpCatalogFetcher.findInIndex(lines, "ExportManifest")).isEqualTo("ExportManifest.json!00_Zz-GsBro");
        assertThatThrownBy(() -> HttpCatalogFetcher.findInIndex(lines, "ExportWeapons"))
                .isInstanceOf(CatalogImportException.class);
    }
}
