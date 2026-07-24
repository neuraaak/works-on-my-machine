#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SECURITY SERVICE EXCEPTIONS - Security Service Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Security service exceptions for Works On My Machine.

This module contains custom exceptions used specifically by the security service:
- SecurityValidatorService (womm/services/security/security_validator_service.py)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class SecurityServiceError(Exception):
    """Base exception for all security service errors.

    This is the main exception class for all security service operations.
    Used for general errors like unexpected failures during validation.
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
# COMMAND VALIDATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class CommandValidationError(SecurityServiceError):
    """Exception raised when command validation fails.

    This exception is raised when a command does not pass security validation,
    such as when it's not in the whitelist, contains dangerous patterns, or has
    invalid arguments.
    """

    def __init__(
        self,
        command: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize command validation error.

        Args:
            command: The command that failed validation
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.command = command
        self.reason = reason
        message = f"Command validation failed: {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# PATH VALIDATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class PathValidationError(SecurityServiceError):
    """Exception raised when path validation fails.

    This exception is raised when a file or directory path does not pass
    security validation, such as when it contains dangerous patterns,
    excessive directory traversal, or points to system directories.
    """

    def __init__(
        self,
        path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize path validation error.

        Args:
            path: The path that failed validation
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.path = path
        self.reason = reason
        message = f"Path validation failed: {reason}"
        super().__init__(message, details)
