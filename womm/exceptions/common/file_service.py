#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# FILE SERVICE EXCEPTIONS - File Service Exception Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception classes for file scanning service operations.

Provides specialized exceptions for file scanning, validation, and access errors.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION CLASSES
# ///////////////////////////////////////////////////////////////


class FileServiceError(Exception):
    """Base exception for file service errors."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        target_path: str = "",
        details: str = "",
    ) -> None:
        """Initialize file service error.

        Args:
            message: Error message
            operation: Operation that failed
            target_path: Path that caused the error
            details: Additional error details
        """
        self.message = message or "File service error occurred"
        self.operation = operation
        self.target_path = target_path
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of error."""
        parts = [self.message]
        if self.operation:
            parts.append(f"Operation: {self.operation}")
        if self.target_path:
            parts.append(f"Path: {self.target_path}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " | ".join(parts)


# ///////////////////////////////////////////////////////////////
# SPECIALIZED EXCEPTION CLASSES
# ///////////////////////////////////////////////////////////////


class DirectoryAccessError(FileServiceError):
    """Exception raised when directory access fails."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        directory_path: str = "",
        reason: str = "",
        details: str = "",
    ) -> None:
        """Initialize directory access error.

        Args:
            message: Error message
            operation: Operation that failed
            directory_path: Directory path that caused the error
            reason: Reason for access failure
            details: Additional error details
        """
        self.reason = reason
        super().__init__(message, operation, directory_path, details)


class FileAccessError(FileServiceError):
    """Exception raised when file access fails."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        file_path: str = "",
        reason: str = "",
        details: str = "",
    ) -> None:
        """Initialize file access error.

        Args:
            message: Error message
            operation: Operation that failed
            file_path: File path that caused the error
            reason: Reason for access failure
            details: Additional error details
        """
        self.reason = reason
        super().__init__(message, operation, file_path, details)


class FileScanError(FileServiceError):
    """Exception raised when file scanning fails."""


class FileValidationError(FileServiceError):
    """Exception raised when file validation fails."""


class SecurityFilterError(FileServiceError):
    """Exception raised when security filtering fails."""


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "DirectoryAccessError",
    "FileAccessError",
    "FileScanError",
    "FileServiceError",
    "FileValidationError",
    "SecurityFilterError",
]
