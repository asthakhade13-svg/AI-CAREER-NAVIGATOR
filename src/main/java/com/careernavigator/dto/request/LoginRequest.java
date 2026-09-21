package com.careernavigator.dto.request;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * LoginRequest DTO
 * This is the data student sends
 * when logging into their account
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class LoginRequest {

    // Email address
    @NotBlank(message = "Email is required")
    @Email(message = "Please enter a valid email")
    private String email;

    // Password
    @NotBlank(message = "Password is required")
    private String password;
}
