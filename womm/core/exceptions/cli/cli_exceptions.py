#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CLI EXCEPTIONS - CLI Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
CLI exceptions for Works On My Machine.

This module contains custom exceptions used specifically by CLI modules:
- CLI utilities (womm/core/utils/cli_utils.py)

Following a pragmatic approach with focused exception types:
1. CLIUtilityError - Base exception for CLI utilities
2. CommandExecutionError - Command execution errors
3. CommandValidationError - Command validation errors
4. TimeoutError - Command timeout errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class CLIUtilityError(Exception):
    """Base exception for all CLI utility errors.

    This is the main exception class for all CLI utility operations.
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
# COMMAND EXECUTION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class CommandExecutionError(CLIUtilityError):
    """Command execution errors for CLI operations.

    This exception is raised when command execution fails,
    such as subprocess failures or command execution errors.
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
        self.command = command
        self.return_code = return_code
        self.stderr = stderr
        reason = f"Command returned {return_code}: {stderr}"
        message = f"Command execution failed for '{command}': {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# COMMAND VALIDATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class CommandValidationError(CLIUtilityError):
    """Command validation errors for CLI operations.

    This exception is raised when command validation fails,
    such as invalid command format or security validation failures.
    """

    def __init__(
        self,
        command: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize command validation error with specific context.

        Args:
            command: The command being validated
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.command = command
        self.reason = reason
        message = f"Command validation failed for '{command}': {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# TIMEOUT EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class TimeoutError(CLIUtilityError):
    """Command timeout errors for CLI operations.

    This exception is raised when command execution times out,
    such as long-running commands or hanging processes.
    """

    def __init__(
        self,
        command: str,
        timeout_seconds: int,
        details: str | None = None,
    ) -> None:
        """Initialize timeout error with specific context.

        Args:
            command: The command that timed out
            timeout_seconds: The timeout duration in seconds
            details: Optional technical details for debugging
        """
        self.command = command
        self.timeout_seconds = timeout_seconds
        reason = f"Command timed out after {timeout_seconds} seconds"
        message = f"Command timeout for '{command}': {reason}"
        super().__init__(message, details)
