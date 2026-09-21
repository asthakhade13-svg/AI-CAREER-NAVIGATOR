package com.careernavigator.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * AuthResponse DTO
 * This is what we send BACK to the student
 * after registration or login
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class AuthResponse {

    // JWT token for authentication
    private String token;

    // Success or error message
    private String message;

    // User details to show on frontend
    private String fullName;
    private String email;
    private String role;

    // Was the request successful?
    private boolean success;
}