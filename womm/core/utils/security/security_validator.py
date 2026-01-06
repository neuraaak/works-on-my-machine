#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SECURITY VALIDATOR - Security Validation Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Security Validator - Utilities for validating commands and file paths.

Handles security validation for command execution and file operations.
Provides comprehensive security checks to prevent dangerous operations.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import re
from pathlib import Path

# Local imports
from ...exceptions.security.security_exceptions import (
    CommandValidationError,
    PathValidationError,
    SecurityUtilityError,
)

# ///////////////////////////////////////////////////////////////
# SECURITY VALIDATOR CLASS
# ///////////////////////////////////////////////////////////////


class SecurityValidator:
    """Validates commands and file paths for security concerns."""

    # Dangerous command patterns
    DANGEROUS_COMMANDS = {
        "rm": ["-rf", "--recursive", "--force"],
        "del": ["/s", "/q", "/f"],
        "format": ["c:", "d:", "/q", "/u"],
        "shutdown": ["/s", "/t", "0"],
        "taskkill": ["/f", "/im", "*"],
        "kill": ["-9", "-f"],
        "chmod": ["777", "000"],
        "chown": ["root:", "sudo:"],
    }

    # Dangerous file patterns
    DANGEROUS_FILE_PATTERNS = [
        r"\.\./\.\./",  # Directory traversal
        r"~/.ssh/",  # SSH keys
        r"/etc/",  # System files
        r"/var/log/",  # Log files
        r"/proc/",  # Process files
        r"/sys/",  # System files
        r"C:\\Windows\\",  # Windows system files
        r"C:\\System32\\",  # Windows system files
    ]

    # Allowed command patterns (whitelist approach)
    ALLOWED_COMMANDS = {
        "python",
        "python3",
        "pip",
        "pip3",
        "node",
        "npm",
        "npx",
        "yarn",
        "git",
        "git-*",
        "ruff",
        "black",
        "isort",
        "mypy",
        "eslint",
        "prettier",
        "cspell",
        "spellcheck",
        "echo",
        "cat",
        "ls",
        "dir",
        "mkdir",
        "rmdir",
        "cp",
        "copy",
        "mv",
        "move",
        "grep",
        "find",
        "sort",
        "uniq",
        "head",
        "tail",
        "wc",
        "curl",
        "wget",
        "tar",
        "zip",
        "unzip",
        "chmod",
        "chown",  # With restrictions
    }

    def __init__(self):
        """Initialize security validator."""
        self.logger = logging.getLogger(__name__)

    def validate_command(self, command: list[str]) -> bool:
        """Validate a command for security concerns.

        Args:
            command: Command to validate as list of strings

        Returns:
            bool: True if command is valid

        Raises:
            CommandValidationError: If command validation fails
            SecurityUtilityError: If unexpected error occurs during validation
        """
        try:
            if not command:
                raise CommandValidationError(
                    command="",
                    reason="Command cannot be empty",
                    details="Empty command list provided",
                )

            if not isinstance(command, list):
                raise CommandValidationError(
                    command=str(command),
                    reason=f"Command must be a list, got: {type(command)}",
                    details=f"Invalid command type: {type(command).__name__}",
                )

            if not all(isinstance(arg, str) for arg in command):
                raise CommandValidationError(
                    command=str(command),
                    reason="All command arguments must be strings",
                    details="Non-string arguments found in command list",
                )

            # Get the base command (first argument)
            base_command = command[0].lower()

            # Check if command is in whitelist
            if base_command not in self.ALLOWED_COMMANDS:
                raise CommandValidationError(
                    command=" ".join(command),
                    reason=f"Command '{base_command}' is not in allowed list",
                    details=f"Command '{base_command}' not found in whitelist",
                )

            # Check for dangerous patterns in the base command
            if self._has_dangerous_patterns(base_command):
                raise CommandValidationError(
                    command=" ".join(command),
                    reason=f"Command '{base_command}' contains dangerous patterns",
                    details="Command matches dangerous pattern rules",
                )

            # Check for dangerous arguments
            for arg in command[1:]:
                if self._is_dangerous_argument(base_command, arg):
                    raise CommandValidationError(
                        command=" ".join(command),
                        reason=f"Dangerous argument '{arg}' for command '{base_command}'",
                        details=f"Argument '{arg}' flagged as dangerous for '{base_command}'",
                    )

            # Additional command-specific validations
            if base_command in [
                "chmod",
                "chown",
            ] and not self._validate_permission_command(command):
                raise CommandValidationError(
                    command=" ".join(command),
                    reason=f"Invalid permission command: {' '.join(command)}",
                    details="Permission command validation failed",
                )

            return True

        except (CommandValidationError, SecurityUtilityError):
            # Re-raise security exceptions as-is
            raise
        except Exception as e:
            # Catch unexpected errors and wrap them
            raise SecurityUtilityError(
                message=f"Unexpected error during command validation: {e}",
                details=f"Exception type: {type(e).__name__}, Command: {command}",
            ) from e

    def validate_file_path(self, file_path: str) -> bool:
        """Validate a file path for security concerns.

        Args:
            file_path: File path to validate

        Returns:
            bool: True if file path is valid

        Raises:
            PathValidationError: If file path validation fails
            SecurityUtilityError: If unexpected error occurs during validation
        """
        try:
            if not file_path:
                raise PathValidationError(
                    path="",
                    reason="File path cannot be empty",
                    details="Empty file path provided",
                )

            if not isinstance(file_path, str):
                raise PathValidationError(
                    path=str(file_path),
                    reason=f"File path must be a string, got: {type(file_path)}",
                    details=f"Invalid path type: {type(file_path).__name__}",
                )

            # Check for dangerous patterns
            for pattern in self.DANGEROUS_FILE_PATTERNS:
                if re.search(pattern, file_path, re.IGNORECASE):
                    raise PathValidationError(
                        path=file_path,
                        reason=f"File path contains dangerous pattern: {pattern}",
                        details=f"Path matches dangerous pattern: {pattern}",
                    )

            # Check for directory traversal attempts
            if ".." in file_path:
                # Count the number of ".." sequences
                traversal_count = file_path.count("..")
                if traversal_count > 2:  # Allow reasonable traversal
                    raise PathValidationError(
                        path=file_path,
                        reason=f"Excessive directory traversal: {traversal_count} levels",
                        details=f"Directory traversal count: {traversal_count}",
                    )

            # Check for absolute paths to system directories
            try:
                path = Path(file_path)
                if path.is_absolute() and self._is_system_directory(path):
                    raise PathValidationError(
                        path=file_path,
                        reason=f"Access to system directory: {file_path}",
                        details="Path resolves to system directory",
                    )
            except (OSError, ValueError) as e:
                raise PathValidationError(
                    path=file_path,
                    reason=f"Invalid file path format: {file_path}",
                    details=f"Path parsing failed: {type(e).__name__}: {e}",
                ) from e

            return True

        except (PathValidationError, SecurityUtilityError):
            # Re-raise security exceptions as-is
            raise
        except Exception as e:
            # Catch unexpected errors and wrap them
            raise SecurityUtilityError(
                message=f"Unexpected error during file path validation: {e}",
                details=f"Exception type: {type(e).__name__}, Path: {file_path}",
            ) from e

    def validate_directory_path(self, dir_path: str) -> bool:
        """Validate a directory path for security concerns.

        Args:
            dir_path: Directory path to validate

        Returns:
            bool: True if directory path is valid

        Raises:
            PathValidationError: If directory path validation fails
            SecurityUtilityError: If unexpected error occurs during validation
        """
        # Use the same validation as file paths
        return self.validate_file_path(dir_path)

    def _has_dangerous_patterns(self, command: str) -> bool:
        """Check if a command contains dangerous patterns.

        Args:
            command: Command to check

        Returns:
            bool: True if dangerous patterns found
        """
        dangerous_patterns = [
            r"rm\s*-rf",  # Recursive force remove
            r"del\s*/[sqf]",  # Windows delete with dangerous flags
            r"format\s*[cd]:",  # Format drives
            r"shutdown\s*/s",  # Shutdown system
            r"taskkill\s*/f",  # Force kill processes
            r"kill\s*-[9f]",  # Force kill
            r"chmod\s*[07]{3}",  # Dangerous permissions
            r"chown\s*root:",  # Change to root
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return True

        return False

    def _is_dangerous_argument(self, command: str, argument: str) -> bool:
        """Check if an argument is dangerous for a specific command.

        Args:
            command: Base command
            argument: Argument to check

        Returns:
            bool: True if argument is dangerous
        """
        command = command.lower()
        argument = argument.lower()

        # Check against dangerous command patterns
        if command in self.DANGEROUS_COMMANDS:
            dangerous_args = self.DANGEROUS_COMMANDS[command]
            for dangerous_arg in dangerous_args:
                if dangerous_arg in argument:
                    return True

        # Check for shell injection patterns
        shell_patterns = [
            r"[;&|`$()]",  # Shell operators
            r"\.\./",  # Directory traversal
            r"~/.ssh/",  # SSH keys
            r"/etc/",  # System files
            r"C:\\Windows\\",  # Windows system files
        ]

        return any(re.search(pattern, argument) for pattern in shell_patterns)

    def _validate_permission_command(self, command: list[str]) -> bool:
        """Validate permission-related commands (chmod, chown).

        Args:
            command: Command to validate

        Returns:
            bool: True if command is valid
        """
        if len(command) < 2:
            return False

        base_command = command[0].lower()
        command[-1]  # Last argument is usually the target

        if base_command == "chmod":
            # Check if permissions are reasonable
            if len(command) >= 2:
                permissions = command[1]
                # Allow common permission patterns
                allowed_patterns = [
                    r"^[0-7]{3,4}$",  # Octal permissions
                    r"^[ugoa]*[+-=][rwxXst]*$",  # Symbolic permissions
                ]
                for pattern in allowed_patterns:
                    if re.match(pattern, permissions):
                        return True
                return False

        elif base_command == "chown" and len(command) >= 2:
            owner = command[1]
            # Allow common owner patterns
            allowed_patterns = [
                r"^[a-zA-Z_][a-zA-Z0-9_]*$",  # Username
                r"^[a-zA-Z_][a-zA-Z0-9_]*:[a-zA-Z_][a-zA-Z0-9_]*$",  # user:group
            ]
            return any(re.match(pattern, owner) for pattern in allowed_patterns)

        return False

    def _is_system_directory(self, path: Path) -> bool:
        """Check if a path is a system directory.

        Args:
            path: Path to check

        Returns:
            bool: True if it's a system directory
        """
        system_dirs = [
            "/",  # Root
            "/bin",
            "/sbin",
            "/usr/bin",
            "/usr/sbin",
            "/etc",
            "/var",
            "/proc",
            "/sys",
            "C:\\",
            "C:\\Windows",
            "C:\\System32",
        ]

        try:
            path_str = str(path.resolve())
            for system_dir in system_dirs:
                if path_str.startswith(system_dir):
                    return True
        except Exception:
            # If path resolution fails, be conservative
            return True

        return False

    def get_security_report(self, command: list[str]) -> dict:
        """Get a detailed security report for a command.

        Args:
            command: Command to analyze

        Returns:
            dict: Security report

        Raises:
            SecurityUtilityError: If unexpected error occurs during analysis
        """
        try:
            # Try to validate the command
            try:
                self.validate_command(command)
                is_safe = True
                reason = "Command is safe"
            except CommandValidationError as e:
                is_safe = False
                reason = e.reason

            report = {
                "command": " ".join(command),
                "is_safe": is_safe,
                "reason": reason,
                "base_command": command[0] if command else None,
                "arguments": command[1:] if len(command) > 1 else [],
                "checks_performed": [],
            }

            if command:
                base_command = command[0].lower()
                report["checks_performed"] = [
                    f"Command '{base_command}' in whitelist: {base_command in self.ALLOWED_COMMANDS}",
                    f"Command has dangerous patterns: {self._has_dangerous_patterns(base_command)}",
                ]

                # Check each argument
                for i, arg in enumerate(command[1:], 1):
                    is_dangerous = self._is_dangerous_argument(base_command, arg)
                    report["checks_performed"].append(
                        f"Argument {i} '{arg}' is dangerous: {is_dangerous}"
                    )

            return report

        except Exception as e:
            raise SecurityUtilityError(
                message=f"Unexpected error during security report generation: {e}",
                details=f"Exception type: {type(e).__name__}, Command: {command}",
            ) from e


# ///////////////////////////////////////////////////////////////
# GLOBAL INSTANCE
# ///////////////////////////////////////////////////////////////

# Global instance for convenience
security_validator = SecurityValidator()
