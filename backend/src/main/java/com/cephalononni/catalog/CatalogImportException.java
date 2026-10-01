package com.cephalononni.catalog;

/** A catalog import that must not be applied; the message is shown as-is on the admin page. */
public class CatalogImportException extends RuntimeException {

    public CatalogImportException(String message) {
        super(message);
    }

    public CatalogImportException(String message, Throwable cause) {
        super(message, cause);
    }
}
