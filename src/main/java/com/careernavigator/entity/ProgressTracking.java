package com.careernavigator.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * ProgressTracking Entity
 * Maps to 'progress_tracking' table
 * Tracks when student completes milestones
 */
@Entity
@Table(name = "progress_tracking")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ProgressTracking {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Which student
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    @com.fasterxml.jackson.annotation.JsonIgnore
    private User user;

    // Which roadmap
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "roadmap_id")
    @com.fasterxml.jackson.annotation.JsonIgnore
    private Roadmap roadmap;

    // Which milestone completed
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "milestone_id")
    @com.fasterxml.jackson.annotation.JsonIgnore
    private RoadmapMilestone milestone;

    // Notes from student
    @Column(columnDefinition = "TEXT")
    private String notes;

    // When completed
    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime completedAt;
}