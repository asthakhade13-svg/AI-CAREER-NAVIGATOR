package com.careernavigator.repository;

import com.careernavigator.entity.ProgressTracking;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * ProgressTrackingRepository
 */
@Repository
public interface ProgressTrackingRepository
        extends JpaRepository<ProgressTracking, Long> {

    List<ProgressTracking> findByUserIdOrderByCompletedAtDesc(
            Long userId
    );
}