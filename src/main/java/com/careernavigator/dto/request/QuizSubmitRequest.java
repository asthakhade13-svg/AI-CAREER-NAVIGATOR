package com.careernavigator.dto.request;

import jakarta.validation.constraints.NotEmpty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * QuizSubmitRequest
 * What student sends when submitting quiz
 * Contains list of questionId + selectedOptionId
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class QuizSubmitRequest {

    @NotEmpty(message = "Answers cannot be empty")
    private List<AnswerRequest> answers;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class AnswerRequest {
        private Long questionId;
        private Long selectedOptionId;
    }
}