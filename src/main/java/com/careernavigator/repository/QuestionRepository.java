package com.careernavigator.repository;

import com.careernavigator.entity.Question;
import com.careernavigator.entity.Topic;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * QuestionRepository
 * Database operations for questions
 */
@Repository
public interface QuestionRepository
        extends JpaRepository<Question, Long> {

    // Get all questions by topic
    List<Question> findByTopic(Topic topic);

    // Count questions by topic
    long countByTopic(Topic topic);
}