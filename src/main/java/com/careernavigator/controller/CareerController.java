package com.careernavigator.controller;

import com.careernavigator.dto.response
        .CareerRecommendationResponse;
import com.careernavigator.service.CareerService;
import com.careernavigator.util.AppConstants;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation
        .AuthenticationPrincipal;
import org.springframework.security.core.userdetails
        .UserDetails;
import org.springframework.web.bind.annotation.*;

/**
 * CareerController
 * Handles career recommendation requests
 * All endpoints require JWT token!
 */
@RestController
@RequestMapping(AppConstants.CAREER_BASE)
@RequiredArgsConstructor
@Slf4j
public class CareerController {

    private final CareerService careerService;

    // ==========================================
    // GENERATE RECOMMENDATIONS
    // POST /api/v1/career/recommend
    // Requires: JWT Token
    // ==========================================
    @PostMapping("/recommend")
    public ResponseEntity<CareerRecommendationResponse>
    generateRecommendations(
            @AuthenticationPrincipal
            UserDetails userDetails) {

        log.info(
                "Generating recommendations for: {}",
                userDetails.getUsername()
        );

        CareerRecommendationResponse response =
                careerService.generateRecommendations(
                        userDetails.getUsername()
                );

        return ResponseEntity.ok(response);
    }

    // ==========================================
    // GET SAVED RECOMMENDATIONS
    // GET /api/v1/career/my-recommendations
    // Requires: JWT Token
    // ==========================================
    @GetMapping("/my-recommendations")
    public ResponseEntity<CareerRecommendationResponse>
    getMyRecommendations(
            @AuthenticationPrincipal
            UserDetails userDetails) {

        log.info(
                "Getting recommendations for: {}",
                userDetails.getUsername()
        );

        CareerRecommendationResponse response =
                careerService.getRecommendations(
                        userDetails.getUsername()
                );

        return ResponseEntity.ok(response);
    }
}