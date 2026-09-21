package com.careernavigator.repository;

import com.careernavigator.entity.CareerRecommendation;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * CareerRecommendationRepository
 * Database operations for career recommendations
 */
@Repository
public interface CareerRecommendationRepository
        extends JpaRepository<CareerRecommendation, Long> {

    // Get all recommendations for a user
    // Ordered by rank (best match first)
    List<CareerRecommendation>
    findByUserIdOrderByRankAsc(Long userId);

    // Get recommendations from specific quiz attempt
    List<CareerRecommendation>
    findByQuizAttemptIdOrderByRankAsc(
            Long quizAttemptId
    );

    // Delete old recommendations before saving new
    void deleteByUserId(Long userId);
}