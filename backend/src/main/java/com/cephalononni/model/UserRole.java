package com.cephalononni.model;

/** Mirrors the FastAPI `UserRole` enum — values are the exact wire/DB strings, not Java-cased. */
public enum UserRole {
    TRAVELLER("Traveller"),
    TENNO("Tenno"),
    ADMINISTRATOR("Administrator");

    private final String wireValue;

    UserRole(String wireValue) {
        this.wireValue = wireValue;
    }

    public String getWireValue() {
        return wireValue;
    }

    public static UserRole fromWireValue(String value) {
        for (UserRole role : values()) {
            if (role.wireValue.equals(value)) {
                return role;
            }
        }
        throw new IllegalArgumentException("Unknown role: " + value);
    }
}
