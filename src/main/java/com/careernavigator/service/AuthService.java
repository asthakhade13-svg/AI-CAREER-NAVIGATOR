package com.careernavigator.service;

import com.careernavigator.dto.request.LoginRequest;
import com.careernavigator.dto.request.RegisterRequest;
import com.careernavigator.dto.response.AuthResponse;
import com.careernavigator.entity.User;
import com.careernavigator.exception.InvalidCredentialsException;
import com.careernavigator.exception.UserAlreadyExistsException;
import com.careernavigator.repository.UserRepository;
import com.careernavigator.security.JwtUtil;
import com.careernavigator.util.AppConstants;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.List;

/**
 * AuthService — Updated with JWT token generation
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    // ==========================================
    // REGISTER
    // ==========================================
    public AuthResponse register(RegisterRequest request) {

        log.info("Registering new user: {}",
                request.getEmail());

        // Check email already exists
        if (userRepository.existsByEmail(
                request.getEmail())) {
            throw new UserAlreadyExistsException(
                    AppConstants.EMAIL_ALREADY_EXISTS
                            + request.getEmail()
            );
        }

        // Encrypt password
        String encodedPassword = passwordEncoder
                .encode(request.getPassword());

        // Build and save user
        User user = User.builder()
                .fullName(request.getFullName())
                .email(request.getEmail())
                .password(encodedPassword)
                .collegeName(request.getCollegeName())
                .branch(request.getBranch())
                .currentYear(request.getCurrentYear())
                .role(User.Role.STUDENT)
                .build();

        User savedUser = userRepository.save(user);

        log.info("User registered with id: {}",
                savedUser.getId());

        // Generate JWT token for new user
        String token = generateTokenForUser(savedUser);

        return AuthResponse.builder()
                .success(true)
                .message(AppConstants.REGISTRATION_SUCCESS)
                .fullName(savedUser.getFullName())
                .email(savedUser.getEmail())
                .role(savedUser.getRole().name())
                .token(token) // Real token now!
                .build();
    }

    // ==========================================
    // LOGIN
    // ==========================================
    public AuthResponse login(LoginRequest request) {

        log.info("Login attempt: {}", request.getEmail());

        // Find user by email
        User user = userRepository
                .findByEmail(request.getEmail())
                .orElseThrow(() ->
                        new InvalidCredentialsException(
                                AppConstants.INVALID_CREDENTIALS
                        )
                );

        // Check password
        if (!passwordEncoder.matches(
                request.getPassword(),
                user.getPassword())) {
            throw new InvalidCredentialsException(
                    AppConstants.INVALID_CREDENTIALS
            );
        }

        // Generate REAL JWT token
        String token = generateTokenForUser(user);

        log.info("Login successful: {}", user.getEmail());

        return AuthResponse.builder()
                .success(true)
                .message("Login successful!")
                .fullName(user.getFullName())
                .email(user.getEmail())
                .role(user.getRole().name())
                .token(token) // Real JWT token!
                .build();
    }

    // ==========================================
    // HELPER — Generate token for user
    // ==========================================
    private String generateTokenForUser(User user) {

        // Spring Security needs UserDetails object
        UserDetails userDetails =
                new org.springframework.security.core
                        .userdetails.User(
                        user.getEmail(),
                        user.getPassword(),
                        List.of(new SimpleGrantedAuthority(
                                "ROLE_" + user.getRole().name()
                        ))
                );

        return jwtUtil.generateToken(userDetails);
    }
}