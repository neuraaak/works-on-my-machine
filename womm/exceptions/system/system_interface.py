#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM INTERFACE EXCEPTIONS - System Interface Exception Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception classes for system interface operations.

This module contains custom exceptions used specifically by the system
interfaces, such as:
- SystemManagerInterface (womm/interfaces/system/system_manager_interface.py)
- UserPathManagerInterface (womm/interfaces/system/user_path_manager_interface.py)
- EnvironmentManagerInterface (womm/interfaces/system/environment_manager_interface.py)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class SystemInterfaceError(Exception):
    """Base exception for all system interface errors.

    This is the main exception class for all system interface operations.
    Used for general errors like unexpected failures during interface operations.
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
# SYSTEM MANAGER INTERFACE EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class EnvironmentInterfaceError(SystemInterfaceError):
    """Exception raised when environment manager interface operations fail.

    This exception is raised when environment refresh or verification
    operations fail at the interface level.
    """

    def __init__(
        self,
        message: str,
        operation: str = "",
        details: str | None = None,
    ) -> None:
        """Initialize environment manager interface error.

        Args:
            message: Human-readable error message
            operation: Operation that failed
            details: Optional technical details for debugging
        """
        super().__init__(message, operation, details)


# ///////////////////////////////////////////////////////////////
# USER PATH MANAGER INTERFACE EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class UserPathInterfaceError(SystemInterfaceError):
    """Exception raised when user path manager interface operations fail.

    This exception is raised when PATH backup, restoration, or modification
    operations fail at the interface level.
    """

    def __init__(
        self,
        message: str,
        operation: str = "",
        path: str = "",
        details: str | None = None,
    ) -> None:
        """Initialize user path manager interface error.

        Args:
            message: Human-readable error message
            operation: Operation that failed
            path: Path that caused the error
            details: Optional technical details for debugging
        """
        self.path = path
        super().__init__(message, operation, details)


# ///////////////////////////////////////////////////////////////
# SYSTEM DETECTOR INTERFACE EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class DetectorInterfaceError(SystemInterfaceError):
    """Exception raised when system detector interface operations fail.

    This exception is raised when system detection, prerequisites checking,
    or interactive selection operations fail at the interface level.
    """

    def __init__(
        self,
        message: str,
        operation: str = "",
        details: str | None = None,
    ) -> None:
        """Initialize system detector interface error.

        Args:
            message: Human-readable error message
            operation: Operation that failed
            details: Optional technical details for debugging
        """
        super().__init__(message, operation, details)
