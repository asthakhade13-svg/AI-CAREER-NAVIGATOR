package com.careernavigator.controller;

import com.careernavigator.dto.request.ChatRequest;
import com.careernavigator.dto.response.ChatResponse;
import com.careernavigator.service.GeminiService;
import com.careernavigator.util.AppConstants;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation
        .AuthenticationPrincipal;
import org.springframework.security.core.userdetails
        .UserDetails;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * ChatbotController
 * Handles AI mentor chat requests
 * All endpoints require JWT token!
 */
@RestController
@RequestMapping(AppConstants.CHAT_BASE)
@RequiredArgsConstructor
@Slf4j
public class ChatbotController {

    private final GeminiService geminiService;

    // ==========================================
    // SEND MESSAGE TO AI
    // POST /api/v1/chat/message
    // ==========================================
    @PostMapping("/message")
    public ResponseEntity<ChatResponse> sendMessage(
            @Valid @RequestBody ChatRequest request,
            @AuthenticationPrincipal
            UserDetails userDetails) {

        log.info("Chat message from: {}",
                userDetails.getUsername());

        ChatResponse response = geminiService.chat(
                request,
                userDetails.getUsername()
        );

        return ResponseEntity.ok(response);
    }

    // ==========================================
    // GET CHAT HISTORY
    // GET /api/v1/chat/history
    // ==========================================
    @GetMapping("/history")
    public ResponseEntity<List<Map<String, Object>>>
    getChatHistory(
            @AuthenticationPrincipal
            UserDetails userDetails) {

        return ResponseEntity.ok(
                geminiService.getChatHistory(
                        userDetails.getUsername()
                )
        );
    }
}