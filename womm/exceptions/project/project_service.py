#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT SERVICE EXCEPTIONS - Project Service Exception Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception classes for project service operations.

Provides specialized exceptions for project detection, validation,
template operations, and VSCode configuration errors.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION CLASSES
# ///////////////////////////////////////////////////////////////


class ProjectServiceError(Exception):
    """Base exception for project service errors."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize project service error.

        Args:
            message: Error message
            operation: Operation that failed
            details: Additional error details
        """
        self.message = message or "Project service error occurred"
        self.operation = operation
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of error."""
        parts = [self.message]
        if self.operation:
            parts.append(f"Operation: {self.operation}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " | ".join(parts)


# ///////////////////////////////////////////////////////////////
# SPECIALIZED EXCEPTION CLASSES
# ///////////////////////////////////////////////////////////////


class ProjectDetectionServiceError(ProjectServiceError):
    """Exception raised when project detection fails."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        project_path: str = "",
        reason: str = "",
        details: str = "",
    ) -> None:
        """Initialize project detection error.

        Args:
            message: Error message
            operation: Operation that failed
            project_path: Path to the project that failed detection
            reason: Reason for failure
            details: Additional error details
        """
        self.project_path = project_path
        self.reason = reason
        super().__init__(message, operation, details)


class TemplateServiceError(ProjectServiceError):
    """Exception raised when template operations fail."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        template_path: str = "",
        reason: str = "",
        details: str = "",
    ) -> None:
        """Initialize template error.

        Args:
            message: Error message
            operation: Operation that failed
            template_path: Path to the template that caused the error
            reason: Reason for failure
            details: Additional error details
        """
        self.template_path = template_path
        self.reason = reason
        super().__init__(message, operation, details)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ProjectDetectionServiceError",
    "ProjectServiceError",
    "TemplateServiceError",
]
