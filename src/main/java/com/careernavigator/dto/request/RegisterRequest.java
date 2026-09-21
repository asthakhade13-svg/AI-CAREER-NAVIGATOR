package com.careernavigator.dto.request;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * RegisterRequest DTO
 * This is the data student sends
 * when creating a new account
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RegisterRequest {

    // Full name - cannot be empty
    @NotBlank(message = "Full name is required")
    private String fullName;

    // Email - must be valid format
    @NotBlank(message = "Email is required")
    @Email(message = "Please enter a valid email")
    private String email;

    // Password - minimum 6 characters
    @NotBlank(message = "Password is required")
    @Size(min = 6, message = "Password must be at least 6 characters")
    private String password;

    // College name - optional
    private String collegeName;

    // Branch - optional
    private String branch;

    // Current year - optional
    private String currentYear;
}