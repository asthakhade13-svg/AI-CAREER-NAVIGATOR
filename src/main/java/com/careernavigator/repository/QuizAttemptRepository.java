package com.careernavigator.repository;

import com.careernavigator.entity.QuizAttempt;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * QuizAttemptRepository
 * Database operations for quiz attempts
 */
@Repository
public interface QuizAttemptRepository
        extends JpaRepository<QuizAttempt, Long> {

    // Get all attempts by a specific user
    List<QuizAttempt> findByUserIdOrderByCreatedAtDesc(
            Long userId
    );

    // Get latest attempt by user
    QuizAttempt findTopByUserIdOrderByCreatedAtDesc(
            Long userId
    );
}