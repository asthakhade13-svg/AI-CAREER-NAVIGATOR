package com.careernavigator.service;

import com.careernavigator.dto.response.ProgressResponse;
import com.careernavigator.entity.*;
import com.careernavigator.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.util.*;
import java.util.stream.Collectors;

/**
 * ProgressService
 * Calculates and returns complete
 * student progress analytics
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class ProgressService {

    private final UserRepository userRepository;
    private final QuizAttemptRepository
            quizAttemptRepository;
    private final CareerRecommendationRepository
            careerRecommendationRepository;
    private final RoadmapRepository roadmapRepository;
    private final RoadmapMilestoneRepository
            milestoneRepository;
    private final ProgressTrackingRepository
            progressTrackingRepository;
    private final ChatHistoryRepository
            chatHistoryRepository;

    // ==========================================
    // GET FULL PROGRESS DASHBOARD
    // ==========================================
    public ProgressResponse getProgress(
            String userEmail) {

        log.info("Getting progress for: {}",
                userEmail);

        // Find user
        User user = userRepository
                .findByEmail(userEmail)
                .orElseThrow(() ->
                        new RuntimeException(
                                "User not found: " + userEmail
                        )
                );

        // Get quiz data
        List<QuizAttempt> quizAttempts =
                quizAttemptRepository
                        .findByUserIdOrderByCreatedAtDesc(
                                user.getId()
                        );

        // Get career recommendations
        List<CareerRecommendation> recommendations =
                careerRecommendationRepository
                        .findByUserIdOrderByRankAsc(
                                user.getId()
                        );

        // Get roadmap
        List<Roadmap> roadmaps =
                roadmapRepository
                        .findByUserIdOrderByCreatedAtDesc(
                                user.getId()
                        );

        // Get progress tracking
        List<ProgressTracking> progressList =
                progressTrackingRepository
                        .findByUserIdOrderByCompletedAtDesc(
                                user.getId()
                        );

        // Get chat history count
        List<com.careernavigator.entity.ChatHistory>
                chatHistory = chatHistoryRepository
                .findByUserIdOrderByCreatedAtDesc(
                        user.getId()
                );

        // Calculate quiz stats
        Double bestScore = quizAttempts.isEmpty()
                ? 0.0
                : quizAttempts.stream()
                .mapToDouble(QuizAttempt::getTotalScore)
                .max()
                .orElse(0.0);

        Double latestScore = quizAttempts.isEmpty()
                ? 0.0
                : quizAttempts.get(0).getTotalScore();

        // Get latest quiz scores per topic
        QuizAttempt latestAttempt = quizAttempts
                .isEmpty() ? null : quizAttempts.get(0);

        // Get career info
        String topCareer = recommendations.isEmpty()
                ? "Not determined yet"
                : recommendations.get(0).getCareerName();

        Double topCareerPct = recommendations.isEmpty()
                ? 0.0
                : recommendations.get(0)
                .getMatchPercentage();

        // Get roadmap progress
        Roadmap currentRoadmap = roadmaps.isEmpty()
                ? null : roadmaps.get(0);

        Double overallProgress = 0.0;
        int totalMilestones = 0;
        int completedMilestones = 0;
        List<ProgressResponse.MilestoneProgress>
                milestoneDetails = new ArrayList<>();

        if (currentRoadmap != null) {
            overallProgress =
                    currentRoadmap
                            .getCompletionPercentage();

            List<RoadmapMilestone> milestones =
                    milestoneRepository
                            .findByRoadmapIdOrderByMonthNumberAsc(
                                    currentRoadmap.getId()
                            );

            totalMilestones = milestones.size();
            completedMilestones = (int) milestones
                    .stream()
                    .filter(m -> Boolean.TRUE
                            .equals(m.getIsCompleted()))
                    .count();

            milestoneDetails = milestones.stream()
                    .map(m ->
                            ProgressResponse.MilestoneProgress
                                    .builder()
                                    .monthNumber(m.getMonthNumber())
                                    .title(m.getTitle())
                                    .isCompleted(m.getIsCompleted())
                                    .status(m.getStatus().name())
                                    .estimatedHours(
                                            m.getEstimatedHours()
                                    )
                                    .build()
                    )
                    .collect(Collectors.toList());
        }

        // Build recent activities
        List<ProgressResponse.ActivityItem> activities =
                buildActivities(
                        quizAttempts,
                        progressList,
                        chatHistory,
                        recommendations,
                        roadmaps
                );

        return ProgressResponse.builder()
                .success(true)
                .message("Progress loaded successfully!")
                .studentName(user.getFullName())
                .studentEmail(user.getEmail())
                .careerPath(topCareer)
                .overallProgress(
                        Math.round(overallProgress * 10.0)
                                / 10.0
                )
                .totalMilestones(totalMilestones)
                .completedMilestones(completedMilestones)
                .remainingMilestones(
                        totalMilestones - completedMilestones
                )
                .totalQuizAttempts(quizAttempts.size())
                .bestQuizScore(
                        Math.round(bestScore * 10.0) / 10.0
                )
                .latestQuizScore(
                        Math.round(latestScore * 10.0) / 10.0
                )
                .webDevScore(
                        latestAttempt != null
                                ? latestAttempt.getWebDevScore()
                                : 0.0
                )
                .aiMlScore(
                        latestAttempt != null
                                ? latestAttempt.getAiMlScore()
                                : 0.0
                )
                .dsaScore(
                        latestAttempt != null
                                ? latestAttempt.getDsaScore()
                                : 0.0
                )
                .cyberScore(
                        latestAttempt != null
                                ? latestAttempt.getCyberScore()
                                : 0.0
                )
                .cloudScore(
                        latestAttempt != null
                                ? latestAttempt.getCloudScore()
                                : 0.0
                )
                .topCareerMatch(topCareer)
                .topCareerMatchPercentage(topCareerPct)
                .totalChatMessages(chatHistory.size())
                .completedRoadmaps(
                        (int) roadmaps.stream()
                                .filter(r -> r.getStatus() ==
                                        Roadmap.RoadmapStatus
                                                .COMPLETED)
                                .count()
                )
                .recentActivities(activities)
                .milestoneProgress(milestoneDetails)
                .build();
    }

    // ==========================================
    // BUILD RECENT ACTIVITIES LIST
    // ==========================================
    private List<ProgressResponse.ActivityItem>
    buildActivities(
            List<QuizAttempt> quizAttempts,
            List<ProgressTracking> progressList,
            List<com.careernavigator.entity.ChatHistory>
                    chatHistory,
            List<CareerRecommendation> recommendations,
            List<Roadmap> roadmaps) {

        List<ProgressResponse.ActivityItem> activities =
                new ArrayList<>();

        // Add quiz attempts
        for (QuizAttempt attempt : quizAttempts) {
            activities.add(
                    ProgressResponse.ActivityItem.builder()
                            .type("QUIZ")
                            .description(
                                    "Completed skill assessment quiz" +
                                            " — Score: " +
                                            Math.round(
                                                    attempt.getTotalScore()
                                            ) + "%"
                            )
                            .icon("🧠")
                            .timeAgo(
                                    getTimeAgo(attempt.getCreatedAt())
                            )
                            .createdAt(
                                    formatDate(attempt.getCreatedAt())
                            )
                            .build()
            );
        }

        // Add milestone completions
        for (ProgressTracking p : progressList) {
            activities.add(
                    ProgressResponse.ActivityItem.builder()
                            .type("MILESTONE")
                            .description(p.getNotes())
                            .icon("✅")
                            .timeAgo(
                                    getTimeAgo(p.getCompletedAt())
                            )
                            .createdAt(
                                    formatDate(p.getCompletedAt())
                            )
                            .build()
            );
        }

        // Add career recommendations
        if (!recommendations.isEmpty()) {
            activities.add(
                    ProgressResponse.ActivityItem.builder()
                            .type("CAREER")
                            .description(
                                    "Career recommendations generated" +
                                            " — Top match: " +
                                            recommendations
                                                    .get(0).getCareerName()
                            )
                            .icon("🎯")
                            .timeAgo(
                                    getTimeAgo(
                                            recommendations
                                                    .get(0).getCreatedAt()
                                    )
                            )
                            .createdAt(
                                    formatDate(
                                            recommendations
                                                    .get(0).getCreatedAt()
                                    )
                            )
                            .build()
            );
        }

        // Add roadmap generation
        for (Roadmap r : roadmaps) {
            activities.add(
                    ProgressResponse.ActivityItem.builder()
                            .type("ROADMAP")
                            .description(
                                    "Generated " + r.getCareerName()
                                            + " learning roadmap"
                            )
                            .icon("🗺️")
                            .timeAgo(
                                    getTimeAgo(r.getCreatedAt())
                            )
                            .createdAt(
                                    formatDate(r.getCreatedAt())
                            )
                            .build()
            );
        }

        // Add chat messages count
        if (!chatHistory.isEmpty()) {
            activities.add(
                    ProgressResponse.ActivityItem.builder()
                            .type("CHAT")
                            .description(
                                    "Asked AI mentor " +
                                            chatHistory.size() +
                                            " career questions"
                            )
                            .icon("🤖")
                            .timeAgo(
                                    getTimeAgo(
                                            chatHistory
                                                    .get(0).getCreatedAt()
                                    )
                            )
                            .createdAt(
                                    formatDate(
                                            chatHistory
                                                    .get(0).getCreatedAt()
                                    )
                            )
                            .build()
            );
        }

        // Sort by most recent first
        activities.sort((a, b) ->
                b.getCreatedAt()
                        .compareTo(a.getCreatedAt())
        );

        // Return max 10 activities
        return activities.stream()
                .limit(10)
                .collect(Collectors.toList());
    }

    // ==========================================
    // HELPER — Format time ago
    // ==========================================
    private String getTimeAgo(LocalDateTime dateTime) {
        if (dateTime == null) return "Unknown";

        LocalDateTime now = LocalDateTime.now();
        long minutes = ChronoUnit.MINUTES
                .between(dateTime, now);
        long hours   = ChronoUnit.HOURS
                .between(dateTime, now);
        long days    = ChronoUnit.DAYS
                .between(dateTime, now);

        if (minutes < 1)  return "Just now";
        if (minutes < 60) return minutes + " min ago";
        if (hours < 24)   return hours + " hours ago";
        if (days < 7)     return days + " days ago";
        return days / 7 + " weeks ago";
    }

    // ==========================================
    // HELPER — Format date
    // ==========================================
    private String formatDate(LocalDateTime dateTime) {
        if (dateTime == null) return "";
        return dateTime.format(
                DateTimeFormatter.ofPattern(
                        "yyyy-MM-dd HH:mm:ss"
                )
        );
    }
}