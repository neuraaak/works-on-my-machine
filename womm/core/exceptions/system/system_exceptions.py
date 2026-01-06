#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM EXCEPTIONS - System Detection Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System detection exceptions for Works On My Machine.

This module contains custom exceptions used specifically by system detection modules:
- SystemDetector (womm/core/utils/system/system_detector.py)

Following a pragmatic approach with specialized exception types:
1. SystemDetectionError - Base exception for all system detection operations
2. PackageManagerDetectionError - Package manager detection errors
3. DevelopmentEnvironmentDetectionError - Development environment detection errors
4. SystemInfoError - System information gathering errors
5. ReportGenerationError - Report generation and export errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class SystemDetectionError(Exception):
    """Base exception for all system detection-related errors.

    This is the main exception class for all system detection operations.
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
# PACKAGE MANAGER DETECTION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class PackageManagerDetectionError(SystemDetectionError):
    """Package manager detection errors for system detection operations.

    This exception is raised when package manager detection operations fail,
    such as checking tool availability or retrieving version information.
    """

    def __init__(
        self,
        package_manager: str,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize package manager detection error with specific context.

        Args:
            package_manager: The package manager being detected (e.g., "apt", "brew")
            operation: The operation being performed (e.g., "availability_check", "version_check")
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.package_manager = package_manager
        self.operation = operation
        self.reason = reason
        message = f"Package manager detection {operation} failed for '{package_manager}': {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# DEVELOPMENT ENVIRONMENT DETECTION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class DevelopmentEnvironmentDetectionError(SystemDetectionError):
    """Development environment detection errors for system detection operations.

    This exception is raised when development environment detection operations fail,
    such as checking editor availability or retrieving version information.
    """

    def __init__(
        self,
        environment: str,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize development environment detection error with specific context.

        Args:
            environment: The development environment being detected (e.g., "code", "vim")
            operation: The operation being performed (e.g., "availability_check", "version_check")
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.environment = environment
        self.operation = operation
        self.reason = reason
        message = f"Development environment detection {operation} failed for '{environment}': {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# SYSTEM INFORMATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class SystemInfoError(SystemDetectionError):
    """System information gathering errors for system detection operations.

    This exception is raised when system information gathering operations fail,
    such as retrieving platform information or environment variables.
    """

    def __init__(
        self,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize system info error with specific context.

        Args:
            operation: The operation being performed (e.g., "platform_info", "environment_vars")
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.reason = reason
        message = f"System information {operation} failed: {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# ENVIRONMENT REFRESH EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class EnvironmentRefreshError(SystemDetectionError):
    """Environment refresh errors for system operations.

    This exception is raised when environment refresh operations fail,
    such as reading registry values or updating environment variables.
    """

    def __init__(
        self,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize environment refresh error with specific context.

        Args:
            operation: The operation being performed (e.g., "environment_refresh", "registry_read")
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.reason = reason
        message = f"Environment refresh {operation} failed: {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# REPORT GENERATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ReportGenerationError(SystemDetectionError):
    """Report generation and export errors for system detection operations.

    This exception is raised when report generation or export operations fail,
    such as writing JSON files or formatting reports.
    """

    def __init__(
        self,
        operation: str,
        file_path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize report generation error with specific context.

        Args:
            operation: The operation being performed (e.g., "export", "write")
            file_path: The file path being accessed
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.file_path = file_path
        self.reason = reason
        message = f"Report generation {operation} failed for '{file_path}': {reason}"
        super().__init__(message, details)
