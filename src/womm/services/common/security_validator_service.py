#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SECURITY VALIDATOR SERVICE - Security Validation Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Security Validator Service - Singleton service for security validation.

Handles security validation for command execution and file operations.
Provides comprehensive security checks to prevent dangerous operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.common import (
    CommandValidationError,
    PathValidationError,
    SecurityServiceError,
)
from ...shared.configs.security import SecurityPatternsConfig
from ...shared.results import (
    CommandValidationResult,
    PathValidationResult,
    SecurityReportResult,
)
from ...utils.security import (
    has_dangerous_command_patterns,
    has_dangerous_file_patterns,
    has_excessive_traversal,
    is_dangerous_argument,
    is_system_directory,
    validate_permission_command,
)

# ///////////////////////////////////////////////////////////////
# SECURITY VALIDATOR SERVICE (SINGLETON)
# ///////////////////////////////////////////////////////////////


class SecurityValidatorService:
    """Singleton service for validating commands and file paths for security concerns."""

    _instance: ClassVar[SecurityValidatorService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> SecurityValidatorService:
        """Create or return the singleton instance.

        Returns:
            SecurityValidatorService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize security validator service (only once)."""
        if SecurityValidatorService._initialized:
            return

        self.logger = logging.getLogger(__name__)
        SecurityValidatorService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def validate_command(self, command: list[str]) -> CommandValidationResult:
        """Validate a command for security concerns.

        Args:
            command: Command to validate as list of strings

        Returns:
            CommandValidationResult: Result with validation status and reason

        Raises:
            CommandValidationError: If command validation fails
            SecurityServiceError: If unexpected error occurs during validation
        """
        try:
            if not command:
                return CommandValidationResult(
                    success=False,
                    message="Command validation failed",
                    command="",
                    is_valid=False,
                    validation_reason="Command cannot be empty",
                )

            if not isinstance(command, list):
                return CommandValidationResult(
                    success=False,
                    message="Command validation failed",
                    command=str(command),
                    is_valid=False,
                    validation_reason=f"Command must be a list, got: {type(command)}",
                )

            if not all(isinstance(arg, str) for arg in command):
                return CommandValidationResult(
                    success=False,
                    message="Command validation failed",
                    command=str(command),
                    is_valid=False,
                    validation_reason="All command arguments must be strings",
                )

            # Get the base command (first argument)
            base_command = command[0].lower()

            # Check if command is in whitelist
            if base_command not in SecurityPatternsConfig.ALLOWED_COMMANDS:
                return CommandValidationResult(
                    success=False,
                    message="Command validation failed",
                    command=" ".join(command),
                    is_valid=False,
                    validation_reason=f"Command '{base_command}' is not in allowed list",
                )

            # Check for dangerous patterns in the base command
            if has_dangerous_command_patterns(base_command):
                return CommandValidationResult(
                    success=False,
                    message="Command validation failed",
                    command=" ".join(command),
                    is_valid=False,
                    validation_reason=f"Command '{base_command}' contains dangerous patterns",
                )

            # Check for dangerous arguments
            for arg in command[1:]:
                if is_dangerous_argument(base_command, arg):
                    return CommandValidationResult(
                        success=False,
                        message="Command validation failed",
                        command=" ".join(command),
                        is_valid=False,
                        validation_reason=f"Dangerous argument '{arg}' for command '{base_command}'",
                    )

            # Additional command-specific validations
            if base_command in ["chmod", "chown"] and not validate_permission_command(
                command
            ):
                return CommandValidationResult(
                    success=False,
                    message="Command validation failed",
                    command=" ".join(command),
                    is_valid=False,
                    validation_reason=f"Invalid permission command: {' '.join(command)}",
                )

            return CommandValidationResult(
                success=True,
                message="Command validated successfully",
                command=" ".join(command),
                is_valid=True,
                validation_reason="Command passed all security checks",
            )

        except (CommandValidationError, SecurityServiceError):
            # Re-raise security exceptions as-is
            raise
        except Exception as e:
            # Catch unexpected errors and wrap them
            raise SecurityServiceError(
                message=f"Unexpected error during command validation: {e}",
                details=f"Exception type: {type(e).__name__}, Command: {command}",
            ) from e

    def validate_file_path(self, file_path: str) -> PathValidationResult:
        """Validate a file path for security concerns.

        Args:
            file_path: File path to validate

        Returns:
            PathValidationResult: Result with validation status and reason

        Raises:
            PathValidationError: If file path validation fails
            SecurityServiceError: If unexpected error occurs during validation
        """
        try:
            if not file_path:
                return PathValidationResult(
                    success=False,
                    message="Path validation failed",
                    path="",
                    is_valid=False,
                    validation_reason="File path cannot be empty",
                )

            if not isinstance(file_path, str):
                return PathValidationResult(
                    success=False,
                    message="Path validation failed",
                    path=str(file_path),
                    is_valid=False,
                    validation_reason=f"File path must be a string, got: {type(file_path)}",
                )

            # Check for dangerous patterns
            if has_dangerous_file_patterns(file_path):
                return PathValidationResult(
                    success=False,
                    message="Path validation failed",
                    path=file_path,
                    is_valid=False,
                    validation_reason="File path contains dangerous patterns",
                )

            # Check for directory traversal attempts
            if has_excessive_traversal(file_path):
                traversal_count = file_path.count("..")
                return PathValidationResult(
                    success=False,
                    message="Path validation failed",
                    path=file_path,
                    is_valid=False,
                    validation_reason=f"Excessive directory traversal: {traversal_count} levels",
                )

            # Check for absolute paths to system directories
            try:
                path = Path(file_path)
                if path.is_absolute() and is_system_directory(path):
                    return PathValidationResult(
                        success=False,
                        message="Path validation failed",
                        path=file_path,
                        is_valid=False,
                        validation_reason=f"Access to system directory: {file_path}",
                    )
            except (OSError, ValueError):
                return PathValidationResult(
                    success=False,
                    message="Path validation failed",
                    path=file_path,
                    is_valid=False,
                    validation_reason=f"Invalid file path format: {file_path}",
                )

            return PathValidationResult(
                success=True,
                message="Path validated successfully",
                path=file_path,
                is_valid=True,
                validation_reason="Path passed all security checks",
            )

        except (PathValidationError, SecurityServiceError):
            # Re-raise security exceptions as-is
            raise
        except Exception as e:
            # Catch unexpected errors and wrap them
            raise SecurityServiceError(
                message=f"Unexpected error during file path validation: {e}",
                details=f"Exception type: {type(e).__name__}, Path: {file_path}",
            ) from e

    def validate_directory_path(self, dir_path: str) -> PathValidationResult:
        """Validate a directory path for security concerns.

        Args:
            dir_path: Directory path to validate

        Returns:
            PathValidationResult: Result with validation status and reason

        Raises:
            PathValidationError: If directory path validation fails
            SecurityUtilityError: If unexpected error occurs during validation
        """
        # Use the same validation as file paths
        return self.validate_file_path(dir_path)

    def get_security_report(self, command: list[str]) -> SecurityReportResult:
        """Get a detailed security report for a command.

        Args:
            command: Command to analyze

        Returns:
            SecurityReportResult: Result with security report

        Raises:
            SecurityServiceError: If unexpected error occurs during analysis
        """
        try:
            # Try to validate the command
            validation_result = self.validate_command(command)
            is_safe = validation_result.is_valid
            reason = validation_result.validation_reason

            checks_performed = []

            if command:
                base_command = command[0].lower()
                checks_performed.append(
                    f"Command '{base_command}' in whitelist: "
                    f"{base_command in SecurityPatternsConfig.ALLOWED_COMMANDS}"
                )
                checks_performed.append(
                    f"Command has dangerous patterns: "
                    f"{has_dangerous_command_patterns(base_command)}"
                )

                # Check each argument
                for i, arg in enumerate(command[1:], 1):
                    is_dangerous = is_dangerous_argument(base_command, arg)
                    checks_performed.append(
                        f"Argument {i} '{arg}' is dangerous: {is_dangerous}"
                    )

            return SecurityReportResult(
                success=True,
                message="Security report generated successfully",
                command=" ".join(command),
                is_safe=is_safe,
                reason=reason,
                base_command=command[0] if command else "",
                arguments=command[1:] if len(command) > 1 else [],
                checks_performed=checks_performed,
            )

        except Exception as e:
            return SecurityReportResult(
                success=False,
                error=f"Unexpected error during security report generation: {e}",
                command=" ".join(command) if command else "",
                is_safe=False,
                reason=str(e),
                base_command=command[0] if command else "",
                arguments=command[1:] if len(command) > 1 else [],
                checks_performed=[],
            )
