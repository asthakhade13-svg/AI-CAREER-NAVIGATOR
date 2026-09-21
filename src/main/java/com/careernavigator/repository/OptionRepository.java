package com.careernavigator.repository;

import com.careernavigator.entity.Option;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * OptionRepository
 * Database operations for options
 */
@Repository
public interface OptionRepository
        extends JpaRepository<Option, Long> {
}