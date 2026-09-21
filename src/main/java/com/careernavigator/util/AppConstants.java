package com.careernavigator.util;

/**
 * AppConstants
 * All constant values used across the app
 * Never hardcode strings - put them here!
 */
public class AppConstants {

    // Prevent creating object of this class
    private AppConstants() {}

    // API URL paths
    public static final String API_BASE      = "/api/v1";
    public static final String AUTH_BASE     = API_BASE + "/auth";
    public static final String QUIZ_BASE     = API_BASE + "/quiz";
    public static final String CAREER_BASE   = API_BASE + "/career";
    public static final String ROADMAP_BASE  = API_BASE + "/roadmap";
    public static final String CHAT_BASE     = API_BASE + "/chat";
    public static final String PROGRESS_BASE = API_BASE + "/progress";


//    public static final String PROGRESS_BASE = API_BASE + "/progress";

    // JWT constants
    public static final String TOKEN_PREFIX = "Bearer ";
    public static final String AUTH_HEADER  = "Authorization";

    // Role names
    public static final String ROLE_STUDENT = "STUDENT";
    public static final String ROLE_ADMIN   = "ADMIN";

    // Response messages
    public static final String USER_NOT_FOUND =
            "User not found with email: ";
    public static final String EMAIL_ALREADY_EXISTS =
            "Email already registered: ";
    public static final String INVALID_CREDENTIALS =
            "Invalid email or password";
    public static final String REGISTRATION_SUCCESS =
            "User registered successfully!";
}