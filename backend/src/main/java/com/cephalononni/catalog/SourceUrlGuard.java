package com.cephalononni.catalog;

import com.cephalononni.exception.ApiException;

import java.net.Inet6Address;
import java.net.InetAddress;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.UnknownHostException;

/**
 * SSRF guard for the admin-editable catalog source URLs: the server fetches whatever is
 * configured, so only absolute https URLs on public addresses are accepted. Checked when an
 * admin saves a URL and again right before every request (DNS can change in between, and
 * redirect targets are only known at fetch time).
 */
public final class SourceUrlGuard {

    private SourceUrlGuard() {}

    /** Returns the parsed URI, or throws a 400 {@link ApiException} naming what's wrong. */
    public static URI requirePublicHttps(String raw) {
        if (raw == null || raw.isBlank()) {
            throw ApiException.badRequest("URL must not be empty");
        }
        URI uri;
        try {
            uri = new URI(raw.trim());
        } catch (URISyntaxException e) {
            throw ApiException.badRequest("Not a valid URL: " + raw);
        }
        if (!"https".equalsIgnoreCase(uri.getScheme()) || uri.getHost() == null) {
            throw ApiException.badRequest("URL must be an absolute https:// URL: " + raw);
        }
        if (uri.getRawUserInfo() != null) {
            throw ApiException.badRequest("URL must not contain credentials: " + raw);
        }

        InetAddress[] addresses;
        try {
            addresses = InetAddress.getAllByName(uri.getHost());
        } catch (UnknownHostException e) {
            throw ApiException.badRequest("Cannot resolve host: " + uri.getHost());
        }
        for (InetAddress address : addresses) {
            if (isNonPublic(address)) {
                throw ApiException.badRequest("URL host must be a public address: " + uri.getHost());
            }
        }
        return uri;
    }

    private static boolean isNonPublic(InetAddress address) {
        if (address.isAnyLocalAddress() || address.isLoopbackAddress() || address.isLinkLocalAddress()
                || address.isSiteLocalAddress() || address.isMulticastAddress()) {
            return true;
        }
        byte[] bytes = address.getAddress();
        if (address instanceof Inet6Address) {
            return (bytes[0] & 0xFE) == 0xFC; // fc00::/7 unique local
        }
        return (bytes[0] & 0xFF) == 100 && (bytes[1] & 0xC0) == 64; // 100.64.0.0/10 carrier-grade NAT
    }
}
