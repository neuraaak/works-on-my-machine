#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# LINT EXCEPTIONS - Linting Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Linting exceptions for Works On My Machine.

This module contains custom exceptions used specifically by linting modules:
- LintManager (womm/core/managers/lint/lint_manager.py)
- Lint utilities (womm/core/utils/lint/*.py)

Following a pragmatic approach with focused exception types:
1. LintUtilityError - Base exception for linting utilities
2. ToolExecutionError - Tool execution errors
3. ToolAvailabilityError - Tool availability errors
4. LintManagerError - Base exception for lint manager
5. LintValidationError - Lint validation errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////////
# UTILITY EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class LintUtilityError(Exception):
    """Base exception for all linting utility errors.

    This is the main exception class for all linting utility operations.
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
# TOOL EXECUTION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ToolExecutionError(LintUtilityError):
    """Tool execution errors for linting operations.

    This exception is raised when linting tool execution fails,
    such as running ruff, black, isort, or other linting tools.
    """

    def __init__(
        self,
        tool_name: str,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize tool execution error with specific context.

        Args:
            tool_name: Name of the linting tool (e.g., "ruff", "black")
            operation: The operation being performed (e.g., "check", "fix")
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.tool_name = tool_name
        self.operation = operation
        self.reason = reason
        message = f"Tool execution {operation} failed for '{tool_name}': {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# TOOL AVAILABILITY EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class ToolAvailabilityError(LintUtilityError):
    """Tool availability errors for linting operations.

    This exception is raised when linting tools are not available,
    such as tools not being installed or not found in PATH.
    """

    def __init__(
        self,
        tool_name: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize tool availability error with specific context.

        Args:
            tool_name: Name of the linting tool (e.g., "ruff", "black")
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.tool_name = tool_name
        self.reason = reason
        message = f"Tool availability check failed for '{tool_name}': {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# MANAGER EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class LintManagerError(Exception):
    """Base exception for LintManager errors.

    This exception is raised when LintManager operations fail,
    such as process orchestration, progress tracking, or state management.
    """

    def __init__(self, message: str, details: str | None = None) -> None:
        """Initialize the manager error with a message and optional details.

        Args:
            message: Human-readable error message
            details: Optional technical details for debugging
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


# ///////////////////////////////////////////////////////////////
# VALIDATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class LintValidationError(LintManagerError):
    """Lint validation errors during linting process.

    This exception is raised when lint validation operations fail,
    such as validating lint results or processing tool output.
    """

    def __init__(
        self,
        validation_type: str,
        file_path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize lint validation error with specific context.

        Args:
            validation_type: Type of validation being performed (e.g., "result_processing", "output_parsing")
            file_path: The file being validated
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.validation_type = validation_type
        self.file_path = file_path
        self.reason = reason
        message = (
            f"Lint validation '{validation_type}' failed for '{file_path}': {reason}"
        )
        super().__init__(message, details)
