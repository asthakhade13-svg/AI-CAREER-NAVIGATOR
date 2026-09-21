package com.careernavigator.exception;

import com.careernavigator.dto.response.AuthResponse;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.FieldError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.HashMap;
import java.util.Map;

/**
 * GlobalExceptionHandler
 * Catches ALL errors in the app
 * Returns clean error messages
 * instead of ugly stack traces
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    // Handles: Email already registered
    @ExceptionHandler(UserAlreadyExistsException.class)
    public ResponseEntity<AuthResponse> handleUserExists(
            UserAlreadyExistsException ex) {

        return ResponseEntity
                .status(HttpStatus.CONFLICT) // 409
                .body(AuthResponse.builder()
                        .success(false)
                        .message(ex.getMessage())
                        .build());
    }

    // Handles: Wrong email or password
    @ExceptionHandler(InvalidCredentialsException.class)
    public ResponseEntity<AuthResponse> handleInvalidCredentials(
            InvalidCredentialsException ex) {

        return ResponseEntity
                .status(HttpStatus.UNAUTHORIZED) // 401
                .body(AuthResponse.builder()
                        .success(false)
                        .message(ex.getMessage())
                        .build());
    }

    // Handles: Validation errors (@NotBlank, @Email etc)
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, String>> handleValidationErrors(
            MethodArgumentNotValidException ex) {

        Map<String, String> errors = new HashMap<>();

        // Collect all field errors
        ex.getBindingResult()
                .getAllErrors()
                .forEach(error -> {
                    String fieldName =
                            ((FieldError) error).getField();
                    String errorMessage =
                            error.getDefaultMessage();
                    errors.put(fieldName, errorMessage);
                });

        return ResponseEntity
                .status(HttpStatus.BAD_REQUEST) // 400
                .body(errors);
    }

    // Handles: Any other unexpected error
    @ExceptionHandler(Exception.class)
    public ResponseEntity<AuthResponse> handleGenericException(
            Exception ex) {

        return ResponseEntity
                .status(HttpStatus.INTERNAL_SERVER_ERROR) // 500
                .body(AuthResponse.builder()
                        .success(false)
                        .message("Something went wrong: "
                                + ex.getMessage())
                        .build());
    }
}