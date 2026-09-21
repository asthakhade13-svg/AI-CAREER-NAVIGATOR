package com.careernavigator.controller;

import com.careernavigator.dto.request.LoginRequest;
import com.careernavigator.dto.request.RegisterRequest;
import com.careernavigator.dto.response.AuthResponse;
import com.careernavigator.service.AuthService;
import com.careernavigator.util.AppConstants;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * AuthController
 * Handles HTTP requests for:
 * POST /api/v1/auth/register
 * POST /api/v1/auth/login
 *
 * @RestController = Controller + @ResponseBody
 * @RequestMapping = base URL for all methods
 */
@RestController
@RequestMapping(AppConstants.AUTH_BASE)
@RequiredArgsConstructor
@Slf4j
public class AuthController {

    // AuthService injected automatically
    private final AuthService authService;

    // ==========================================
    // REGISTER ENDPOINT
    // POST /api/v1/auth/register
    // ==========================================
    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(
            @Valid @RequestBody RegisterRequest request) {

        log.info("Register request received for: {}",
                request.getEmail());

        AuthResponse response = authService.register(request);

        return ResponseEntity
                .status(HttpStatus.CREATED) // 201
                .body(response);
    }

    // ==========================================
    // LOGIN ENDPOINT
    // POST /api/v1/auth/login
    // ==========================================
    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(
            @Valid @RequestBody LoginRequest request) {

        log.info("Login request received for: {}",
                request.getEmail());

        AuthResponse response = authService.login(request);

        return ResponseEntity
                .status(HttpStatus.OK) // 200
                .body(response);
    }

    // ==========================================
    // HEALTH CHECK ENDPOINT
    // GET /api/v1/auth/health
    // ==========================================
    @GetMapping("/health")
    public ResponseEntity<String> healthCheck() {
        return ResponseEntity.ok(
                "Career Navigator API is running! 🚀"
        );
    }
}