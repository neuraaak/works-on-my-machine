#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CLI UTILS - Unified CLI Manager
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Unified CLI Manager for Works On My Machine.

Handles command execution with optional security validation.
Provides a unified interface for running commands with proper error handling,
timeout management, and security validation.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import subprocess
import time
from pathlib import Path

# Local imports
# Import specialized exceptions
from ..exceptions.cli import (
    CLIUtilityError,
    CommandExecutionError,
    CommandValidationError,
    TimeoutError,
)

# ///////////////////////////////////////////////////////////////
# COMMAND RESULT CLASS
# ///////////////////////////////////////////////////////////////


class CommandResult:
    """Enhanced command result with security information."""

    def __init__(
        self,
        returncode: int,
        stdout: str = "",
        stderr: str = "",
        command: list[str] | None = None,
        cwd: Path | None = None,
        security_validated: bool = False,
        execution_time: float = 0.0,
    ) -> None:
        """Initialize command result.

        Args:
            returncode: Return code from command execution
            stdout: Standard output
            stderr: Standard error output
            command: Command that was executed
            cwd: Working directory
            security_validated: Whether command was security validated
            execution_time: Execution time in seconds
        """
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.command = command or []
        self.cwd = cwd
        self.security_validated = security_validated
        self.execution_time = execution_time

    @property
    def success(self) -> bool:
        """Check if command execution was successful."""
        return self.returncode == 0

    def __bool__(self):
        """Return a boolean representation of the result."""
        return self.success

    def __str__(self):
        """Return a string representation of the result."""
        return f"CommandResult(success={self.success}, validated={self.security_validated}, time={self.execution_time:.2f}s)"


# ///////////////////////////////////////////////////////////////
# CLI UTILS CLASS
# ///////////////////////////////////////////////////////////////


class CLIUtils:
    """Unified CLI manager with optional security validation."""

    def __init__(
        self,
        default_cwd: str | Path | None = None,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> None:
        """Initialize CLI manager.

        Args:
            default_cwd: Default working directory
            timeout: Command timeout in seconds
            max_retries: Maximum number of retries for failed commands
            retry_delay: Delay between retries in seconds

        Raises:
            CLIUtilityError: If initialization parameters are invalid
        """
        try:
            # Validate initialization parameters
            self._validate_init_parameters(timeout, max_retries, retry_delay)

            self.default_cwd = Path(default_cwd) if default_cwd else Path.cwd()
            self.timeout = timeout
            self.max_retries = max_retries
            self.retry_delay = retry_delay
            self.logger = logging.getLogger(__name__)

        except (
            CLIUtilityError,
            CommandExecutionError,
            CommandValidationError,
            TimeoutError,
        ):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise CLIUtilityError(
                message=f"Unexpected error during CLI manager initialization: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def run(
        self,
        command: str | list[str],
        description: str = "",
        cwd: str | Path | None = None,
        validate_security: bool = False,
        **kwargs: dict,
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
            CLIUtilityError: If command validation fails
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
                raise CLIUtilityError(
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
            CLIUtilityError,
            CommandValidationError,
            TimeoutError,
            CommandExecutionError,
        ):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise CLIUtilityError(
                message=f"Unexpected error during command execution: {e}",
                details=f"Exception type: {type(e).__name__}, Command: {command}",
            ) from e

    def _execute_command(
        self,
        cmd: list[str],
        cwd: Path,
        **kwargs: dict,
    ) -> subprocess.CompletedProcess[str]:
        """Execute a single command attempt.

        Args:
            cmd: Command to execute as list of strings
            cwd: Working directory
            **kwargs: Additional subprocess arguments

        Returns:
            subprocess.CompletedProcess: Result of command execution

        Raises:
            CLIUtilityError: If command validation fails
            subprocess.TimeoutExpired: If command times out
            subprocess.SubprocessError: If command execution fails
        """
        try:
            # Validate command format
            if not isinstance(cmd, list) or not all(
                isinstance(arg, str) for arg in cmd
            ):
                raise CLIUtilityError(
                    message=f"Command must be a list of strings, got: {type(cmd)}",
                    details=f"Invalid command format: {type(cmd).__name__}",
                )

            if not cmd:
                raise CLIUtilityError(
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

            for key, value in kwargs.items():
                if key in valid_subprocess_args:
                    subprocess_args[key] = value

            # Execute command with explicit security validation
            # The command has already been validated by the calling method
            return subprocess.run(cmd, **subprocess_args)  # noqa: S603

        except (CLIUtilityError, subprocess.TimeoutExpired, subprocess.SubprocessError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise CLIUtilityError(
                message=f"Unexpected error during command execution: {e}",
                details=f"Exception type: {type(e).__name__}, Command: {cmd}",
            ) from e

    def run_silent(self, command: str | list[str], **kwargs: dict) -> CommandResult:
        """Execute a command in silent mode.

        Args:
            command: Command to execute
            **kwargs: Additional arguments for run method

        Returns:
            CommandResult: Result of command execution
        """
        return self.run(command, **kwargs)

    def run_secure(
        self, command: str | list[str], description: str = "", **kwargs: dict
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

    def check_command_available(self, command: str) -> bool:
        """Check if a command is available and optionally validate security.

        Args:
            command: Command to check

        Returns:
            bool: True if command is available
        """
        try:
            if not command:
                return False

            import shutil

            if not shutil.which(command):
                return False

            # Additional security check
            try:
                from .security.security_validator import SecurityValidator

                validator = SecurityValidator()
                validator.validate_command([command])  # Lève exception si invalide
                return True
            except ImportError:
                # If security validator is not available, just check availability
                return True
            except Exception:
                # If security validation fails, command is not available
                return False

        except Exception as e:
            # Log but don't raise - this is a helper method
            self.logger.warning(
                f"Error checking command availability: {command}, Error: {e}"
            )
            return False

    def get_command_version(
        self, command: str, version_flag: str = "--version"
    ) -> str | None:
        """Get version of a command.

        Args:
            command: Command to get version for
            version_flag: Flag to use for version check

        Returns:
            Optional[str]: Version string or None if not available
        """
        try:
            if not command:
                return None

            if not self.check_command_available(command):
                return None

            result = self.run_silent([command, version_flag])
            if result.success and result.stdout.strip():
                # Extract version from output
                output = result.stdout.strip()
                if output:
                    # Take first line which probably contains version
                    first_line = output.split("\n")[0]
                    return first_line

            return None

        except Exception as e:
            # Log but don't raise - this is a helper method
            self.logger.warning(f"Error getting command version: {command}, Error: {e}")
            return None

    def _validate_init_parameters(
        self, timeout: int, max_retries: int, retry_delay: float
    ) -> None:
        """Validate initialization parameters.

        Args:
            timeout: Command timeout in seconds
            max_retries: Maximum number of retries
            retry_delay: Delay between retries

        Raises:
            CLIUtilityError: If parameters are invalid
        """
        if timeout <= 0:
            raise CLIUtilityError(
                message=f"Timeout must be positive, got: {timeout}",
                details="Invalid timeout parameter for CLI manager initialization",
            )

        if max_retries < 0:
            raise CLIUtilityError(
                message=f"Max retries must be non-negative, got: {max_retries}",
                details="Invalid max_retries parameter for CLI manager initialization",
            )

        if retry_delay < 0:
            raise CLIUtilityError(
                message=f"Retry delay must be non-negative, got: {retry_delay}",
                details="Invalid retry_delay parameter for CLI manager initialization",
            )

    def _validate_command_input(self, command: str | list[str]) -> None:
        """Validate command input.

        Args:
            command: Command to validate

        Raises:
            CLIUtilityError: If command is invalid
        """
        if not command:
            raise CLIUtilityError(
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
            from .security.security_validator import SecurityValidator

            validator = SecurityValidator()
            validator.validate_command(command)  # Lève exception si invalide
        except ImportError:
            self.logger.warning("Security validator not available, skipping validation")
        except Exception as e:
            raise CommandValidationError(
                command=str(command),
                reason=f"Security validation failed: {e}",
                details="Command contains potentially dangerous patterns",
            ) from e


# Global instance
cli = CLIUtils()


def run_command(
    command: str | list[str], description: str = "", **kwargs: dict
) -> CommandResult:
    """Convenience function to run a command.

    Args:
        command: Command to execute
        description: Description for logging
        **kwargs: Additional arguments for CLIUtils.run

    Returns:
        CommandResult: Result of command execution
    """
    return cli.run(command, description, **kwargs)


def run_silent(command: str | list[str], **kwargs: dict) -> CommandResult:
    """Convenience function to run a command silently.

    Args:
        command: Command to execute
        **kwargs: Additional arguments for CLIUtils.run

    Returns:
        CommandResult: Result of command execution
    """
    return cli.run_silent(command, **kwargs)


def get_tool_version(tool: str, version_flag: str = "--version") -> str | None:
    """Get version of a tool.

    Args:
        tool: Tool name
        version_flag: Version flag to use

    Returns:
        Optional[str]: Version string or None
    """
    return cli.get_command_version(tool, version_flag)
