package com.careernavigator.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Question Entity
 * Maps to 'questions' table in MySQL
 * Each question has multiple options
 */
@Entity
@Table(name = "questions")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Question {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // The actual question text
    @Column(nullable = false, columnDefinition = "TEXT")
    private String questionText;

    // Which topic this question belongs to
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Topic topic;

    // Easy, Medium or Hard
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Difficulty difficulty;

    // One question has many options
    // CascadeType.ALL = if question deleted,
    // options also deleted
    @OneToMany(
            mappedBy = "question",
            cascade = CascadeType.ALL,
            fetch = FetchType.EAGER
    )
    private List<Option> options;

    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime createdAt;
}