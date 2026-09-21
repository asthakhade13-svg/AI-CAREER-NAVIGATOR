package com.careernavigator.security;

import com.careernavigator.util.AppConstants;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

/**
 * JwtFilter — JWT Authentication Filter
 *
 * Runs on EVERY HTTP request
 * Checks if request has valid JWT token
 * If valid → allows access
 * If invalid/missing → blocks access
 *
 * OncePerRequestFilter = runs exactly
 * once per request (not multiple times)
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class JwtFilter extends OncePerRequestFilter {

    private final JwtUtil jwtUtil;
    private final UserDetailsServiceImpl userDetailsService;

    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain filterChain)
            throws ServletException, IOException {

        // Step 1: Get Authorization header
        final String authHeader =
                request.getHeader(AppConstants.AUTH_HEADER);

        // Step 2: Check if header exists and starts with "Bearer "
        if (authHeader == null ||
                !authHeader.startsWith(
                        AppConstants.TOKEN_PREFIX)) {

            // No token — continue without authentication
            filterChain.doFilter(request, response);
            return;
        }

        // Step 3: Extract token (remove "Bearer " prefix)
        final String jwt = authHeader.substring(7);

        // Step 4: Extract email from token
        final String userEmail;
        try {
            userEmail = jwtUtil.extractUsername(jwt);
        } catch (Exception e) {
            log.error("Invalid JWT token: {}", e.getMessage());
            filterChain.doFilter(request, response);
            return;
        }

        // Step 5: If email found and not already authenticated
        if (userEmail != null &&
                SecurityContextHolder.getContext()
                        .getAuthentication() == null) {

            // Step 6: Load user from database
            UserDetails userDetails =
                    userDetailsService
                            .loadUserByUsername(userEmail);

            // Step 7: Validate token
            if (jwtUtil.isTokenValid(jwt, userDetails)) {

                // Step 8: Create authentication object
                UsernamePasswordAuthenticationToken authToken =
                        new UsernamePasswordAuthenticationToken(
                                userDetails,
                                null,
                                userDetails.getAuthorities()
                        );

                authToken.setDetails(
                        new WebAuthenticationDetailsSource()
                                .buildDetails(request)
                );

                // Step 9: Set authentication in context
                SecurityContextHolder.getContext()
                        .setAuthentication(authToken);

                log.debug("JWT token valid for user: {}",
                        userEmail);
            }
        }

        // Step 10: Continue with request
        filterChain.doFilter(request, response);
    }
}