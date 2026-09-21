package com.careernavigator.repository;

import com.careernavigator.entity.RoadmapMilestone;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * RoadmapMilestoneRepository
 * Database operations for milestones
 */
@Repository
public interface RoadmapMilestoneRepository
        extends JpaRepository<RoadmapMilestone, Long> {

    // Get all milestones for a roadmap
    List<RoadmapMilestone> findByRoadmapIdOrderByMonthNumberAsc(
            Long roadmapId
    );

    // Count completed milestones
    long countByRoadmapIdAndIsCompleted(
            Long roadmapId,
            Boolean isCompleted
    );
}