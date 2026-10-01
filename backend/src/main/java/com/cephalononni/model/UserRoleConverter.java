package com.cephalononni.model;

import jakarta.persistence.AttributeConverter;
import jakarta.persistence.Converter;

/**
 * Stores {@link UserRole} as its wire value ("Tenno", "Administrator"): what the legacy backend
 * wrote, what V1's column default is, and what the README's first-admin SQL sets. Plain
 * {@code @Enumerated(STRING)} stored "TENNO"/"ADMINISTRATOR" instead, so neither legacy rows
 * nor a hand-promoted admin could be loaded. Enum-name values are still read, for rows written
 * before this converter existed (V2 also normalizes them).
 */
@Converter
public class UserRoleConverter implements AttributeConverter<UserRole, String> {

    @Override
    public String convertToDatabaseColumn(UserRole role) {
        return role == null ? null : role.getWireValue();
    }

    @Override
    public UserRole convertToEntityAttribute(String value) {
        if (value == null) {
            return null;
        }
        for (UserRole role : UserRole.values()) {
            if (role.getWireValue().equals(value) || role.name().equals(value)) {
                return role;
            }
        }
        throw new IllegalArgumentException("Unknown role in users.role: " + value);
    }
}
