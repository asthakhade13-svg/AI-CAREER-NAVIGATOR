package com.careernavigator.entity;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

/**
 * User Entity
 * Maps to 'users' table in MySQL
 * Each field = one column in database
 */
@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder

public class User {
    // Primary Key - auto increment 1,2,3...
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // User's full name
    @Column(nullable = false)
    private String fullName;

    // Email - must be unique
    @Column(nullable = false, unique = true)
    private String email;

    // Password - will be encrypted later
    @Column(nullable = false)
    private String password;

    // College name
    @Column
    private String collegeName;

    // Branch like CSE, IT
    @Column
    private String branch;

    // 1st year, 2nd year etc
    @Column
    private String currentYear;

    // Role - STUDENT or ADMIN
    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Role role;

    // Auto set when created
    @CreationTimestamp
    @Column(updatable = false)
    private LocalDateTime createdAt;

    // Auto updates when changed
    @UpdateTimestamp
    private LocalDateTime updatedAt;

    // Role options
    public enum Role {
        STUDENT,
        ADMIN
    }
}
