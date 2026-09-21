package com.careernavigator.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;
import java.util.List;
import com.fasterxml.jackson.annotation.JsonIgnore;

/**
 * QuizAttempt Entity
 * Maps to 'quiz_attempts' table
 * Stores one complete quiz attempt by a student
 */
@Entity
@Table(name = "quiz_attempts")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class QuizAttempt {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Which student took this quiz
    @ManyToOne(fetch = FetchType.EAGER)
    @JoinColumn(name = "user_id", nullable = false)
    @JsonIgnore
    private User user;

    // Overall score percentage
    @Column
    private Double totalScore;

    // Score per topic (percentage)
    @Column
    private Double webDevScore;

    @Column
    private Double aiMlScore;

    @Column
    private Double dsaScore;

    @Column
    private Double cyberScore;

    @Column
    private Double cloudScore;

    // Total questions attempted
    @Column
    private Integer totalQuestions;

    // Total correct answers
    @Column
    private Integer correctAnswers;

    // All answers in this attempt
    @OneToMany(
            mappedBy = "quizAttempt",
            cascade = CascadeType.ALL
    )
    private List<Answer> answers;

    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime completedAt;
}