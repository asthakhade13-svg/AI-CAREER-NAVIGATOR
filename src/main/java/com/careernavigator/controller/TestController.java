package com.careernavigator.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

/**
 * TestController
 * Tests JWT protected endpoints
 * Only accessible with valid JWT token
 */
@RestController
@RequestMapping("/api/v1/test")
public class TestController {

    // PUBLIC endpoint — no token needed
    @GetMapping("/public")
    public ResponseEntity<String> publicEndpoint() {
        return ResponseEntity.ok(
                "This is PUBLIC — anyone can see this!"
        );
    }

    // PROTECTED endpoint — JWT token required
    @GetMapping("/protected")
    public ResponseEntity<Map<String, String>>
    protectedEndpoint(
            @AuthenticationPrincipal
            UserDetails userDetails) {

        Map<String, String> response = new HashMap<>();
        response.put("message",
                "This is PROTECTED — JWT verified!");
        response.put("loggedInUser",
                userDetails.getUsername());
        response.put("role",
                userDetails.getAuthorities()
                        .toString());

        return ResponseEntity.ok(response);
    }
}