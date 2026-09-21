package com.careernavigator.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * QuizResultResponse
 * What we send back after quiz submission
 * Contains scores per topic
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class QuizResultResponse {

    private Long attemptId;
    private Integer totalQuestions;
    private Integer correctAnswers;
    private Double totalScore;

    // Score per topic (percentage)
    private Double webDevScore;
    private Double aiMlScore;
    private Double dsaScore;
    private Double cyberScore;
    private Double cloudScore;

    // Top recommended career
    private String topCareerMatch;
    private String message;
    private boolean success;
}