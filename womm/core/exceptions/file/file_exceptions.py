#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# FILE EXCEPTIONS - File Scanning Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
File scanning exceptions for Works On My Machine.

This module contains custom exceptions used specifically by file scanning modules:
- File utilities (womm/core/utils/file_scanner.py)

Following a pragmatic approach with focused exception types:
1. FileUtilityError - Base exception for file utilities
2. FileScanError - File scanning errors
3. FileAccessError - File access errors
4. SecurityFilterError - Security filtering errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class FileUtilityError(Exception):
    """Base exception for all file utility errors.

    This is the main exception class for all file utility operations.
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
# FILE SCANNING EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class FileScanError(FileUtilityError):
    """File scanning errors for file utility operations.

    This exception is raised when file scanning operations fail,
    such as directory traversal or file discovery errors.
    """

    def __init__(
        self,
        operation: str,
        target_path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize file scan error with specific context.

        Args:
            operation: The operation being performed (e.g., "directory_scan", "file_discovery")
            target_path: The path being scanned
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.target_path = target_path
        self.reason = reason
        message = f"File scan {operation} failed for '{target_path}': {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# FILE ACCESS EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class FileAccessError(FileUtilityError):
    """File access errors for file utility operations.

    This exception is raised when file access operations fail,
    such as permission errors or file system access issues.
    """

    def __init__(
        self,
        operation: str,
        file_path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize file access error with specific context.

        Args:
            operation: The operation being performed (e.g., "read", "write", "list")
            file_path: The file being accessed
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.file_path = file_path
        self.reason = reason
        message = f"File access {operation} failed for '{file_path}': {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# SECURITY FILTERING EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class SecurityFilterError(FileUtilityError):
    """Security filtering errors for file utility operations.

    This exception is raised when security filtering operations fail,
    such as pattern matching or security validation errors.
    """

    def __init__(
        self,
        operation: str,
        file_path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize security filter error with specific context.

        Args:
            operation: The operation being performed (e.g., "pattern_match", "security_validation")
            file_path: The file being filtered
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.file_path = file_path
        self.reason = reason
        message = f"Security filter {operation} failed for '{file_path}': {reason}"
        super().__init__(message, details)
