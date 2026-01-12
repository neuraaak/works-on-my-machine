#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM SERVICE EXCEPTIONS - System Service Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System service exceptions for Works On My Machine.

This module contains custom exceptions used specifically by the system
services, such as:
- SystemDetectorService (womm/services/system/system_detector_service.py)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class SystemServiceError(Exception):
    """Base exception for all system service errors.

    This is the main exception class for all system service operations.
    Used for general errors like unexpected failures during system operations.
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
# SYSTEM DETECTION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class DevEnvDetectionServiceError(SystemServiceError):
    """Exception raised when development environment detection fails.

    This exception is raised when development environments cannot be detected.
    """

    def __init__(
        self,
        environment: str,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize development environment detection error.

        Args:
            environment: Development environment that failed
            operation: Operation that failed
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.environment = environment
        self.operation = operation
        self.reason = reason
        message = f"Development environment detection error for {environment} during {operation}: {reason}"
        super().__init__(message, details)


class PkgManagerDetectionServiceError(SystemServiceError):
    """Exception raised when package manager detection fails.

    This exception is raised when package managers cannot be detected
    or their information cannot be retrieved.
    """

    def __init__(
        self,
        package_manager: str,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize package manager detection error.

        Args:
            package_manager: Package manager that failed
            operation: Operation that failed
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.package_manager = package_manager
        self.operation = operation
        self.reason = reason
        message = f"Package manager detection error for {package_manager} during {operation}: {reason}"
        super().__init__(message, details)


class SystemDetectionServiceError(SystemServiceError):
    """Exception raised when system detection fails.

    This exception is raised when the system detector cannot determine
    system information, package managers, or development environments.
    """

    def __init__(
        self,
        message: str,
        details: str | None = None,
    ) -> None:
        """Initialize system detection error.

        Args:
            message: Human-readable error message
            details: Optional technical details for debugging
        """
        super().__init__(message, details)


class InfoServiceError(SystemServiceError):
    """Exception raised when system information gathering fails.

    This exception is raised when platform information cannot be retrieved.
    """

    def __init__(
        self,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize system info error.

        Args:
            operation: Operation that failed
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.reason = reason
        message = f"System info error during {operation}: {reason}"
        super().__init__(message, details)


class ReportGenerationServiceError(SystemServiceError):
    """Exception raised when report generation fails.

    This exception is raised when system reports cannot be generated or exported.
    """

    def __init__(
        self,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize report generation error.

        Args:
            operation: Operation that failed
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.reason = reason
        message = f"Report generation error during {operation}: {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# PATH MANAGEMENT EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class FileSystemServiceError(SystemServiceError):
    """Exception raised when file system operations fail.

    This exception is raised when file or directory operations
    cannot be completed successfully.
    """

    def __init__(
        self,
        operation: str,
        path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize file system error.

        Args:
            operation: Operation that failed
            path: Path that failed
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.path = path
        self.reason = reason
        message = f"File system error during {operation} on {path}: {reason}"
        super().__init__(message, details)


class RegistryServiceError(SystemServiceError):
    """Exception raised when Windows registry operations fail.

    This exception is raised when registry queries or modifications
    cannot be completed successfully.
    """

    def __init__(
        self,
        registry_key: str,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize registry error.

        Args:
            registry_key: Registry key that failed
            operation: Operation that failed
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.registry_key = registry_key
        self.operation = operation
        self.reason = reason
        message = f"Registry error for {registry_key} during {operation}: {reason}"
        super().__init__(message, details)


class UserPathServiceError(SystemServiceError):
    """Exception raised when PATH operations fail.

    This exception is raised when PATH environment variable operations
    cannot be completed successfully.
    """

    def __init__(
        self,
        message: str,
        details: str | None = None,
    ) -> None:
        """Initialize user path error.

        Args:
            message: Human-readable error message
            details: Optional technical details for debugging
        """
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# ENVIRONMENT MANAGEMENT EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class EnvironmentServiceError(SystemServiceError):
    """Exception raised when environment refresh operations fail.

    This exception is raised when environment variables cannot be refreshed
    from the registry or system configuration.
    """

    def __init__(
        self,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize environment refresh error.

        Args:
            operation: Operation that failed
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.reason = reason
        message = f"Environment refresh error during {operation}: {reason}"
        super().__init__(message, details)
