package com.careernavigator.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * RoadmapResponse
 * Complete roadmap sent to student
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RoadmapResponse {

    private boolean success;
    private String message;
    private Long roadmapId;
    private String careerName;
    private String totalDuration;
    private String difficultyLevel;
    private Double completionPercentage;
    private String status;
    private Integer totalMilestones;
    private Integer completedMilestones;
    private List<MilestoneDetail> milestones;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class MilestoneDetail {
        private Long id;
        private Integer monthNumber;
        private String title;
        private String description;
        private String topics;
        private String resources;
        private String projectIdea;
        private Integer estimatedHours;
        private Boolean isCompleted;
        private String status;
    }
}