package com.careernavigator.exception;

/**
 * InvalidCredentialsException
 * Thrown when email or password is wrong
 * during login
 */
public class InvalidCredentialsException
        extends RuntimeException {

    public InvalidCredentialsException(String message) {
        super(message);
    }
}