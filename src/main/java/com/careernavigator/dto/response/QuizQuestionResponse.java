package com.careernavigator.dto.response;

import com.careernavigator.entity.Difficulty;
import com.careernavigator.entity.Topic;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * QuizQuestionResponse
 * What we send to student
 * when they request questions
 * NOTE: isCorrect is NOT included!
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class QuizQuestionResponse {

    private Long id;
    private String questionText;
    private Topic topic;
    private Difficulty difficulty;
    private List<OptionResponse> options;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class OptionResponse {
        private Long id;
        private String optionText;
        // No isCorrect field here!
    }
}