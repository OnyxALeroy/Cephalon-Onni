package com.cephalononni.web.dto;

/** The single error envelope shape used across every endpoint: {"detail": "..."}. */
public record ErrorResponse(String detail) {
}
