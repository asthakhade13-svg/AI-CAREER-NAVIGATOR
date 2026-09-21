package com.careernavigator.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * CareerRecommendation Entity
 * Maps to 'career_recommendations' table
 * Stores AI-generated career recommendations
 * for each student based on quiz results
 */
@Entity
@Table(name = "career_recommendations")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CareerRecommendation {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Which student this recommendation is for
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    @com.fasterxml.jackson.annotation.JsonIgnore
    private User user;

    // Which quiz attempt generated this
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "quiz_attempt_id")
    @com.fasterxml.jackson.annotation.JsonIgnore
    private QuizAttempt quizAttempt;

    // Career name eg "Web Development"
    @Column(nullable = false)
    private String careerName;

    // Match percentage eg 95.5
    @Column(nullable = false)
    private Double matchPercentage;

    // Rank 1 = best match, 2 = second best etc
    @Column(name = "`rank`", nullable = false)
    private Integer rank;

    // Why this career was recommended
    @Column(columnDefinition = "TEXT")
    private String reason;

    // Key skills needed for this career
    @Column(columnDefinition = "TEXT")
    private String requiredSkills;

    // Estimated salary range
    @Column
    private String salaryRange;

    // Difficulty to enter this field
    @Column
    private String difficultyLevel;

    // How long to become job ready
    @Column
    private String timeToLearn;

    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime createdAt;
}