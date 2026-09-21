package com.careernavigator.service;

import com.careernavigator.config.GeminiConfig;
import com.careernavigator.dto.request.ChatRequest;
import com.careernavigator.dto.response.ChatResponse;
import com.careernavigator.entity.ChatHistory;
import com.careernavigator.entity.User;
import com.careernavigator.repository.ChatHistoryRepository;
import com.careernavigator.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.time.LocalDateTime;
import java.util.*;

/**
 * GeminiService
 * Handles all AI chat functionality
 * Calls Google Gemini API
 * Saves chat history to database
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class GeminiService {

    private final GeminiConfig geminiConfig;
    private final RestTemplate restTemplate;
    private final ChatHistoryRepository chatHistoryRepository;
    private final UserRepository userRepository;

    // System prompt — tells Gemini how to behave
    private static final String SYSTEM_PROMPT =
            "You are CareerBot, a friendly AI career mentor " +
                    "for first-generation B.Tech CSE students in India. " +
                    "Your role is to: " +
                    "1. Guide students about tech career paths " +
                    "(Web Dev, AI/ML, Cybersecurity, Data Science, Cloud) " +
                    "2. Give practical actionable advice " +
                    "3. Recommend free learning resources " +
                    "4. Help with resume and interview prep " +
                    "5. Motivate students who feel lost " +
                    "6. Give advice specific to Indian students " +
                    "Keep responses clear, friendly and encouraging. " +
                    "Use simple language. " +
                    "Always give specific next steps.";

    // ==========================================
    // SEND MESSAGE TO GEMINI
    // ==========================================
    public ChatResponse chat(
            ChatRequest request,
            String userEmail) {

        log.info("Chat request from: {}", userEmail);

        // Find user
        User user = userRepository
                .findByEmail(userEmail)
                .orElseThrow(() ->
                        new RuntimeException("User not found")
                );

        // Build prompt with system context
        String fullPrompt = SYSTEM_PROMPT +
                "\n\nStudent question: " +
                request.getMessage();

        // Call Gemini API
        String aiResponse = callGeminiApi(fullPrompt);

        // Save to chat history
        ChatHistory history = ChatHistory.builder()
                .user(user)
                .userMessage(request.getMessage())
                .aiResponse(aiResponse)
                .chatType(
                        request.getChatType() != null
                                ? request.getChatType()
                                : "GENERAL"
                )
                .build();

        chatHistoryRepository.save(history);

        log.info("Chat saved for user: {}", userEmail);

        return ChatResponse.builder()
                .success(true)
                .message("AI response received!")
                .userMessage(request.getMessage())
                .aiResponse(aiResponse)
                .timestamp(LocalDateTime.now())
                .build();
    }

    // ==========================================
    // GET CHAT HISTORY
    // ==========================================
    public List<Map<String, Object>> getChatHistory(
            String userEmail) {

        User user = userRepository
                .findByEmail(userEmail)
                .orElseThrow(() ->
                        new RuntimeException("User not found")
                );

        List<ChatHistory> history =
                chatHistoryRepository
                        .findByUserIdOrderByCreatedAtDesc(
                                user.getId()
                        );

        // Convert to safe map
        List<Map<String, Object>> result =
                new ArrayList<>();

        for (ChatHistory chat : history) {
            Map<String, Object> map =
                    new LinkedHashMap<>();
            map.put("id", chat.getId());
            map.put("userMessage", chat.getUserMessage());
            map.put("aiResponse", chat.getAiResponse());
            map.put("chatType", chat.getChatType());
            map.put("createdAt", chat.getCreatedAt());
            result.add(map);
        }

        return result;
    }

    // ==========================================
    // CALL GEMINI API
    // ==========================================
    private String callGeminiApi(String prompt) {

        try {
            // Build URL with API key
            String url = geminiConfig.getApiUrl()
                    + "?key="
                    + geminiConfig.getApiKey();

            // Build request body
            Map<String, Object> requestBody =
                    new HashMap<>();

            Map<String, Object> content =
                    new HashMap<>();
            Map<String, Object> part =
                    new HashMap<>();

            part.put("text", prompt);
            content.put("parts",
                    List.of(part));
            requestBody.put("contents",
                    List.of(content));

            // Set headers
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(
                    MediaType.APPLICATION_JSON
            );

            HttpEntity<Map<String, Object>> entity =
                    new HttpEntity<>(requestBody, headers);

            // Make API call
            ResponseEntity<Map> response =
                    restTemplate.exchange(
                            url,
                            HttpMethod.POST,
                            entity,
                            Map.class
                    );

            // Extract response text
            return extractResponseText(response.getBody());

        } catch (Exception e) {
            log.error(
                    "Gemini API error: {}",
                    e.getMessage()
            );
            return "I am having trouble connecting " +
                    "right now. Please try again! " +
                    "Error: " + e.getMessage();
        }
    }

    // ==========================================
    // EXTRACT TEXT FROM GEMINI RESPONSE
    // ==========================================
    @SuppressWarnings("unchecked")
    private String extractResponseText(
            Map<String, Object> responseBody) {

        try {
            List<Map<String, Object>> candidates =
                    (List<Map<String, Object>>)
                            responseBody.get("candidates");

            if (candidates != null &&
                    !candidates.isEmpty()) {

                Map<String, Object> firstCandidate =
                        candidates.get(0);

                Map<String, Object> content =
                        (Map<String, Object>)
                                firstCandidate.get("content");

                List<Map<String, Object>> parts =
                        (List<Map<String, Object>>)
                                content.get("parts");

                if (parts != null &&
                        !parts.isEmpty()) {
                    return (String) parts
                            .get(0).get("text");
                }
            }

            return "Sorry I could not generate " +
                    "a response. Please try again!";

        } catch (Exception e) {
            log.error(
                    "Error extracting response: {}",
                    e.getMessage()
            );
            return "Error processing AI response. " +
                    "Please try again!";
        }
    }
}