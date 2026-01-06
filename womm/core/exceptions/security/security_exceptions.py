#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SECURITY EXCEPTIONS - Security Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Security exceptions for Works On My Machine.

This module contains custom exceptions used specifically by security modules:
- SecurityValidator (womm/core/utils/security/security_validator.py)

Following a pragmatic approach with focused exception types:
1. SecurityUtilityError - Base exception for security utilities
2. ValidationError - Security validation errors
3. CommandValidationError - Command validation errors
4. PathValidationError - Path validation errors
5. FileValidationError - File validation errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class SecurityUtilityError(Exception):
    """Base exception for all security utility errors.

    This is the main exception class for all security utility operations.
    Used for general errors like invalid arguments, unexpected failures, etc.
    """

    def __init__(self, message: str, details: str | None = None) -> None:
        """Initialize the exception with a message and optional details.

        Args:
            message: Human-readable error message
            details: Optional technical details for debugging
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


# ///////////////////////////////////////////////////////////////
# VALIDATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ValidationError(SecurityUtilityError):
    """General security validation errors.

    This exception is raised when general security validation operations fail,
    such as input validation or security checks.
    """

    def __init__(
        self,
        validation_type: str,
        value: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize validation error with specific context.

        Args:
            validation_type: Type of validation being performed (e.g., "input", "security")
            value: The value being validated
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.validation_type = validation_type
        self.value = value
        self.reason = reason
        message = (
            f"Security validation '{validation_type}' failed for '{value}': {reason}"
        )
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# COMMAND VALIDATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class CommandValidationError(SecurityUtilityError):
    """Command validation errors for security operations.

    This exception is raised when command validation operations fail,
    such as validating command safety or checking command permissions.
    """

    def __init__(
        self,
        command: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize command validation error with specific context.

        Args:
            command: The command being validated
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.command = command
        self.reason = reason
        message = f"Command validation failed for '{command}': {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# PATH VALIDATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class PathValidationError(SecurityUtilityError):
    """Path validation errors for security operations.

    This exception is raised when path validation operations fail,
    such as checking path safety or validating file paths.
    """

    def __init__(
        self,
        path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize path validation error with specific context.

        Args:
            path: The path being validated
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.path = path
        self.reason = reason
        message = f"Path validation failed for '{path}': {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# FILE VALIDATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class FileValidationError(SecurityUtilityError):
    """File validation errors for security operations.

    This exception is raised when file validation operations fail,
    such as checking file safety or validating file operations.
    """

    def __init__(
        self,
        file_path: str,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize file validation error with specific context.

        Args:
            file_path: The file being validated
            operation: The operation being performed (e.g., "read", "write", "execute")
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.file_path = file_path
        self.operation = operation
        self.reason = reason
        message = f"File validation {operation} failed for '{file_path}': {reason}"
        super().__init__(message, details)
