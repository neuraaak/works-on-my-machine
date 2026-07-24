#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INSTALLATION SERVICE EXCEPTIONS - Installation Service Exception Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception classes for installation service operations.

Provides specialized exceptions for installation and uninstallation operations,
file operations, path configuration, and verification errors.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION CLASSES
# ///////////////////////////////////////////////////////////////


class WommDeploymentServiceError(Exception):
    """Base exception for installation service errors."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize installation service error.

        Args:
            message: Error message
            operation: Operation that failed
            details: Additional error details
        """
        self.message = message or "Installation service error occurred"
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
# INSTALLATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class DependencyServiceError(WommDeploymentServiceError):
    """Exception raised when installation fails."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize installation error.

        Args:
            message: Error message
            operation: Operation that failed
            details: Additional error details
        """
        super().__init__(
            message=message or "Installation failed",
            operation=operation,
            details=details,
        )


class DeploymentFileServiceError(WommDeploymentServiceError):
    """Exception raised when file operations fail during installation."""

    def __init__(
        self,
        message: str = "",
        file_path: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize installation file error.

        Args:
            message: Error message
            file_path: Path to the file that caused the error
            operation: Operation that failed
            details: Additional error details
        """
        self.file_path = file_path
        super().__init__(
            message=message or "File operation failed during installation",
            operation=operation,
            details=details or f"File: {file_path}",
        )


class PathServiceError(WommDeploymentServiceError):
    """Exception raised when PATH configuration fails during installation."""

    def __init__(
        self,
        message: str = "",
        path: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize installation path error.

        Args:
            message: Error message
            path: Path that caused the error
            operation: Operation that failed
            details: Additional error details
        """
        self.path = path
        super().__init__(
            message=message or "PATH configuration failed during installation",
            operation=operation,
            details=details or f"Path: {path}",
        )


class VerificationServiceError(WommDeploymentServiceError):
    """Exception raised when uninstallation verification fails."""

    def __init__(
        self,
        message: str = "",
        verification_type: str = "",
        target_path: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize uninstallation verification error.

        Args:
            message: Error message
            verification_type: Type of verification that failed
            target_path: Target path for uninstallation
            operation: Operation that failed
            details: Additional error details
        """
        self.verification_type = verification_type
        self.target_path = target_path
        super().__init__(
            message=message or "Uninstallation verification failed",
            operation=operation,
            details=details
            or f"Verification type: {verification_type}, Target: {target_path}",
        )


# ///////////////////////////////////////////////////////////////
# UTILITY EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ExeVerificationServiceError(WommDeploymentServiceError):
    """Exception raised when executable verification fails."""

    def __init__(
        self,
        message: str = "",
        executable_name: str = "",
        reason: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize executable verification error.

        Args:
            message: Error message
            executable_name: Name of the executable that failed verification
            reason: Reason for verification failure
            operation: Operation that failed
            details: Additional error details
        """
        self.executable_name = executable_name
        self.reason = reason
        super().__init__(
            message=message or f"Executable verification failed: {reason}",
            operation=operation,
            details=details or f"Executable: {executable_name}",
        )


class FileVerificationServiceError(WommDeploymentServiceError):
    """Exception raised when file verification fails."""

    def __init__(
        self,
        message: str = "",
        verification_type: str = "",
        file_path: str = "",
        reason: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize file verification error.

        Args:
            message: Error message
            verification_type: Type of verification that failed
            file_path: Path to the file that failed verification
            reason: Reason for verification failure
            operation: Operation that failed
            details: Additional error details
        """
        self.verification_type = verification_type
        self.file_path = file_path
        self.reason = reason
        super().__init__(
            message=message or f"File verification failed: {reason}",
            operation=operation,
            details=details or f"File: {file_path}, Type: {verification_type}",
        )


class DeploymentUtilityError(WommDeploymentServiceError):
    """Exception raised when installation utility operations fail."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize installation utility error.

        Args:
            message: Error message
            operation: Operation that failed
            details: Additional error details
        """
        super().__init__(
            message=message or "Installation utility operation failed",
            operation=operation,
            details=details,
        )


class PathUtilityError(WommDeploymentServiceError):
    """Exception raised when PATH utility operations fail."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        path: str = "",
        reason: str = "",
        details: str = "",
    ) -> None:
        """Initialize path utility error.

        Args:
            message: Error message
            operation: Operation that failed
            path: Path that caused the error
            reason: Reason for failure
            details: Additional error details
        """
        self.path = path
        self.reason = reason
        super().__init__(
            message=message or f"PATH utility operation failed: {reason}",
            operation=operation,
            details=details or f"Path: {path}",
        )


# ///////////////////////////////////////////////////////////////
# DEPLOYMENT MANAGER EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class WommUninstallerError(WommDeploymentServiceError):
    """Exception raised when uninstallation manager operations fail."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize uninstallation manager error.

        Args:
            message: Error message
            operation: Operation that failed
            details: Additional error details
        """
        super().__init__(
            message=message or "Uninstallation manager operation failed",
            operation=operation,
            details=details,
        )


class WommInstallerError(WommDeploymentServiceError):
    """Exception raised when installation manager operations fail."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize installation manager error.

        Args:
            message: Error message
            operation: Operation that failed
            details: Additional error details
        """
        super().__init__(
            message=message or "Installation manager operation failed",
            operation=operation,
            details=details,
        )
