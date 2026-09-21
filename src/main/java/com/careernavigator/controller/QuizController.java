package com.careernavigator.controller;

import com.careernavigator.dto.request.QuizSubmitRequest;
import com.careernavigator.dto.response.QuizQuestionResponse;
import com.careernavigator.dto.response.QuizResultResponse;
import com.careernavigator.service.QuizService;
import com.careernavigator.util.AppConstants;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

/**
 * QuizController
 * Handles all quiz related HTTP requests
 * All endpoints require JWT token!
 */
@RestController
@RequestMapping(AppConstants.QUIZ_BASE)
@RequiredArgsConstructor
@Slf4j
public class QuizController {

    private final QuizService quizService;

    // ==========================================
    // GET ALL QUESTIONS
    // GET /api/v1/quiz/questions
    // Requires: JWT Token
    // ==========================================
    @GetMapping("/questions")
    public ResponseEntity<List<QuizQuestionResponse>>
    getQuestions() {

        log.info("Fetching all quiz questions");
        List<QuizQuestionResponse> questions =
                quizService.getAllQuestions();

        return ResponseEntity.ok(questions);
    }

    // ==========================================
    // SUBMIT QUIZ
    // POST /api/v1/quiz/submit
    // Requires: JWT Token
    // ==========================================
    @PostMapping("/submit")
    public ResponseEntity<QuizResultResponse> submitQuiz(
            @Valid @RequestBody QuizSubmitRequest request,
            @AuthenticationPrincipal UserDetails userDetails) {

        log.info("Quiz submission from: {}",
                userDetails.getUsername());

        QuizResultResponse result =
                quizService.submitQuiz(
                        request,
                        userDetails.getUsername()
                );

        return ResponseEntity.ok(result);
    }

    // ==========================================
    // GET QUIZ HISTORY
    // GET /api/v1/quiz/history
    // Requires: JWT Token
    // ==========================================
    // ==========================================
// GET QUIZ HISTORY
// GET /api/v1/quiz/history
// ==========================================
    @GetMapping("/history")
    public ResponseEntity<List<Map<String, Object>>>
    getHistory(
            @AuthenticationPrincipal
            UserDetails userDetails) {

        log.info("Fetching quiz history for: {}",
                userDetails.getUsername());

        return ResponseEntity.ok(
                quizService.getQuizHistory(
                        userDetails.getUsername()
                )
        );
    }
}