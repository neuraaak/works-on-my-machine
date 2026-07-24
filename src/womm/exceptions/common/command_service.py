#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CLI SERVICE EXCEPTIONS - Command Runner Service Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
CLI service exceptions for Works On My Machine.

This module contains custom exceptions used specifically by the command
runner service (formerly CLI utils).
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class CommandServiceError(Exception):
    """Base exception for all CLI service errors.

    Used for unexpected failures during command preparation or execution.
    """

    def __init__(self, message: str, details: str | None = None) -> None:
        """Initialize the exception with a message and optional details."""
        self.message = message
        self.details = details
        super().__init__(self.message)


# ///////////////////////////////////////////////////////////////
# UTILITY / VALIDATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class CommandUtilityError(CommandServiceError):
    """Exception raised for invalid CLI service usage or parameters."""

    def __init__(self, message: str, details: str | None = None) -> None:
        """Initialize CLI utility error."""
        super().__init__(message, details)


class TimeoutError(CommandServiceError):
    """Exception raised when a command execution times out."""

    def __init__(
        self,
        command: str,
        timeout_seconds: int,
        details: str | None = None,
    ) -> None:
        """Initialize timeout error."""
        self.command = command
        self.timeout_seconds = timeout_seconds
        message = f"Command timed out after {timeout_seconds}s: {command}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# EXECUTION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class CommandExecutionError(CommandServiceError):
    """Exception raised when command execution fails."""

    def __init__(
        self,
        command: str,
        return_code: int,
        stderr: str | None = None,
        details: str | None = None,
    ) -> None:
        """Initialize command execution error."""
        self.command = command
        self.return_code = return_code
        self.stderr = stderr or ""
        message = f"Command execution failed (code {return_code}): {command}"
        super().__init__(message, details or self.stderr)


__all__ = [
    "CommandExecutionError",
    "CommandServiceError",
    "CommandUtilityError",
    "TimeoutError",
]
