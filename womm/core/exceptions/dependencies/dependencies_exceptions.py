#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPENDENCIES EXCEPTIONS - Dependencies Management Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependencies management exceptions for Works On My Machine.

This module contains custom exceptions used specifically by dependency management modules:
- RuntimeManager (womm/core/managers/dependencies/runtime_manager.py)
- DevToolsManager (womm/core/managers/dependencies/dev_tools_manager.py)
- PackageManager (womm/core/managers/dependencies/package_manager.py)

Following a pragmatic approach with focused exception types:
1. DependenciesUtilityError - Base exception for dependencies utilities
2. RuntimeManagerError - Runtime management errors
3. DevToolsError - Development tools errors
4. PackageManagerError - Package manager errors
5. InstallationError - Installation process errors
6. ValidationError - Validation errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class DependenciesUtilityError(Exception):
    """Base exception for all dependencies utility errors.

    This is the main exception class for all dependencies utility operations.
    Used for general errors like invalid arguments, unexpected failures, etc.
    """

    def __init__(self, message: str, details: str | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            details: Additional error details
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


# ///////////////////////////////////////////////////////////////
# RUNTIME MANAGEMENT EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class RuntimeManagerError(DependenciesUtilityError):
    """Exception for runtime management errors.

    Used for errors related to runtime detection, installation, and management.
    """

    def __init__(
        self,
        runtime_name: str,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize the runtime error.

        Args:
            runtime_name: Name of the runtime (python, node, git)
            operation: Operation that failed
            reason: Reason for failure
            details: Additional error details
        """
        self.runtime_name = runtime_name
        self.operation = operation
        self.reason = reason
        message = f"Runtime {runtime_name} {operation} failed: {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# DEVELOPMENT TOOLS EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class DevToolsError(DependenciesUtilityError):
    """Exception for development tools errors.

    Used for errors related to development tools detection, installation, and management.
    """

    def __init__(
        self,
        tool_name: str,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize the dev tools error.

        Args:
            tool_name: Name of the development tool
            operation: Operation that failed
            reason: Reason for failure
            details: Additional error details
        """
        self.tool_name = tool_name
        self.operation = operation
        self.reason = reason
        message = f"Dev tool {tool_name} {operation} failed: {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# PACKAGE MANAGER EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class PackageManagerError(DependenciesUtilityError):
    """Exception for package manager errors.

    Used for errors related to package manager detection, installation, and operations.
    """

    def __init__(
        self,
        manager_name: str,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize the package manager error.

        Args:
            manager_name: Name of the package manager
            operation: Operation that failed
            reason: Reason for failure
            details: Additional error details
        """
        self.manager_name = manager_name
        self.operation = operation
        self.reason = reason
        message = f"Package manager {manager_name} {operation} failed: {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# INSTALLATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class InstallationError(DependenciesUtilityError):
    """Exception for installation process errors.

    Used for errors during the installation of runtimes, tools, or packages.
    """

    def __init__(
        self,
        component: str,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize the installation error.

        Args:
            component: Component being installed (runtime, tool, package)
            operation: Operation that failed
            reason: Reason for failure
            details: Additional error details
        """
        self.component = component
        self.operation = operation
        self.reason = reason
        message = f"Installation of {component} {operation} failed: {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# VALIDATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ValidationError(DependenciesUtilityError):
    """Exception for validation errors.

    Used for errors during validation of runtimes, tools, or package managers.
    """

    def __init__(
        self,
        component: str,
        validation_type: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize the validation error.

        Args:
            component: Component being validated
            validation_type: Type of validation that failed
            reason: Reason for failure
            details: Additional error details
        """
        self.component = component
        self.validation_type = validation_type
        self.reason = reason
        message = f"Validation of {component} ({validation_type}) failed: {reason}"
        super().__init__(message, details)
