package com.careernavigator.exception;

/**
 * UserAlreadyExistsException
 * Thrown when someone tries to register
 * with an email that already exists
 */
public class UserAlreadyExistsException
        extends RuntimeException {

    public UserAlreadyExistsException(String message) {
        super(message);
    }
}