package com.careernavigator.entity;

import jakarta.persistence.*;
import lombok.*;

/**
 * RoadmapMilestone Entity
 * Maps to 'roadmap_milestones' table
 * Each milestone = one month of learning
 */
@Entity
@Table(name = "roadmap_milestones")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class RoadmapMilestone {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Which roadmap this belongs to
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "roadmap_id", nullable = false)
    @com.fasterxml.jackson.annotation.JsonIgnore
    private Roadmap roadmap;

    // Month number eg 1, 2, 3
    @Column(nullable = false)
    private Integer monthNumber;

    // Title eg "HTML & CSS Basics"
    @Column(nullable = false)
    private String title;

    // What to learn this month
    @Column(columnDefinition = "TEXT")
    private String description;

    // Specific topics to cover
    @Column(columnDefinition = "TEXT")
    private String topics;

    // Free resources to use
    @Column(columnDefinition = "TEXT")
    private String resources;

    // Project to build this month
    @Column
    private String projectIdea;

    // Estimated hours needed
    @Column
    private Integer estimatedHours;

    // Is this milestone completed?
    @Column(nullable = false)
    private Boolean isCompleted;

    // Milestone status
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private MilestoneStatus status;

    public enum MilestoneStatus {
        LOCKED,
        ACTIVE,
        COMPLETED
    }
}