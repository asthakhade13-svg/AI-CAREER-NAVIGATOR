package com.careernavigator.repository;

import com.careernavigator.entity.Roadmap;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * RoadmapRepository
 * Database operations for roadmaps
 */
@Repository
public interface RoadmapRepository
        extends JpaRepository<Roadmap, Long> {

    // Get all roadmaps for a user
    List<Roadmap> findByUserIdOrderByCreatedAtDesc(
            Long userId
    );

    // Get roadmap by user and career name
    Optional<Roadmap> findByUserIdAndCareerName(
            Long userId,
            String careerName
    );

    // Delete roadmap by user id
    void deleteByUserId(Long userId);
}