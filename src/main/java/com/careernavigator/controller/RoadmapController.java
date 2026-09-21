package com.careernavigator.controller;

import com.careernavigator.dto.response.RoadmapResponse;
import com.careernavigator.service.RoadmapService;
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
 * RoadmapController
 * Handles roadmap generation and tracking
 * All endpoints require JWT token!
 */
@RestController
@RequestMapping(AppConstants.ROADMAP_BASE)
@RequiredArgsConstructor
@Slf4j
public class RoadmapController {

    private final RoadmapService roadmapService;

    // ==========================================
    // GENERATE ROADMAP
    // POST /api/v1/roadmap/generate
    // ==========================================
    @PostMapping("/generate")
    public ResponseEntity<RoadmapResponse>
    generateRoadmap(
            @AuthenticationPrincipal
            UserDetails userDetails) {

        log.info("Generating roadmap for: {}",
                userDetails.getUsername());

        RoadmapResponse response =
                roadmapService.generateRoadmap(
                        userDetails.getUsername()
                );

        return ResponseEntity.ok(response);
    }

    // ==========================================
    // GET MY ROADMAP
    // GET /api/v1/roadmap/my-roadmap
    // ==========================================
    @GetMapping("/my-roadmap")
    public ResponseEntity<RoadmapResponse>
    getMyRoadmap(
            @AuthenticationPrincipal
            UserDetails userDetails) {

        RoadmapResponse response =
                roadmapService.getMyRoadmap(
                        userDetails.getUsername()
                );

        return ResponseEntity.ok(response);
    }

    // ==========================================
    // COMPLETE MILESTONE
    // PUT /api/v1/roadmap/complete/{milestoneId}
    // ==========================================
    @PutMapping("/complete/{milestoneId}")
    public ResponseEntity<RoadmapResponse>
    completeMilestone(
            @PathVariable Long milestoneId,
            @AuthenticationPrincipal
            UserDetails userDetails) {

        log.info(
                "Completing milestone {} for: {}",
                milestoneId,
                userDetails.getUsername()
        );

        RoadmapResponse response =
                roadmapService.completeMilestone(
                        milestoneId,
                        userDetails.getUsername()
                );

        return ResponseEntity.ok(response);
    }
}