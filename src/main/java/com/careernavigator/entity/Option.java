package com.careernavigator.entity;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.*;
import lombok.*;

/**
 * Option Entity
 * Maps to 'options' table in MySQL
 * Each option belongs to one question
 */
@Entity
@Table(name = "options")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Option {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // The option text shown to student
    @Column(nullable = false)
    private String optionText;

    // Is this the correct answer?
    // JsonIgnore = don't send this to frontend!
    // We don't want to cheat!
    @JsonIgnore
    @Column(nullable = false)
    private Boolean isCorrect;

    // Many options belong to one question
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "question_id")
    @JsonIgnore
    private Question question;
}