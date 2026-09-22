package com.careernavigator.service;

import com.careernavigator.dto.response
        .CareerRecommendationResponse;
import com.careernavigator.entity.*;
import com.careernavigator.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation
        .Transactional;

import java.util.*;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.*;

/**
 * CareerService
 * Smart career recommendation engine
 *
 * Analyzes quiz scores and matches
 * student strengths to career paths using FastAPI ML model
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class CareerService {

    private final CareerRecommendationRepository
            careerRecommendationRepository;
    private final QuizAttemptRepository
            quizAttemptRepository;
    private final UserRepository userRepository;
    private final RestTemplate restTemplate;

    @Value("${ml.backend.url:http://localhost:8000/api/v1}")
    private String mlBackendUrl;

    // ==========================================
    // GENERATE RECOMMENDATIONS FROM LATEST QUIZ
    // ==========================================
    @Transactional
    public CareerRecommendationResponse
    generateRecommendations(String userEmail) {

        log.info(
                "Generating career recommendations for: {}",
                userEmail
        );

        // Find user
        User user = userRepository
                .findByEmail(userEmail)
                .orElseThrow(() ->
                        new RuntimeException(
                                "User not found: " + userEmail
                        )
                );

        // Get latest quiz attempt
        QuizAttempt attempt =
                quizAttemptRepository
                        .findTopByUserIdOrderByCreatedAtDesc(
                                user.getId()
                        );

        if (attempt == null) {
            return CareerRecommendationResponse.builder()
                    .success(false)
                    .message(
                            "Please complete the quiz first!"
                    )
                    .build();
        }

        // Delete old recommendations
        careerRecommendationRepository
                .deleteByUserId(user.getId());

        // Generate new recommendations via ML Engine (with heuristic fallback)
        List<CareerRecommendationResponse.CareerDetail> careers = fetchMlRecommendations(user, attempt);
        if (careers == null || careers.isEmpty()) {
            careers = buildCareerRecommendations(attempt);
        }

        // Save to database
        saveRecommendations(user, attempt, careers);

        // Build response
        return CareerRecommendationResponse.builder()
                .success(true)
                .message(
                        "Career recommendations generated!"
                )
                .studentName(user.getFullName())
                .studentEmail(user.getEmail())
                .totalScore(attempt.getTotalScore())
                .webDevScore(attempt.getWebDevScore())
                .aiMlScore(attempt.getAiMlScore())
                .dsaScore(attempt.getDsaScore())
                .cyberScore(attempt.getCyberScore())
                .cloudScore(attempt.getCloudScore())
                .topCareer(careers.get(0).getCareerName())
                .topCareerMatch(
                        careers.get(0).getMatchPercentage()
                )
                .recommendations(careers)
                .build();
    }

    // ==========================================
    // GET SAVED RECOMMENDATIONS
    // ==========================================
    public CareerRecommendationResponse
    getRecommendations(String userEmail) {

        User user = userRepository
                .findByEmail(userEmail)
                .orElseThrow(() ->
                        new RuntimeException("User not found")
                );

        List<CareerRecommendation> saved =
                careerRecommendationRepository
                        .findByUserIdOrderByRankAsc(
                                user.getId()
                        );

        if (saved.isEmpty()) {
            return CareerRecommendationResponse.builder()
                    .success(false)
                    .message(
                            "No recommendations found. " +
                                    "Please take the quiz first!"
                    )
                    .build();
        }

        // Convert to response
        List<CareerRecommendationResponse.CareerDetail>
                careers = saved.stream()
                .map(rec ->
                        CareerRecommendationResponse
                                .CareerDetail.builder()
                                .rank(rec.getRank())
                                .careerName(rec.getCareerName())
                                .matchPercentage(
                                        rec.getMatchPercentage()
                                )
                                .reason(rec.getReason())
                                .requiredSkills(
                                        rec.getRequiredSkills()
                                )
                                .salaryRange(rec.getSalaryRange())
                                .difficultyLevel(
                                        rec.getDifficultyLevel()
                                )
                                .timeToLearn(rec.getTimeToLearn())
                                .build()
                )
                .collect(Collectors.toList());

        // Get latest quiz attempt for scores
        QuizAttempt attempt =
                quizAttemptRepository
                        .findTopByUserIdOrderByCreatedAtDesc(
                                user.getId()
                        );

        return CareerRecommendationResponse.builder()
                .success(true)
                .message("Recommendations retrieved!")
                .studentName(user.getFullName())
                .studentEmail(user.getEmail())
                .totalScore(
                        attempt != null
                                ? attempt.getTotalScore() : 0
                )
                .webDevScore(
                        attempt != null
                                ? attempt.getWebDevScore() : 0
                )
                .aiMlScore(
                        attempt != null
                                ? attempt.getAiMlScore() : 0
                )
                .dsaScore(
                        attempt != null
                                ? attempt.getDsaScore() : 0
                )
                .cyberScore(
                        attempt != null
                                ? attempt.getCyberScore() : 0
                )
                .cloudScore(
                        attempt != null
                                ? attempt.getCloudScore() : 0
                )
                .topCareer(careers.get(0).getCareerName())
                .topCareerMatch(
                        careers.get(0).getMatchPercentage()
                )
                .recommendations(careers)
                .build();
    }

    // ==========================================
    // FETCH RECOMMENDATIONS FROM FASTAPI ML BACKEND
    // ==========================================
    @SuppressWarnings("unchecked")
    private List<CareerRecommendationResponse.CareerDetail> fetchMlRecommendations(User user, QuizAttempt attempt) {
        try {
            if (restTemplate == null || mlBackendUrl == null) {
                return null;
            }
            String url = mlBackendUrl + "/recommendation/recommend";

            Map<String, Object> quizResults = new HashMap<>();
            quizResults.put("Web Development", attempt.getWebDevScore());
            quizResults.put("AI / Machine Learning", attempt.getAiMlScore());
            quizResults.put("DSA", attempt.getDsaScore());
            quizResults.put("Cybersecurity", attempt.getCyberScore());
            quizResults.put("Cloud Computing", attempt.getCloudScore());

            Map<String, Object> requestBody = new HashMap<>();
            requestBody.put("student_id", user.getEmail());
            requestBody.put("quiz_results", quizResults);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            HttpEntity<Map<String, Object>> entity = new HttpEntity<>(requestBody, headers);

            ResponseEntity<Map> response = restTemplate.exchange(url, HttpMethod.POST, entity, Map.class);
            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                Map<String, Object> body = response.getBody();
                List<Map<String, Object>> recs = (List<Map<String, Object>>) body.get("recommendations");
                if (recs != null && !recs.isEmpty()) {
                    List<CareerRecommendationResponse.CareerDetail> careers = new ArrayList<>();
                    int rank = 1;
                    for (Map<String, Object> rec : recs) {
                        String domain = String.valueOf(rec.get("domain"));
                        double score = 75.0;
                        if (rec.get("score") instanceof Number) {
                            score = ((Number) rec.get("score")).doubleValue();
                        }
                        careers.add(CareerRecommendationResponse.CareerDetail.builder()
                                .rank(rank++)
                                .careerName(domain)
                                .matchPercentage(Math.round(score * 10.0) / 10.0)
                                .reason("Our AI Psychometric ML model recommends " + domain + " based on your verified performance and aptitude profile.")
                                .requiredSkills("Core CS fundamentals, Domain Specialization, Project portfolio")
                                .salaryRange("₹8L – ₹35L per year")
                                .difficultyLevel("Intermediate")
                                .timeToLearn("6–12 months")
                                .emoji("🎯")
                                .build());
                    }
                    log.info("Successfully fetched {} ML recommendations from FastAPI", careers.size());
                    return careers;
                }
            }
        } catch (Exception e) {
            log.warn("FastAPI ML service call failed or offline, falling back to local engine: {}", e.getMessage());
        }
        return null;
    }

    // ==========================================
    // BUILD CAREER RECOMMENDATIONS (Local Engine)
    // ==========================================
    private List<CareerRecommendationResponse.CareerDetail>
    buildCareerRecommendations(
            QuizAttempt attempt) {

        double web   = attempt.getWebDevScore();
        double ai    = attempt.getAiMlScore();
        double dsa   = attempt.getDsaScore();
        double cyber = attempt.getCyberScore();
        double cloud = attempt.getCloudScore();

        List<CareerRecommendationResponse.CareerDetail>
                careers = new ArrayList<>();

        // 1. Web Development
        double webMatch = calculateWebDevMatch(
                web, dsa
        );
        careers.add(
                CareerRecommendationResponse
                        .CareerDetail.builder()
                        .careerName("Web Development")
                        .matchPercentage(webMatch)
                        .reason(buildReason(
                                "Web Development", web, dsa
                        ))
                        .requiredSkills(
                                "HTML, CSS, JavaScript, " +
                                        "React, Node.js, MySQL"
                        )
                        .salaryRange("₹6L – ₹25L per year")
                        .difficultyLevel("Beginner Friendly")
                        .timeToLearn("6–12 months")
                        .emoji("💻")
                        .build()
        );

        // 2. AI / Machine Learning
        double aiMatch = calculateAiMlMatch(ai, dsa);
        careers.add(
                CareerRecommendationResponse
                        .CareerDetail.builder()
                        .careerName("AI / Machine Learning")
                        .matchPercentage(aiMatch)
                        .reason(buildReason(
                                "AI/ML", ai, dsa
                        ))
                        .requiredSkills(
                                "Python, NumPy, Pandas, " +
                                        "Scikit-learn, TensorFlow"
                        )
                        .salaryRange("₹8L – ₹40L per year")
                        .difficultyLevel("Intermediate")
                        .timeToLearn("12–18 months")
                        .emoji("🤖")
                        .build()
        );

        // 3. Data Science
        double dataMatch = calculateDataScienceMatch(
                ai, dsa, web
        );
        careers.add(
                CareerRecommendationResponse
                        .CareerDetail.builder()
                        .careerName("Data Science")
                        .matchPercentage(dataMatch)
                        .reason(buildReason(
                                "Data Science", ai, dsa
                        ))
                        .requiredSkills(
                                "Python, SQL, Pandas, " +
                                        "Statistics, Tableau"
                        )
                        .salaryRange("₹7L – ₹35L per year")
                        .difficultyLevel("Intermediate")
                        .timeToLearn("10–14 months")
                        .emoji("📊")
                        .build()
        );

        // 4. Cybersecurity
        double cyberMatch = calculateCyberMatch(
                cyber, dsa
        );
        careers.add(
                CareerRecommendationResponse
                        .CareerDetail.builder()
                        .careerName("Cybersecurity")
                        .matchPercentage(cyberMatch)
                        .reason(buildReason(
                                "Cybersecurity", cyber, dsa
                        ))
                        .requiredSkills(
                                "Linux, Networking, Python, " +
                                        "Ethical Hacking, Kali Linux"
                        )
                        .salaryRange("₹7L – ₹30L per year")
                        .difficultyLevel("Intermediate")
                        .timeToLearn("8–12 months")
                        .emoji("🔐")
                        .build()
        );

        // 5. Cloud Computing
        double cloudMatch = calculateCloudMatch(
                cloud, dsa
        );
        careers.add(
                CareerRecommendationResponse
                        .CareerDetail.builder()
                        .careerName("Cloud Computing")
                        .matchPercentage(cloudMatch)
                        .reason(buildReason(
                                "Cloud Computing", cloud, dsa
                        ))
                        .requiredSkills(
                                "AWS, Docker, Kubernetes, " +
                                        "Linux, Terraform"
                        )
                        .salaryRange("₹8L – ₹35L per year")
                        .difficultyLevel("Intermediate")
                        .timeToLearn("8–12 months")
                        .emoji("☁️")
                        .build()
        );

        // 6. DevOps
        double devopsMatch = calculateDevOpsMatch(
                cloud, dsa, web
        );
        careers.add(
                CareerRecommendationResponse
                        .CareerDetail.builder()
                        .careerName("DevOps")
                        .matchPercentage(devopsMatch)
                        .reason(buildReason(
                                "DevOps", cloud, dsa
                        ))
                        .requiredSkills(
                                "Linux, Docker, Jenkins, " +
                                        "Git, Kubernetes, CI/CD"
                        )
                        .salaryRange("₹8L – ₹32L per year")
                        .difficultyLevel("Advanced")
                        .timeToLearn("10–14 months")
                        .emoji("⚙️")
                        .build()
        );

        // Sort by match percentage descending
        careers.sort((a, b) ->
                Double.compare(
                        b.getMatchPercentage(),
                        a.getMatchPercentage()
                )
        );

        // Assign ranks
        for (int i = 0; i < careers.size(); i++) {
            careers.get(i).setRank(i + 1);
        }

        return careers;
    }

    // ==========================================
    // MATCH CALCULATION ALGORITHMS
    // ==========================================

    private double calculateWebDevMatch(
            double web, double dsa) {
        // Web dev heavily depends on web score
        double match = (web * 0.70) + (dsa * 0.30);
        return roundScore(Math.min(match + 5, 100));
    }

    private double calculateAiMlMatch(
            double ai, double dsa) {
        // AI/ML needs both AI and DSA skills
        double match = (ai * 0.60) + (dsa * 0.40);
        return roundScore(Math.min(match + 3, 100));
    }

    private double calculateDataScienceMatch(
            double ai, double dsa, double web) {
        // Data Science is mix of AI, DSA, and some web
        double match = (ai * 0.50) +
                (dsa * 0.35) +
                (web * 0.15);
        return roundScore(Math.min(match + 2, 100));
    }

    private double calculateCyberMatch(
            double cyber, double dsa) {
        // Cybersecurity needs cyber knowledge + DSA
        double match = (cyber * 0.65) + (dsa * 0.35);
        return roundScore(Math.min(match + 4, 100));
    }

    private double calculateCloudMatch(
            double cloud, double dsa) {
        // Cloud needs cloud knowledge + DSA
        double match = (cloud * 0.70) + (dsa * 0.30);
        return roundScore(Math.min(match + 3, 100));
    }

    private double calculateDevOpsMatch(
            double cloud, double dsa, double web) {
        // DevOps is mix of cloud, web, DSA
        double match = (cloud * 0.45) +
                (dsa * 0.35) +
                (web * 0.20);
        return roundScore(Math.min(match + 2, 100));
    }

    private double roundScore(double score) {
        return Math.round(score * 10.0) / 10.0;
    }

    // ==========================================
    // BUILD REASON TEXT
    // ==========================================
    private String buildReason(
            String career,
            double primaryScore,
            double dsaScore) {

        String level;
        if (primaryScore >= 80)      level = "excellent";
        else if (primaryScore >= 60) level = "good";
        else if (primaryScore >= 40) level = "moderate";
        else                         level = "developing";

        return String.format(
                "Your %s knowledge is %s (%.0f%%) and " +
                        "your DSA foundation is at %.0f%%. " +
                        "This makes %s a strong career choice for you!",
                career, level,
                primaryScore, dsaScore, career
        );
    }

    // ==========================================
    // SAVE RECOMMENDATIONS TO DATABASE
    // ==========================================
    private void saveRecommendations(
            User user,
            QuizAttempt attempt,
            List<CareerRecommendationResponse
                    .CareerDetail> careers) {

        List<CareerRecommendation> entities =
                careers.stream()
                        .map(career ->
                                CareerRecommendation.builder()
                                        .user(user)
                                        .quizAttempt(attempt)
                                        .careerName(
                                                career.getCareerName()
                                        )
                                        .matchPercentage(
                                                career.getMatchPercentage()
                                        )
                                        .rank(career.getRank())
                                        .reason(career.getReason())
                                        .requiredSkills(
                                                career.getRequiredSkills()
                                        )
                                        .salaryRange(
                                                career.getSalaryRange()
                                        )
                                        .difficultyLevel(
                                                career.getDifficultyLevel()
                                        )
                                        .timeToLearn(
                                                career.getTimeToLearn()
                                        )
                                        .build()
                        )
                        .collect(Collectors.toList());

        careerRecommendationRepository
                .saveAll(entities);

        log.info(
                "Saved {} recommendations for user: {}",
                entities.size(),
                user.getEmail()
        );
    }
}