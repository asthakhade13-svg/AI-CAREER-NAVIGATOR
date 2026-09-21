package com.careernavigator.controller;

import com.careernavigator.dto.response.ProgressResponse;
import com.careernavigator.service.ProgressService;
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
 * ProgressController
 * Handles student progress tracking APIs
 * All endpoints require JWT token!
 */
@RestController
@RequestMapping(AppConstants.PROGRESS_BASE)
@RequiredArgsConstructor
@Slf4j
public class ProgressController {

    private final ProgressService progressService;

    // ==========================================
    // GET MY PROGRESS DASHBOARD
    // GET /api/v1/progress/dashboard
    // ==========================================
    @GetMapping("/dashboard")
    public ResponseEntity<ProgressResponse>
    getProgressDashboard(
            @AuthenticationPrincipal
            UserDetails userDetails) {

        log.info("Progress dashboard for: {}",
                userDetails.getUsername());

        ProgressResponse response =
                progressService.getProgress(
                        userDetails.getUsername()
                );

        return ResponseEntity.ok(response);
    }

    // ==========================================
    // GET QUICK STATS
    // GET /api/v1/progress/stats
    // ==========================================
    @GetMapping("/stats")
    public ResponseEntity<?> getQuickStats(
            @AuthenticationPrincipal
            UserDetails userDetails) {

        log.info("Quick stats for: {}",
                userDetails.getUsername());

        ProgressResponse response =
                progressService.getProgress(
                        userDetails.getUsername()
                );

        // Return only key stats
        java.util.Map<String, Object> stats =
                new java.util.LinkedHashMap<>();

        stats.put("studentName",
                response.getStudentName());
        stats.put("overallProgress",
                response.getOverallProgress() + "%");
        stats.put("completedMilestones",
                response.getCompletedMilestones());
        stats.put("totalMilestones",
                response.getTotalMilestones());
        stats.put("bestQuizScore",
                response.getBestQuizScore() + "%");
        stats.put("topCareer",
                response.getTopCareerMatch());
        stats.put("totalChatMessages",
                response.getTotalChatMessages());
        stats.put("totalQuizAttempts",
                response.getTotalQuizAttempts());

        return ResponseEntity.ok(stats);
    }
}