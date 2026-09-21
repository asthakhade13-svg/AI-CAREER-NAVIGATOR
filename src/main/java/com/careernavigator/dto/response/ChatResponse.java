package com.careernavigator.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

/**
 * ChatResponse
 * What we send back after AI responds
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChatResponse {

    private boolean success;
    private String message;
    private String aiResponse;
    private String userMessage;
    private LocalDateTime timestamp;
}