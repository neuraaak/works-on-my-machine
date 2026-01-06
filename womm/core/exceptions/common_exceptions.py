#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# COMMON EXCEPTIONS - Common Module Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Common module exceptions for Works On My Machine.

This module contains custom exceptions used specifically by common utility modules:
- imports.py - Import and path resolution utilities
- path_resolver.py - Path management utilities
- security.py - Security and command execution utilities
- results.py - Result data classes (no exceptions needed)

Following a pragmatic approach with focused exception types:
1. CommonUtilityError - Base exception for common utilities
2. ImportError - Import-related errors
3. PathResolutionError - Path resolution errors
4. SecurityError - Security validation and execution errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class CommonUtilityError(Exception):
    """Base exception for all common utility errors.

    This is the main exception class for all common utility operations.
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
# IMPORT-RELATED EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ImportUtilityError(CommonUtilityError):
    """Import utility errors for dynamic module imports.

    This exception is raised when dynamic import operations fail,
    such as importing shared modules or resolving module paths.
    """

    def __init__(
        self,
        module_name: str,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize import utility error with specific context.

        Args:
            module_name: Name of the module being imported
            operation: The operation being performed (e.g., "import_shared_module")
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.module_name = module_name
        self.operation = operation
        self.reason = reason
        message = f"Import {operation} failed for '{module_name}': {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# PATH RESOLUTION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class PathResolutionError(CommonUtilityError):
    """Path resolution errors for path management utilities.

    This exception is raised when path resolution operations fail,
    such as resolving script paths or validating file existence.
    """

    def __init__(
        self,
        operation: str,
        path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize path resolution error with specific context.

        Args:
            operation: The operation being performed (e.g., "resolve_script_path")
            path: The path being resolved
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.path = path
        self.reason = reason
        message = f"Path resolution {operation} failed for '{path}': {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# SECURITY EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class SecurityError(CommonUtilityError):
    """Security-related errors for command execution and validation.

    This exception is raised when security operations fail,
    such as command validation or secure execution.
    """

    def __init__(
        self,
        operation: str,
        command: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize security error with specific context.

        Args:
            operation: The operation being performed (e.g., "run_secure_command")
            command: The command being executed
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.command = command
        self.reason = reason
        message = f"Security {operation} failed for '{command}': {reason}"
        super().__init__(message, details)


class CommandExecutionError(SecurityError):
    """Command execution errors for security utilities.

    This exception is raised when command execution fails,
    such as subprocess failures or timeout issues.
    """

    def __init__(
        self,
        command: str,
        return_code: int,
        stderr: str,
        details: str | None = None,
    ) -> None:
        """Initialize command execution error with specific context.

        Args:
            command: The command that failed
            return_code: The return code from the command
            stderr: Error output from the command
            details: Optional technical details for debugging
        """
        self.return_code = return_code
        self.stderr = stderr
        reason = f"Command returned {return_code}: {stderr}"
        super().__init__("execution", command, reason, details)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Base exception
    "CommonUtilityError",
    # Import exceptions
    "ImportUtilityError",
    # Path resolution exceptions
    "PathResolutionError",
    # Security exceptions
    "SecurityError",
    "CommandExecutionError",
]
