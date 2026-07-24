#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# LINT SERVICE EXCEPTIONS - Lint Service Exception Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception classes for linting service operations.

Provides specialized exceptions for linting tool operations, validation,
and execution errors.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION CLASSES
# ///////////////////////////////////////////////////////////////


class LintServiceError(Exception):
    """Base exception for lint service errors."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize lint service error.

        Args:
            message: Error message
            operation: Operation that failed
            details: Additional error details
        """
        self.message = message or "Lint service error occurred"
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


class ToolExecutionServiceError(LintServiceError):
    """Exception raised when linting tool execution fails."""

    def __init__(
        self,
        message: str = "",
        tool_name: str = "",
        operation: str = "",
        reason: str = "",
        details: str = "",
    ) -> None:
        """Initialize tool execution error.

        Args:
            message: Error message
            tool_name: Name of the tool that failed
            operation: Operation that failed
            reason: Reason for failure
            details: Additional error details
        """
        self.tool_name = tool_name
        self.reason = reason
        super().__init__(message, operation, details)


class ToolAvailabilityServiceError(LintServiceError):
    """Exception raised when a linting tool is not available."""

    def __init__(
        self,
        message: str = "",
        tool_name: str = "",
        operation: str = "",
        reason: str = "",
        details: str = "",
    ) -> None:
        """Initialize tool availability error.

        Args:
            message: Error message
            tool_name: Name of the tool that is not available
            operation: Operation that failed
            reason: Reason for failure
            details: Additional error details
        """
        self.tool_name = tool_name
        self.reason = reason
        super().__init__(message, operation, details)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "LintServiceError",
    "ToolAvailabilityServiceError",
    "ToolExecutionServiceError",
]
