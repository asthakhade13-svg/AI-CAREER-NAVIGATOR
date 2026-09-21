package com.careernavigator.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;

import java.util.Arrays;
import java.util.List;

/**
 * CorsConfig
 * Fixes CORS error between frontend and backend
 */
@Configuration
public class CorsConfig {

    @Bean
    public CorsFilter corsFilter() {

        CorsConfiguration config =
                new CorsConfiguration();

        // Allow ALL origins
        config.setAllowedOriginPatterns(
                List.of("*")
        );

        // Allow specific origins
        config.setAllowedOrigins(Arrays.asList(
                "http://localhost:5500",
                "http://localhost:5501",
                "http://127.0.0.1:5500",
                "http://127.0.0.1:5501",
                "http://localhost:3000",
                "null"
        ));

        // Allow all methods
        config.setAllowedMethods(Arrays.asList(
                "GET", "POST", "PUT",
                "DELETE", "OPTIONS", "PATCH"
        ));

        // Allow all headers
        config.setAllowedHeaders(Arrays.asList(
                "Authorization",
                "Content-Type",
                "Accept",
                "Origin",
                "X-Requested-With"
        ));

        // Expose Authorization header
        config.setExposedHeaders(Arrays.asList(
                "Authorization"
        ));

        // Don't require credentials
        config.setAllowCredentials(false);

        // Cache preflight for 1 hour
        config.setMaxAge(3600L);

        UrlBasedCorsConfigurationSource source =
                new UrlBasedCorsConfigurationSource();

        source.registerCorsConfiguration(
                "/**", config
        );

        return new CorsFilter(source);
    }
}