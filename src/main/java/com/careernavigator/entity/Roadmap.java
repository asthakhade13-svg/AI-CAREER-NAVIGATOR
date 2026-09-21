package com.careernavigator.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;
import java.util.List;

/**
 * Roadmap Entity
 * Maps to 'roadmaps' table in MySQL
 * Stores personalized learning roadmap
 * for each student
 */
@Entity
@Table(name = "roadmaps")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Roadmap {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Which student owns this roadmap
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    @com.fasterxml.jackson.annotation.JsonIgnore
    private User user;

    // Career this roadmap is for
    @Column(nullable = false)
    private String careerName;

    // Total duration eg "6 months"
    @Column
    private String totalDuration;

    // Difficulty level
    @Column
    private String difficultyLevel;

    // Current status
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private RoadmapStatus status;

    // Overall completion percentage
    @Column
    private Double completionPercentage;

    // All milestones in this roadmap
    @OneToMany(
            mappedBy = "roadmap",
            cascade = CascadeType.ALL,
            fetch = FetchType.EAGER
    )
    @OrderBy("monthNumber ASC")
    private List<RoadmapMilestone> milestones;

    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    // Roadmap status options
    public enum RoadmapStatus {
        NOT_STARTED,
        IN_PROGRESS,
        COMPLETED
    }
}