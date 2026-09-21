package com.careernavigator.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

/**
 * ChatHistory Entity
 * Stores all chat messages between
 * student and AI mentor
 */
@Entity
@Table(name = "chat_history")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ChatHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Which student sent this message
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    @com.fasterxml.jackson.annotation.JsonIgnore
    private User user;

    // Student's question
    @Column(nullable = false, columnDefinition = "TEXT")
    private String userMessage;

    // AI's response
    @Column(nullable = false, columnDefinition = "TEXT")
    private String aiResponse;

    // Type of chat: CAREER, ROADMAP, GENERAL
    @Column
    private String chatType;

    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime createdAt;
}