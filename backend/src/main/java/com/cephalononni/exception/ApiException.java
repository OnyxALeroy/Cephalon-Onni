package com.cephalononni.exception;

import org.springframework.http.HttpStatus;
import org.springframework.lang.NonNull;

/**
 * Single exception type for all handler/service-level errors. GlobalExceptionHandler turns any
 * instance into the standard `{"detail": "..."}` envelope (see backend-rework-plan.md Phase 3 -
 * "standardize on one error envelope ... applied consistently everywhere").
 */
public class ApiException extends RuntimeException {

    @NonNull
    private final HttpStatus status;

    public ApiException(@NonNull HttpStatus status, String detail) {
        super(detail);
        this.status = status;
    }

    @NonNull
    public HttpStatus getStatus() {
        return status;
    }

    public static ApiException badRequest(String detail) {
        return new ApiException(HttpStatus.BAD_REQUEST, detail);
    }

    public static ApiException unauthorized(String detail) {
        return new ApiException(HttpStatus.UNAUTHORIZED, detail);
    }

    public static ApiException forbidden(String detail) {
        return new ApiException(HttpStatus.FORBIDDEN, detail);
    }

    public static ApiException notFound(String detail) {
        return new ApiException(HttpStatus.NOT_FOUND, detail);
    }

    public static ApiException conflict(String detail) {
        return new ApiException(HttpStatus.CONFLICT, detail);
    }

    public static ApiException serviceUnavailable(String detail) {
        return new ApiException(HttpStatus.SERVICE_UNAVAILABLE, detail);
    }

    public static ApiException internal(String detail) {
        return new ApiException(HttpStatus.INTERNAL_SERVER_ERROR, detail);
    }
}
