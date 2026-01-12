#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT INTERFACE EXCEPTIONS - Context Interface Exception Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception classes for context interface operations.

This module contains custom exceptions used specifically by the context
interfaces, such as:
- ContextMenuInterface (womm/interfaces/context/registry_interface.py)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class ContextInterfaceError(Exception):
    """Base exception for all context interface errors.

    This is the main exception class for all context interface operations.
    Used for general errors like unexpected failures during interface operations.
    """

    def __init__(
        self,
        message: str,
        operation: str = "",
        details: str = "",
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
# CONTEXT MENU INTERFACE EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class MenuInterfaceError(ContextInterfaceError):
    """Exception raised when context menu interface operations fail.

    This exception is raised when context menu operations cannot be completed
    successfully, such as installation, removal, or verification.
    """

    def __init__(
        self,
        message: str,
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize context menu interface error.

        Args:
            message: Human-readable error message
            operation: Operation that failed
            details: Optional technical details for debugging
        """
        super().__init__(message, operation, details)


# ///////////////////////////////////////////////////////////////
# REGISTRY INTERFACE EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class RegistryInterfaceError(ContextInterfaceError):
    """Exception raised when registry interface operations fail.

    This exception is raised when Windows registry operations cannot be
    completed successfully.
    """

    def __init__(
        self,
        message: str,
        operation: str = "",
        key_path: str = "",
        details: str = "",
    ) -> None:
        """Initialize registry interface error.

        Args:
            message: Human-readable error message
            operation: Operation that failed
            key_path: Registry key path that failed
            details: Optional technical details for debugging
        """
        self.key_path = key_path
        super().__init__(message, operation, details)


# ///////////////////////////////////////////////////////////////
# SCRIPT INTERFACE EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ScriptDetectorInterfaceError(ContextInterfaceError):
    """Exception raised when script interface operations fail.

    This exception is raised when script generation or handling operations
    cannot be completed successfully.
    """

    def __init__(
        self,
        message: str,
        script_path: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize script interface error.

        Args:
            message: Human-readable error message
            script_path: Path to the script that failed
            operation: Operation that failed
            details: Optional technical details for debugging
        """
        self.script_path = script_path
        super().__init__(message, operation, details)


# ///////////////////////////////////////////////////////////////
# ICON INTERFACE EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class IconInterfaceError(ContextInterfaceError):
    """Exception raised when icon interface operations fail.

    This exception is raised when icon detection, validation, or resolution
    operations cannot be completed successfully at the interface level.
    """

    def __init__(
        self,
        message: str,
        operation: str = "",
        icon_path: str = "",
        details: str = "",
    ) -> None:
        """Initialize icon interface error.

        Args:
            message: Human-readable error message
            operation: Operation that failed
            icon_path: Path to the icon that caused the error
            details: Optional technical details for debugging
        """
        self.icon_path = icon_path
        super().__init__(message, operation, details)


# ///////////////////////////////////////////////////////////////
# VALIDATION INTERFACE EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ValidationInterfaceError(ContextInterfaceError):
    """Exception raised when validation interface operations fail.

    This exception is raised when validation operations cannot be completed
    successfully at the interface level.
    """

    def __init__(
        self,
        message: str,
        operation: str = "",
        field: str = "",
        details: str = "",
    ) -> None:
        """Initialize validation interface error.

        Args:
            message: Human-readable error message
            operation: Operation that failed
            field: Field that failed validation
            details: Optional technical details for debugging
        """
        self.field = field
        super().__init__(message, operation, details)
