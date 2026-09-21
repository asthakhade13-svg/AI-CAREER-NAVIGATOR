package com.careernavigator.entity;

import jakarta.persistence.*;
import lombok.*;

/**
 * Answer Entity
 * Maps to 'answers' table
 * Stores each answer a student selected
 */
@Entity
@Table(name = "answers")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Answer {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Which quiz attempt this answer belongs to
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(
            name = "quiz_attempt_id",
            nullable = false
    )
    private QuizAttempt quizAttempt;

    // Which question was answered
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "question_id", nullable = false)
    private Question question;

    // Which option student selected
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(
            name = "selected_option_id",
            nullable = false
    )
    private Option selectedOption;

    // Was the answer correct?
    @Column(nullable = false)
    private Boolean isCorrect;
}