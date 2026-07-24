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


class DependenciesInterfaceError(Exception):
    """Base exception for all dependencies interface errors.

    This is the main exception class for all dependencies interface operations.
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
# PACKAGE MANAGER INTERFACE EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class DevToolsInterfaceError(DependenciesInterfaceError):
    """Exception raised when dev tools manager interface operations fail.

    This exception is raised when development tools detection, checking,
    or installation operations fail at the interface level.
    """

    def __init__(
        self,
        message: str,
        tool_name: str = "",
        language: str = "",
        operation: str = "",
        details: str | None = None,
    ) -> None:
        """Initialize dev tools manager interface error.

        Args:
            message: Human-readable error message
            tool_name: Name of the tool that caused the error
            language: Programming language context
            operation: Operation that failed
            details: Optional technical details for debugging
        """
        self.tool_name = tool_name
        self.language = language
        super().__init__(message, operation, details)


class SystemPkgManagerInterfaceError(DependenciesInterfaceError):
    """Exception raised when package manager interface operations fail.

    This exception is raised when package manager detection, checking,
    or installation operations fail at the interface level.
    """

    def __init__(
        self,
        message: str,
        manager_name: str = "",
        operation: str = "",
        details: str | None = None,
    ) -> None:
        """Initialize package manager interface error.

        Args:
            message: Human-readable error message
            manager_name: Name of the package manager that caused the error
            operation: Operation that failed
            details: Optional technical details for debugging
        """
        super().__init__(message, operation, details)
        self.manager_name = manager_name


# ///////////////////////////////////////////////////////////////
# RUNTIME MANAGER INTERFACE EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class RuntimeInterfaceError(DependenciesInterfaceError):
    """Exception raised when runtime manager interface operations fail.

    This exception is raised when runtime detection, checking,
    or installation operations fail at the interface level.
    """

    def __init__(
        self,
        message: str,
        runtime_name: str = "",
        operation: str = "",
        details: str | None = None,
    ) -> None:
        """Initialize runtime manager interface error.

        Args:
            message: Human-readable error message
            runtime_name: Name of the runtime that caused the error
            operation: Operation that failed
            details: Optional technical details for debugging
        """
        super().__init__(message, operation, details)
        self.runtime_name = runtime_name
