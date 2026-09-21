package com.careernavigator.repository;

import com.careernavigator.entity.ChatHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * ChatHistoryRepository
 * Database operations for chat history
 */
@Repository
public interface ChatHistoryRepository
        extends JpaRepository<ChatHistory, Long> {

    // Get chat history for a user
    // Latest messages first
    List<ChatHistory> findByUserIdOrderByCreatedAtDesc(
            Long userId
    );

    // Get last 10 messages for context
    List<ChatHistory> findTop10ByUserIdOrderByCreatedAtDesc(
            Long userId
    );
}