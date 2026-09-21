package com.careernavigator.service;

import com.careernavigator.dto.request.QuizSubmitRequest;
import com.careernavigator.dto.response.QuizQuestionResponse;
import com.careernavigator.dto.response.QuizResultResponse;
import com.careernavigator.entity.*;
import com.careernavigator.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * QuizService
 * Handles all quiz business logic:
 * - Get questions
 * - Submit answers
 * - Calculate scores
 * - Save results
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class QuizService {

    private final QuestionRepository questionRepository;
    private final QuizAttemptRepository quizAttemptRepository;
    private final OptionRepository optionRepository;
    private final UserRepository userRepository;

    // ==========================================
    // GET ALL QUESTIONS
    // ==========================================
    public List<QuizQuestionResponse> getAllQuestions() {

        log.info("Fetching all quiz questions");

        List<Question> questions =
                questionRepository.findAll();

        // Convert Question entities to DTOs
        // WITHOUT revealing correct answers!
        return questions.stream()
                .map(this::mapToQuestionResponse)
                .collect(Collectors.toList());
    }

    // ==========================================
    // SUBMIT QUIZ
    // ==========================================
    @Transactional
    public QuizResultResponse submitQuiz(
            QuizSubmitRequest request,
            String userEmail) {

        log.info("Processing quiz submission for: {}",
                userEmail);

        // Find the user
        User user = userRepository
                .findByEmail(userEmail)
                .orElseThrow(() ->
                        new RuntimeException(
                                "User not found: " + userEmail
                        )
                );

        // Track scores per topic
        Map<Topic, Integer> topicTotal = new HashMap<>();
        Map<Topic, Integer> topicCorrect = new HashMap<>();

        // Initialize topic counters
        for (Topic topic : Topic.values()) {
            topicTotal.put(topic, 0);
            topicCorrect.put(topic, 0);
        }

        int totalCorrect = 0;
        List<Answer> answerList = new ArrayList<>();

        // Create quiz attempt first
        QuizAttempt attempt = QuizAttempt.builder()
                .user(user)
                .totalQuestions(
                        request.getAnswers().size()
                )
                .completedAt(LocalDateTime.now())
                .build();

        QuizAttempt savedAttempt =
                quizAttemptRepository.save(attempt);

        // Process each answer
        for (QuizSubmitRequest.AnswerRequest ar
                : request.getAnswers()) {

            // Find the question
            Question question = questionRepository
                    .findById(ar.getQuestionId())
                    .orElse(null);

            if (question == null) continue;

            // Find the selected option
            Option selectedOption = optionRepository
                    .findById(ar.getSelectedOptionId())
                    .orElse(null);

            if (selectedOption == null) continue;

            // Check if answer is correct
            boolean isCorrect =
                    selectedOption.getIsCorrect();

            if (isCorrect) {
                totalCorrect++;
                topicCorrect.merge(
                        question.getTopic(), 1,
                        Integer::sum
                );
            }

            topicTotal.merge(
                    question.getTopic(), 1,
                    Integer::sum
            );

            // Save this answer
            Answer answer = Answer.builder()
                    .quizAttempt(savedAttempt)
                    .question(question)
                    .selectedOption(selectedOption)
                    .isCorrect(isCorrect)
                    .build();

            answerList.add(answer);
        }

        // Calculate percentages per topic
        double webDevScore = calcScore(
                topicCorrect.get(Topic.WEB_DEV),
                topicTotal.get(Topic.WEB_DEV)
        );
        double aiMlScore = calcScore(
                topicCorrect.get(Topic.AI_ML),
                topicTotal.get(Topic.AI_ML)
        );
        double dsaScore = calcScore(
                topicCorrect.get(Topic.DSA),
                topicTotal.get(Topic.DSA)
        );
        double cyberScore = calcScore(
                topicCorrect.get(Topic.CYBERSECURITY),
                topicTotal.get(Topic.CYBERSECURITY)
        );
        double cloudScore = calcScore(
                topicCorrect.get(Topic.CLOUD_COMPUTING),
                topicTotal.get(Topic.CLOUD_COMPUTING)
        );

        // Overall score
        double totalScore = request.getAnswers()
                .isEmpty() ? 0 :
                ((double) totalCorrect /
                        request.getAnswers().size()) * 100;

        // Update attempt with scores
        savedAttempt.setTotalScore(totalScore);
        savedAttempt.setWebDevScore(webDevScore);
        savedAttempt.setAiMlScore(aiMlScore);
        savedAttempt.setDsaScore(dsaScore);
        savedAttempt.setCyberScore(cyberScore);
        savedAttempt.setCloudScore(cloudScore);
        savedAttempt.setCorrectAnswers(totalCorrect);
        savedAttempt.setAnswers(answerList);

        quizAttemptRepository.save(savedAttempt);

        log.info(
                "Quiz completed for {}. Score: {}%",
                userEmail,
                totalScore
        );

        // Find top career match
        String topCareer = findTopCareer(
                webDevScore, aiMlScore,
                dsaScore, cyberScore, cloudScore
        );

        return QuizResultResponse.builder()
                .attemptId(savedAttempt.getId())
                .totalQuestions(
                        request.getAnswers().size()
                )
                .correctAnswers(totalCorrect)
                .totalScore(Math.round(totalScore * 10.0)
                        / 10.0)
                .webDevScore(webDevScore)
                .aiMlScore(aiMlScore)
                .dsaScore(dsaScore)
                .cyberScore(cyberScore)
                .cloudScore(cloudScore)
                .topCareerMatch(topCareer)
                .message("Quiz completed successfully!")
                .success(true)
                .build();
    }

    // ==========================================
    // GET QUIZ HISTORY
    // ==========================================
    // ==========================================
// GET QUIZ HISTORY
// ==========================================
    public List<Map<String, Object>> getQuizHistory(
            String userEmail) {

        User user = userRepository
                .findByEmail(userEmail)
                .orElseThrow(() ->
                        new RuntimeException("User not found")
                );

        List<QuizAttempt> attempts =
                quizAttemptRepository
                        .findByUserIdOrderByCreatedAtDesc(
                                user.getId()
                        );

        // Convert to simple map to avoid
        // lazy loading issues
        return attempts.stream()
                .map(attempt -> {
                    Map<String, Object> map =
                            new LinkedHashMap<>();
                    map.put("attemptId",
                            attempt.getId());
                    map.put("totalQuestions",
                            attempt.getTotalQuestions());
                    map.put("correctAnswers",
                            attempt.getCorrectAnswers());
                    map.put("totalScore",
                            attempt.getTotalScore());
                    map.put("webDevScore",
                            attempt.getWebDevScore());
                    map.put("aiMlScore",
                            attempt.getAiMlScore());
                    map.put("dsaScore",
                            attempt.getDsaScore());
                    map.put("cyberScore",
                            attempt.getCyberScore());
                    map.put("cloudScore",
                            attempt.getCloudScore());
                    map.put("completedAt",
                            attempt.getCompletedAt());
                    map.put("createdAt",
                            attempt.getCreatedAt());
                    return map;
                })
                .collect(Collectors.toList());
    }

    // ==========================================
    // PRIVATE HELPER METHODS
    // ==========================================

    // Calculate score percentage for a topic
    private double calcScore(int correct, int total) {
        if (total == 0) return 0.0;
        return Math.round(
                ((double) correct / total) * 100 * 10.0
        ) / 10.0;
    }

    // Find which career has highest score
    private String findTopCareer(
            double web, double ai,
            double dsa, double cyber, double cloud) {

        Map<String, Double> scores = new LinkedHashMap<>();
        scores.put("Web Development", web);
        scores.put("AI / Machine Learning", ai);
        scores.put("Data Structures & Algorithms", dsa);
        scores.put("Cybersecurity", cyber);
        scores.put("Cloud Computing", cloud);

        return scores.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse("Web Development");
    }

    // Convert Question entity to Response DTO
    private QuizQuestionResponse mapToQuestionResponse(
            Question question) {

        List<QuizQuestionResponse.OptionResponse> options =
                question.getOptions().stream()
                        .map(opt ->
                                QuizQuestionResponse
                                        .OptionResponse.builder()
                                        .id(opt.getId())
                                        .optionText(opt.getOptionText())
                                        // isCorrect NOT included!
                                        .build()
                        )
                        .collect(Collectors.toList());

        return QuizQuestionResponse.builder()
                .id(question.getId())
                .questionText(question.getQuestionText())
                .topic(question.getTopic())
                .difficulty(question.getDifficulty())
                .options(options)
                .build();
    }
}