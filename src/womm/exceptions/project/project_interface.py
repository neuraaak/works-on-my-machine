#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT INTERFACE EXCEPTIONS - Project Interface Exception Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception classes for project interface operations.

Provides specialized exceptions for project creation, setup, and template operations.
Interfaces catch service exceptions and raise interface exceptions.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION CLASSES
# ///////////////////////////////////////////////////////////////


class ProjectInterfaceError(Exception):
    """Base exception for project interface errors."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize project interface error.

        Args:
            message: Error message
            operation: Operation that failed
            details: Additional error details
        """
        self.message = message or "Project interface error occurred"
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


class CreateInterfaceError(ProjectInterfaceError):
    """Exception raised when project creation fails."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        project_path: str = "",
        project_type: str = "",
        details: str = "",
    ) -> None:
        """Initialize project creation interface error.

        Args:
            message: Error message
            operation: Operation that failed
            project_path: Path to the project that failed creation
            project_type: Type of project that failed creation
            details: Additional error details
        """
        self.project_path = project_path
        self.project_type = project_type
        super().__init__(message, operation, details)


class ProjectDetectionInterfaceError(ProjectInterfaceError):
    """Exception raised when project detection fails."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        project_path: str = "",
        details: str = "",
    ) -> None:
        """Initialize project detection interface error.

        Args:
            message: Error message
            operation: Operation that failed
            project_path: Path to the project that failed detection
            details: Additional error details
        """
        self.project_path = project_path
        super().__init__(message, operation, details)


class SetupInterfaceError(ProjectInterfaceError):
    """Exception raised when project setup fails."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        project_path: str = "",
        project_type: str = "",
        details: str = "",
    ) -> None:
        """Initialize project setup interface error.

        Args:
            message: Error message
            operation: Operation that failed
            project_path: Path to the project that failed setup
            project_type: Type of project that failed setup
            details: Additional error details
        """
        self.project_path = project_path
        self.project_type = project_type
        super().__init__(message, operation, details)


class TemplateInterfaceError(ProjectInterfaceError):
    """Exception raised when template operations fail."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        template_name: str = "",
        details: str = "",
    ) -> None:
        """Initialize template interface error.

        Args:
            message: Error message
            operation: Operation that failed
            template_name: Name of the template that caused the error
            details: Additional error details
        """
        self.template_name = template_name
        super().__init__(message, operation, details)
