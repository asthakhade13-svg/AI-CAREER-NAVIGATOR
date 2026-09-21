package com.careernavigator.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Function;

/**
 * JwtUtil — JWT Token Utility Class
 *
 * Responsibilities:
 * 1. Generate JWT token after login
 * 2. Extract email from token
 * 3. Validate token
 * 4. Check if token is expired
 */
@Component
@Slf4j
public class JwtUtil {

    // Read secret key from application.properties
    @Value("${jwt.secret}")
    private String secretKey;

    // Read expiration from application.properties
    @Value("${jwt.expiration}")
    private long jwtExpiration;

    // ==========================================
    // GENERATE TOKEN
    // ==========================================
    public String generateToken(UserDetails userDetails) {
        return generateToken(new HashMap<>(), userDetails);
    }

    public String generateToken(
            Map<String, Object> extraClaims,
            UserDetails userDetails) {

        log.debug("Generating JWT token for user: {}",
                userDetails.getUsername());

        return Jwts.builder()
                // Extra data to store in token
                .claims(extraClaims)
                // Store email as subject
                .subject(userDetails.getUsername())
                // When token was created
                .issuedAt(new Date(System.currentTimeMillis()))
                // When token expires (24 hours)
                .expiration(new Date(
                        System.currentTimeMillis() + jwtExpiration
                ))
                // Sign with secret key
                .signWith(getSigningKey())
                .compact();
    }

    // ==========================================
    // VALIDATE TOKEN
    // ==========================================
    public boolean isTokenValid(
            String token,
            UserDetails userDetails) {

        final String username = extractUsername(token);

        return (username.equals(
                userDetails.getUsername()))
                && !isTokenExpired(token);
    }

    // ==========================================
    // EXTRACT DATA FROM TOKEN
    // ==========================================

    // Get email from token
    public String extractUsername(String token) {
        return extractClaim(token, Claims::getSubject);
    }

    // Get expiration date from token
    public Date extractExpiration(String token) {
        return extractClaim(token, Claims::getExpiration);
    }

    // Generic method to extract any claim
    public <T> T extractClaim(
            String token,
            Function<Claims, T> claimsResolver) {

        final Claims claims = extractAllClaims(token);
        return claimsResolver.apply(claims);
    }

    // ==========================================
    // PRIVATE HELPER METHODS
    // ==========================================

    private boolean isTokenExpired(String token) {
        return extractExpiration(token)
                .before(new Date());
    }

    private Claims extractAllClaims(String token) {
        return Jwts.parser()
                .verifyWith(getSigningKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    // Create signing key from secret string
    private SecretKey getSigningKey() {
        byte[] keyBytes = secretKey
                .getBytes(StandardCharsets.UTF_8);
        return Keys.hmacShaKeyFor(keyBytes);
    }
}