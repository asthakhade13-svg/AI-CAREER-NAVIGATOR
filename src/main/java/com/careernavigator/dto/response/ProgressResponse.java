package com.careernavigator.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * ProgressResponse
 * Complete progress dashboard data
 * for a student
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProgressResponse {

    private boolean success;
    private String message;

    // Student info
    private String studentName;
    private String studentEmail;
    private String careerPath;

    // Overall stats
    private Double overallProgress;
    private Integer totalMilestones;
    private Integer completedMilestones;
    private Integer remainingMilestones;

    // Quiz stats
    private Integer totalQuizAttempts;
    private Double bestQuizScore;
    private Double latestQuizScore;

    // Skill scores from latest quiz
    private Double webDevScore;
    private Double aiMlScore;
    private Double dsaScore;
    private Double cyberScore;
    private Double cloudScore;

    // Career info
    private String topCareerMatch;
    private Double topCareerMatchPercentage;

    // Activity counts
    private Integer totalChatMessages;
    private Integer completedRoadmaps;

    // Recent activities
    private List<ActivityItem> recentActivities;

    // Milestone details
    private List<MilestoneProgress> milestoneProgress;

    /**
     * Single activity item
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ActivityItem {
        private String type;
        private String description;
        private String icon;
        private String timeAgo;
        private String createdAt;
    }

    /**
     * Milestone progress detail
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class MilestoneProgress {
        private Integer monthNumber;
        private String title;
        private Boolean isCompleted;
        private String status;
        private Integer estimatedHours;
    }
}