package com.careernavigator.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * CareerRecommendationResponse
 * What we send back to student
 * after generating recommendations
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CareerRecommendationResponse {

    private boolean success;
    private String message;

    // Student info
    private String studentName;
    private String studentEmail;

    // Quiz scores summary
    private Double totalScore;
    private Double webDevScore;
    private Double aiMlScore;
    private Double dsaScore;
    private Double cyberScore;
    private Double cloudScore;

    // Top career recommendation
    private String topCareer;
    private Double topCareerMatch;

    // All recommendations ranked
    private List<CareerDetail> recommendations;

    /**
     * Individual career detail
     */
    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CareerDetail {
        private Integer rank;
        private String careerName;
        private Double matchPercentage;
        private String reason;
        private String requiredSkills;
        private String salaryRange;
        private String difficultyLevel;
        private String timeToLearn;
        private String emoji;
    }
}