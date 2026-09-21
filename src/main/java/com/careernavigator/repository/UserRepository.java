package com.careernavigator.repository;

import com.careernavigator.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

/**
 * UserRepository
 * All database operations for User table
 * JpaRepository gives us free methods:
 * save(), findById(), findAll(), delete()
 */
@Repository
public interface UserRepository
        extends JpaRepository<User, Long> {

    // Find user by email address
    Optional<User> findByEmail(String email);

    // Check if email already registered
    boolean existsByEmail(String email);
}