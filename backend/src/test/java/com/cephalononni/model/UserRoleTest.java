package com.cephalononni.model;

import org.junit.jupiter.api.Test;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;

class UserRoleTest {

    @Test
    void wireValuesMatchTheOldBackendsExactStrings() {
        assertThat(UserRole.TRAVELLER.getWireValue()).isEqualTo("Traveller");
        assertThat(UserRole.TENNO.getWireValue()).isEqualTo("Tenno");
        assertThat(UserRole.ADMINISTRATOR.getWireValue()).isEqualTo("Administrator");
    }

    @Test
    void fromWireValueRoundTripsForEveryRole() {
        for (UserRole role : UserRole.values()) {
            assertThat(UserRole.fromWireValue(role.getWireValue())).isEqualTo(role);
        }
    }

    @Test
    void fromWireValueRejectsAnUnknownRole() {
        assertThrows(IllegalArgumentException.class, () -> UserRole.fromWireValue("SuperAdmin"));
    }
}
