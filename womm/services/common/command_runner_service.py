#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# COMMAND RUNNER SERVICE - Unified CLI Command Runner
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
CommandRunnerService - unified, secure command execution service.

Provides a singleton service for running commands with:
- optional security validation
- retry/timeout handling
- structured error reporting via dedicated exceptions.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import subprocess
import time
from pathlib import Path
from threading import Lock
from typing import Any, ClassVar

# Local imports
from ...exceptions.common import (
    CommandExecutionError,
    CommandServiceError,
    CommandUtilityError,
    CommandValidationError,
    TimeoutError,
)
from ...shared.result_models import CommandResult
from ...shared.results import (
    CommandAvailabilityResult,
    CommandVersionResult,
)

# ///////////////////////////////////////////////////////////////
# COMMAND RUNNER SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class CommandRunnerService:
    """Singleton command runner with optional security validation."""

    _instance: ClassVar[CommandRunnerService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> CommandRunnerService:
        """Create or return the singleton instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        default_cwd: str | Path | None = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        """Initialize command runner service (only once).

        Args:
            default_cwd: Default working directory
            timeout: Command timeout in seconds
            max_retries: Maximum number of retries for failed commands
            retry_delay: Delay between retries in seconds

        Raises:
            CommandUtilityError: If initialization parameters are invalid
        """
        if CommandRunnerService._initialized:
            return

        try:
            # Validate initialization parameters
            self._validate_init_parameters(timeout, max_retries, retry_delay)

            self.default_cwd = Path(default_cwd) if default_cwd else Path.cwd()
            self.timeout = timeout
            self.max_retries = max_retries
            self.retry_delay = retry_delay
            self.logger = logging.getLogger(__name__)
            CommandRunnerService._initialized = True

        except (
            CommandUtilityError,
            CommandExecutionError,
            CommandValidationError,
            TimeoutError,
        ):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise CommandUtilityError(
                message=f"Unexpected error during CLI manager initialization: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PUBLIC API METHODS
    # ///////////////////////////////////////////////////////////////

    def run(
        self,
        command: str | list[str],
        description: str = "",
        cwd: str | Path | None = None,
        validate_security: bool = False,
        **kwargs: Any,
    ) -> CommandResult:
        """Execute a command with optional security validation.

        Args:
            command: Command to execute
            description: Description for logging
            cwd: Working directory
            validate_security: Whether to validate command security
            **kwargs: Additional subprocess arguments

        Returns:
            CommandResult: Result of command execution

        Raises:
            CommandUtilityError: If command validation fails
            CommandValidationError: If security validation fails
            TimeoutError: If command times out
            CommandExecutionError: If command execution fails
        """
        try:
            # Input validation
            self._validate_command_input(command)

            # Convert string command to list
            if isinstance(command, str):
                command = [command]
            elif not isinstance(command, list):
                raise CommandUtilityError(
                    message=f"Command must be a string or list of strings, got: {type(command)}",
                    details=f"Invalid command type: {type(command).__name__}",
                )

            # Set working directory
            working_dir = Path(cwd) if cwd else self.default_cwd

            # Security validation if requested
            if validate_security:
                self._validate_command_security(command)

            # Log command execution if description provided
            if description:
                self.logger.info(f"Executing command: {description}")

            # Execute command with retries
            start_time = time.time()
            last_error = None

            for attempt in range(self.max_retries + 1):
                try:
                    result = self._execute_command(command, working_dir, **kwargs)
                    execution_time = time.time() - start_time

                    return CommandResult(
                        returncode=result.returncode,
                        stdout=result.stdout,
                        stderr=result.stderr,
                        command=command,
                        cwd=working_dir,
                        security_validated=validate_security,
                        execution_time=execution_time,
                    )

                except subprocess.TimeoutExpired as e:
                    last_error = TimeoutError(
                        command=str(command),
                        timeout_seconds=self.timeout,
                        details=f"Attempt {attempt + 1}/{self.max_retries + 1}",
                    )
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        raise last_error from e

                except subprocess.SubprocessError as e:
                    last_error = CommandExecutionError(
                        command=str(command),
                        return_code=getattr(e, "returncode", -1),
                        stderr=str(e),
                        details=f"Attempt {attempt + 1}/{self.max_retries + 1}: {e}",
                    )
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        raise last_error from e

                except Exception as e:
                    last_error = CommandExecutionError(
                        command=str(command),
                        return_code=-1,
                        stderr=str(e),
                        details=f"Unexpected error on attempt {attempt + 1}/{self.max_retries + 1}: {e}",
                    )
                    if attempt < self.max_retries:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        raise last_error from e

            # This should never be reached, but just in case
            raise last_error

        except (
            CommandUtilityError,
            CommandValidationError,
            TimeoutError,
            CommandExecutionError,
        ):
            # Re-raise specialized exceptions as-is
            raise
        except CommandServiceError:
            # Re-raise CLI-specific exceptions unchanged
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise CommandUtilityError(
                message=f"Unexpected error during command execution: {e}",
                details=f"Exception type: {type(e).__name__}, Command: {command}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE EXECUTION HELPERS
    # ///////////////////////////////////////////////////////////////

    def _execute_command(
        self,
        cmd: list[str],
        cwd: Path,
        **kwargs: Any,
    ) -> subprocess.CompletedProcess[str]:
        """Execute a single command attempt.

        Args:
            cmd: Command to execute as list of strings
            cwd: Working directory
            **kwargs: Additional subprocess arguments

        Returns:
            subprocess.CompletedProcess: Result of command execution

        Raises:
            CommandUtilityError: If command validation fails
            subprocess.TimeoutExpired: If command times out
            subprocess.SubprocessError: If command execution fails
        """
        try:
            # Validate command format
            if not isinstance(cmd, list) or not all(
                isinstance(arg, str) for arg in cmd
            ):
                raise CommandUtilityError(
                    message=f"Command must be a list of strings, got: {type(cmd)}",
                    details=f"Invalid command format: {type(cmd).__name__}",
                )

            if not cmd:
                raise CommandUtilityError(
                    message="Command cannot be empty",
                    details="Empty command list provided",
                )

            # Prepare subprocess arguments with explicit security settings
            subprocess_args = {
                "cwd": cwd,
                "timeout": self.timeout,
                "text": True,
                "encoding": "utf-8",
                "errors": "replace",
                "capture_output": True,
                "shell": False,  # Explicitly disable shell for security
            }

            # Add valid kwargs for subprocess
            valid_subprocess_args = {
                "input",
                "env",
                "check",
                "stdin",
                "stdout",
                "stderr",
                "preexec_fn",
                "close_fds",
                "pass_fds",
                "restore_signals",
                "start_new_session",
                "group",
                "extra_groups",
                "user",
                "umask",
                "startupinfo",
                "creationflags",
            }

            subprocess_args.update(
                {
                    key: value
                    for key, value in kwargs.items()
                    if key in valid_subprocess_args
                }
            )

            # Execute command with explicit security validation
            # The command has already been validated by the calling method
            return subprocess.run(cmd, check=False, **subprocess_args)

        except (
            CommandUtilityError,
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
        ):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise CommandUtilityError(
                message=f"Unexpected error during command execution: {e}",
                details=f"Exception type: {type(e).__name__}, Command: {cmd}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PUBLIC CONVENIENCE METHODS (INSTANCE)
    # ///////////////////////////////////////////////////////////////

    def run_silent(self, command: str | list[str], **kwargs: Any) -> CommandResult:
        """Execute a command in silent mode.

        Args:
            command: Command to execute
            **kwargs: Additional arguments for run method

        Returns:
            CommandResult: Result of command execution
        """
        return self.run(command, **kwargs)

    def run_secure(
        self,
        command: str | list[str],
        description: str = "",
        **kwargs: Any,
    ) -> CommandResult:
        """Execute a command with security validation.

        Args:
            command: Command to execute
            description: Description for logging
            **kwargs: Additional arguments for run method

        Returns:
            CommandResult: Result of command execution
        """
        return self.run(command, description, validate_security=True, **kwargs)

    def check_command_available(self, command: str) -> CommandAvailabilityResult:
        """Check if a command is available and optionally validate security.

        Args:
            command: Command to check

        Returns:
            CommandAvailabilityResult: Result with availability and security validation status
        """
        try:
            if not command:
                return CommandAvailabilityResult(
                    success=False,
                    message="Command name is empty",
                    command_name=command,
                    is_available=False,
                    security_validated=False,
                )

            import shutil

            if not shutil.which(command):
                return CommandAvailabilityResult(
                    success=False,
                    message=f"Command '{command}' not found in PATH",
                    command_name=command,
                    is_available=False,
                    security_validated=False,
                )

            # Additional security check
            security_validated = False
            try:
                from .security_validator_service import (
                    SecurityValidatorService,
                )

                validator = SecurityValidatorService()
                validation_result = validator.validate_command([command])
                security_validated = validation_result.is_valid
            except ImportError:
                # If security validator is not available, skip security validation
                security_validated = True
            except Exception:
                # If security validation fails, command is not secure
                security_validated = False

            return CommandAvailabilityResult(
                success=True,
                message=f"Command '{command}' is available",
                command_name=command,
                is_available=True,
                security_validated=security_validated,
            )

        except Exception as e:
            # Log but don't raise - this is a helper method
            self.logger.warning(
                f"Error checking command availability: {command}, Error: {e}"
            )
            return CommandAvailabilityResult(
                success=False,
                error=str(e),
                command_name=command,
                is_available=False,
                security_validated=False,
            )

    def get_command_version(
        self,
        command: str,
        version_flag: str = "--version",
    ) -> CommandVersionResult:
        """Get version of a command.

        Args:
            command: Command to get version for
            version_flag: Flag to use for version check

        Returns:
            CommandVersionResult: Result with version information
        """
        try:
            if not command:
                return CommandVersionResult(
                    success=False,
                    message="Command name is empty",
                    command_name=command,
                    version="",
                    version_flag=version_flag,
                )

            availability_result = self.check_command_available(command)
            if not availability_result.is_available:
                return CommandVersionResult(
                    success=False,
                    message=f"Command '{command}' not available",
                    command_name=command,
                    version="",
                    version_flag=version_flag,
                )

            result = self.run_silent([command, version_flag])
            if bool(result) and result.stdout.strip():
                # Extract version from output
                output = result.stdout.strip()
                if output:
                    # Take first line which probably contains version
                    first_line = output.split("\n")[0]
                    return CommandVersionResult(
                        success=True,
                        message=f"Version retrieved for '{command}'",
                        command_name=command,
                        version=first_line,
                        version_flag=version_flag,
                    )

            return CommandVersionResult(
                success=False,
                message=f"No version output from '{command} {version_flag}'",
                command_name=command,
                version="",
                version_flag=version_flag,
            )

        except Exception as e:
            # Log but don't raise - this is a helper method
            self.logger.warning(f"Error getting command version: {command}, Error: {e}")
            return CommandVersionResult(
                success=False,
                error=str(e),
                command_name=command,
                version="",
                version_flag=version_flag,
            )

    # ///////////////////////////////////////////////////////////////
    # PRIVATE VALIDATION HELPERS
    # ///////////////////////////////////////////////////////////////

    def _validate_init_parameters(
        self, timeout: int, max_retries: int, retry_delay: float
    ) -> None:
        """Validate initialization parameters.

        Args:
            timeout: Command timeout in seconds
            max_retries: Maximum number of retries
            retry_delay: Delay between retries

        Raises:
            CommandUtilityError: If parameters are invalid
        """
        if timeout <= 0:
            raise CommandUtilityError(
                message=f"Timeout must be positive, got: {timeout}",
                details="Invalid timeout parameter for CLI manager initialization",
            )

        if max_retries < 0:
            raise CommandUtilityError(
                message=f"Max retries must be non-negative, got: {max_retries}",
                details="Invalid max_retries parameter for CLI manager initialization",
            )

        if retry_delay < 0:
            raise CommandUtilityError(
                message=f"Retry delay must be non-negative, got: {retry_delay}",
                details="Invalid retry_delay parameter for CLI manager initialization",
            )

    def _validate_command_input(self, command: str | list[str]) -> None:
        """Validate command input.

        Args:
            command: Command to validate

        Raises:
            CommandUtilityError: If command is invalid
        """
        if not command:
            raise CommandUtilityError(
                message="Command cannot be empty",
                details="Empty command provided for execution",
            )

    def _validate_command_security(self, command: list[str]) -> None:
        """Validate command security using SecurityValidator.

        Args:
            command: Command to validate

        Raises:
            CommandValidationError: If security validation fails
        """
        try:
            from .security_validator_service import SecurityValidatorService

            validator = SecurityValidatorService()
            validation_result = validator.validate_command(command)
            if not validation_result.is_valid:
                raise CommandValidationError(
                    command=str(command),
                    reason=f"Security validation failed: {validation_result.validation_reason}",
                    details="Command contains potentially dangerous patterns",
                )
        except CommandValidationError:
            raise
        except ImportError:
            self.logger.warning("Security validator not available, skipping validation")
        except Exception as e:
            raise CommandValidationError(
                command=str(command),
                reason=f"Security validation failed: {e}",
                details="Command contains potentially dangerous patterns",
            ) from e
