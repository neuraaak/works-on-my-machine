#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SECURITY - Security Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Security utilities for Works On My Machine.

This module provides security validation and secure command execution with multiple
execution modes to replace direct subprocess usage.

USAGE GUIDE:

    # For user commands (strict validation)
    result = run_secure_command("python --version", "Check Python")

    # For internal commands (no validation)
    result = run_command(["git", "init"], "Initialize repo", cwd=project_path)

    # For silent operations (replace subprocess.run)
    result = run_silent(["pip", "install", "package"], cwd=venv_path)

MIGRATION FROM SUBPROCESS:

    # OLD (causes Ruff warnings):
    subprocess.run(["git", "init"], cwd=path, check=True, capture_output=True)  # noqa: S603

    # NEW (no warnings):
    result = run_silent(["git", "init"], cwd=path)
    if not result.success:
        raise SecurityError(
            operation="run_silent",
            command="git init",
            reason="Git initialization failed",
            details=result.stderr,
        )

Assume security modules are available (no fallbacks).
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import TYPE_CHECKING, Any

# Local imports
from ..core.exceptions import SecurityError

# Type checking imports
if TYPE_CHECKING:
    from ..core.utils.cli_utils import CommandResult

# ///////////////////////////////////////////////////////////////
# VALIDATION RESULT CLASS
# ///////////////////////////////////////////////////////////////


class ValidationFailedResult:
    """Result object for failed command validation."""

    def __init__(self, error_msg: str) -> None:
        """Initialize validation failed result.

        Args:
            error_msg: Error message describing validation failure
        """
        self.success = False
        self.returncode = 1
        self.stderr = error_msg
        self.stdout = ""


# ///////////////////////////////////////////////////////////////
# SECURE COMMAND EXECUTION
# ///////////////////////////////////////////////////////////////


def run_secure_command(cmd: str | list[str], description: str = "") -> "CommandResult":
    """Secure command execution with validation.

    Args:
        cmd: Command to execute (string or list)
        description: Description for logging

    Returns:
        Command result object with success attribute
    """
    try:
        # Import CLI manager for secure execution
        from ..core.utils.cli_utils import run_secure
        from ..core.utils.security.security_validator import security_validator

        # Validate command first
        command_list = cmd.split() if isinstance(cmd, str) else list(cmd)
        is_valid, error = security_validator.validate_command(command_list)

        if not is_valid:
            return ValidationFailedResult(f"Command validation failed: {error}")

        # Execute with secure CLI manager
        result = run_secure(cmd, description)
        if not hasattr(result, "success"):
            result.success = result.returncode == 0
        return result

    except ImportError as e:
        raise SecurityError(
            operation="run_secure_command",
            command=str(cmd),
            reason="Failed to import required security modules",
            details=str(e),
        ) from e
    except Exception as e:
        raise SecurityError(
            operation="run_secure_command",
            command=str(cmd),
            reason="Unexpected error during secure command execution",
            details=str(e),
        ) from e


# ///////////////////////////////////////////////////////////////
# STANDARD COMMAND EXECUTION
# ///////////////////////////////////////////////////////////////


def run_command(
    cmd: str | list[str], description: str = "", **kwargs: Any
) -> "CommandResult":
    """Standard command execution without security validation.

    Use this for internal commands that need to bypass strict validation
    (e.g., system commands, package managers, etc.).

    Args:
        cmd: Command to execute (string or list)
        description: Description for logging
        **kwargs: Additional arguments (cwd, timeout, etc.)

    Returns:
        Command result object with success attribute
    """
    try:
        # Import CLI manager for standard execution
        from ..core.utils.cli_utils import run_command as cli_run_command

        result = cli_run_command(cmd, description, **kwargs)
        if not hasattr(result, "success"):
            result.success = result.returncode == 0
        return result

    except ImportError as e:
        raise SecurityError(
            operation="run_command",
            command=str(cmd),
            reason="Failed to import required CLI modules",
            details=str(e),
        ) from e
    except Exception as e:
        raise SecurityError(
            operation="run_command",
            command=str(cmd),
            reason="Unexpected error during command execution",
            details=str(e),
        ) from e


# ///////////////////////////////////////////////////////////////
# SILENT COMMAND EXECUTION
# ///////////////////////////////////////////////////////////////


def run_silent(cmd: str | list[str], **kwargs: Any) -> "CommandResult":
    """Silent command execution without output.

    Convenience wrapper for subprocess.run replacement that avoids
    Ruff security warnings.

    Args:
        cmd: Command to execute (string or list)
        **kwargs: Additional arguments (cwd, timeout, etc.)

    Returns:
        Command result object with success attribute
    """
    try:
        # Import CLI manager for silent execution
        from ..core.utils.cli_utils import run_silent as cli_run_silent

        result = cli_run_silent(cmd, **kwargs)
        if not hasattr(result, "success"):
            result.success = result.returncode == 0
        return result

    except ImportError as e:
        raise SecurityError(
            operation="run_silent",
            command=str(cmd),
            reason="Failed to import required CLI modules",
            details=str(e),
        ) from e
    except Exception as e:
        raise SecurityError(
            operation="run_silent",
            command=str(cmd),
            reason="Unexpected error during silent command execution",
            details=str(e),
        ) from e


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "run_secure_command",
    "run_command",
    "run_silent",
]
