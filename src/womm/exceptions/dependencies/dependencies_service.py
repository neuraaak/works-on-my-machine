#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPENDENCIES INTERFACE EXCEPTIONS - Dependencies Interface Exception Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception classes for dependencies interface operations.

This module contains custom exceptions used specifically by the dependencies
interfaces, such as:
- PackageManager (womm/interfaces/dependencies/package_manager.py)
- RuntimeManager (womm/interfaces/dependencies/runtime_manager.py)
- DevToolsManager (womm/interfaces/dependencies/dev_tools_manager.py)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class DependenciesServiceError(Exception):
    """Base exception for all dependencies interface errors.

    This is the main exception class for all dependencies services operations.
    Used for general errors like unexpected failures during services operations.
    """

    def __init__(
        self,
        message: str,
        operation: str = "",
        details: str | None = None,
    ) -> None:
        """Initialize the exception with a message and optional details.

        Args:
            message: Human-readable error message
            operation: Operation that failed
            details: Optional technical details for debugging
        """
        self.message = message
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
# PACKAGE MANAGER INTERFACE EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class DevToolsServiceError(DependenciesServiceError):
    """Exception raised when development tools operations fail."""

    def __init__(
        self,
        tool_name: str = "",
        operation: str = "",
        reason: str = "",
        details: str = "",
    ) -> None:
        """Initialize dev tools error.

        Args:
            tool_name: Name of the tool that caused the error
            operation: Operation that failed
            reason: Reason for the error
            details: Additional error details
        """
        message = (
            f"Dev tools error for {tool_name}: {reason}"
            if tool_name and reason
            else "Dev tools error occurred"
        )
        super().__init__(
            message=message,
            operation=operation,
            details=details,
        )
        self.tool_name = tool_name
        self.reason = reason


class SystemPkgManagerServiceError(DependenciesServiceError):
    """Exception raised when package manager operations fail."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize package manager error.

        Args:
            message: Error message
            operation: Operation that failed
            details: Additional error details
        """
        super().__init__(
            message=message or "Package manager error occurred",
            operation=operation,
            details=details,
        )


class RuntimeServiceError(DependenciesServiceError):
    """Exception raised when runtime manager operations fail."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize runtime manager error.

        Args:
            message: Error message
            operation: Operation that failed
            details: Additional error details
        """
        super().__init__(
            message=message or "Runtime manager error occurred",
            operation=operation,
            details=details,
        )
