#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# LINT INTERFACE EXCEPTIONS - Lint Interface Exception Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Lint interface exceptions for Works On My Machine.

This module contains custom exceptions used specifically by the lint
interfaces, such as:
- PythonLintInterface (womm/interfaces/lint/python_lint_interface.py)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class LintInterfaceError(Exception):
    """Base exception for all lint interface errors.

    This is the main exception class for all lint interface operations.
    Used for general errors like unexpected failures during lint operations.
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
# PYTHON LINT INTERFACE EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class PythonLintInterfaceError(LintInterfaceError):
    """Exception raised when Python linting operations fail.

    This exception is raised when Python linting operations cannot be
    completed successfully, such as checking or fixing Python code.
    """

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        details: str | None = None,
    ) -> None:
        """Initialize Python lint interface error.

        Args:
            message: Human-readable error message
            operation: Optional operation that failed
            details: Optional technical details for debugging
        """
        self.operation = operation
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "LintInterfaceError",
    "PythonLintInterfaceError",
]
