package com.cephalononni.catalog;

import com.fasterxml.jackson.core.json.JsonReadFeature;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.json.JsonMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Component;
import org.tukaani.xz.LZMAInputStream;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.net.ProxySelector;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Fetches the Warframe PublicExport JSONs (via the LZMA-compressed index, which maps each export
 * name to its current hashed file name) and the drop-tables page.
 *
 * Redirects are followed by hand so that every hop goes through {@link SourceUrlGuard}: the
 * default drop-tables URL itself 302s to a CDN, and an automatic redirect would otherwise let an
 * allowed URL bounce the server to an internal address.
 */
@Component
public class HttpCatalogFetcher implements CatalogFetcher {

    private static final Logger log = LoggerFactory.getLogger(HttpCatalogFetcher.class);
    private static final Duration CONNECT_TIMEOUT = Duration.ofSeconds(5);
    private static final Duration REQUEST_TIMEOUT = Duration.ofSeconds(60);
    private static final int MAX_REDIRECTS = 5;

    /**
     * Lenient on purpose: the exports have historically shipped raw control characters inside
     * strings, which strict parsing (the legacy seeder's) rejects - silently skipping the table.
     */
    static final ObjectMapper EXPORT_MAPPER = JsonMapper.builder()
            .enable(JsonReadFeature.ALLOW_UNESCAPED_CONTROL_CHARS)
            .build();

    private final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(CONNECT_TIMEOUT)
            .followRedirects(HttpClient.Redirect.NEVER)
            // Honour -Dhttps.proxyHost & co. like HttpURLConnection does (HttpClient ignores them otherwise).
            .proxy(ProxySelector.getDefault())
            .build();

    @Override
    public CatalogPayload fetch(CatalogUrls urls) {
        List<String> index = parseIndex(get(urls.exportIndexUrl()));

        Map<String, JsonNode> exports = new LinkedHashMap<>();
        for (String exportName : CatalogPayload.REQUIRED_EXPORTS) {
            String fileName = findInIndex(index, exportName);
            JsonNode items = parseExport(exportName, get(urls.exportContentBaseUrl() + fileName));
            log.info("Fetched {} ({} entries)", exportName, items.size());
            exports.put(exportName, items);
        }

        String html = new String(get(urls.dropTablesUrl()), StandardCharsets.UTF_8);
        List<DropTableParser.DropRow> drops = DropTableParser.parse(html);
        log.info("Parsed {} drop rows from the drop tables", drops.size());
        return new CatalogPayload(exports, drops);
    }

    /** The index is LZMA ("alone" format) text, one "ExportX_en.json!00_hash" per CRLF line. */
    static List<String> parseIndex(byte[] compressed) {
        try (InputStream in = new LZMAInputStream(new ByteArrayInputStream(compressed))) {
            return new String(in.readAllBytes(), StandardCharsets.UTF_8).lines()
                    .map(String::trim)
                    .filter(line -> !line.isEmpty())
                    .toList();
        } catch (IOException e) {
            throw new CatalogImportException("Could not decompress the PublicExport index: " + e.getMessage(), e);
        }
    }

    /** ExportManifest is "ExportManifest.json!..."; every other export is "ExportX_<lang>.json!...". */
    static String findInIndex(List<String> index, String exportName) {
        String prefix = exportName.equals("ExportManifest") ? exportName + "." : exportName + "_";
        return index.stream()
                .filter(line -> line.startsWith(prefix))
                .findFirst()
                .orElseThrow(() -> new CatalogImportException("PublicExport index has no entry for " + exportName));
    }

    /**
     * Each file is an object wrapping the item array under the export's own name, possibly next
     * to sibling arrays (ExportWeapons also carries ExportRailjackWeapons); ExportManifest wraps
     * it under "Manifest" alone.
     */
    static JsonNode parseExport(String exportName, byte[] body) {
        JsonNode root;
        try {
            root = EXPORT_MAPPER.readTree(body);
        } catch (IOException e) {
            throw new CatalogImportException(exportName + " is not valid JSON: " + e.getMessage(), e);
        }
        JsonNode items = root;
        if (root != null && root.isObject()) {
            items = root.has(exportName) ? root.get(exportName) : root.size() == 1 ? root.elements().next() : null;
        }
        if (items == null || !items.isArray()) {
            throw new CatalogImportException(exportName + " does not contain an item array");
        }
        return items;
    }

    private byte[] get(String url) {
        URI uri = SourceUrlGuard.requirePublicHttps(url);
        for (int hop = 0; hop <= MAX_REDIRECTS; hop++) {
            HttpResponse<byte[]> response;
            try {
                response = httpClient.send(HttpRequest.newBuilder(uri).timeout(REQUEST_TIMEOUT).GET().build(),
                        HttpResponse.BodyHandlers.ofByteArray());
            } catch (IOException e) {
                throw new UncheckedIOException("GET " + uri + " failed: " + e.getMessage(), e);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new CatalogImportException("Interrupted while fetching " + uri, e);
            }
            int status = response.statusCode();
            if (status >= 300 && status < 400) {
                URI from = uri;
                String location = response.headers().firstValue("Location")
                        .orElseThrow(() -> new CatalogImportException("Redirect without Location from " + from));
                uri = SourceUrlGuard.requirePublicHttps(from.resolve(location).toString());
                continue;
            }
            if (status < 200 || status >= 300) {
                throw new CatalogImportException("GET " + uri + " returned HTTP " + status);
            }
            return response.body();
        }
        throw new CatalogImportException("Too many redirects fetching " + url);
    }
}
