#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT SERVICE EXCEPTIONS - Context Service Exception Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception classes for context service operations.

Provides specialized exceptions for context menu operations,
registry operations, validation, and script handling errors.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION CLASSES
# ///////////////////////////////////////////////////////////////


class ContextServiceError(Exception):
    """Base exception for context service errors."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize context service error.

        Args:
            message: Error message
            operation: Operation that failed
            details: Additional error details
        """
        self.message = message or "Context service error occurred"
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
# CONTEXT EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class MenuServiceError(ContextServiceError):
    """Exception raised when context menu operations fail."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize context menu error.

        Args:
            message: Error message
            operation: Operation that failed
            details: Additional error details
        """
        super().__init__(message, operation, details)


class ContextUtilityError(ContextServiceError):
    """Exception raised when context utility operations fail."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize context utility error.

        Args:
            message: Error message
            operation: Operation that failed
            details: Additional error details
        """
        super().__init__(message, operation, details)


class ScriptDetectorServiceError(ContextServiceError):
    """Exception raised when script operations fail."""

    def __init__(
        self,
        message: str = "",
        script_path: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize script error.

        Args:
            message: Error message
            script_path: Path to the script that failed
            operation: Operation that failed
            details: Additional error details
        """
        self.script_path = script_path
        super().__init__(message, operation, details)


class IconServiceError(ContextServiceError):
    """Exception raised when icon service operations fail."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        icon_path: str = "",
        details: str = "",
    ) -> None:
        """Initialize icon service error.

        Args:
            message: Error message
            operation: Operation that failed
            icon_path: Path to the icon that caused the error
            details: Additional error details
        """
        self.icon_path = icon_path
        super().__init__(message, operation, details)
