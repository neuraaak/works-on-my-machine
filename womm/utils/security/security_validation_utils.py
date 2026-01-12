#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SECURITY VALIDATION UTILS - Pure Security Validation Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure security validation functions for Works On My Machine.

This module contains stateless utility functions for security validation
that can be used independently without class instantiation.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import re
from pathlib import Path

# Local imports
from ...shared.configs.security.security_patterns_config import SecurityPatternsConfig

# ///////////////////////////////////////////////////////////////
# COMMAND VALIDATION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def has_dangerous_command_patterns(command: str) -> bool:
    """Check if a command contains dangerous patterns.

    Args:
        command: Command to check

    Returns:
        bool: True if dangerous patterns found
    """
    for pattern in SecurityPatternsConfig.DANGEROUS_COMMAND_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True
    return False


def is_dangerous_argument(command: str, argument: str) -> bool:
    """Check if an argument is dangerous for a specific command.

    Args:
        command: Base command (lowercase)
        argument: Argument to check

    Returns:
        bool: True if argument is dangerous
    """
    command_lower = command.lower()
    argument_lower = argument.lower()

    # Check against dangerous command patterns
    if command_lower in SecurityPatternsConfig.DANGEROUS_COMMANDS:
        dangerous_args = SecurityPatternsConfig.DANGEROUS_COMMANDS[command_lower]
        for dangerous_arg in dangerous_args:
            if dangerous_arg in argument_lower:
                return True

    # Check for shell injection patterns
    return any(
        re.search(pattern, argument_lower)
        for pattern in SecurityPatternsConfig.SHELL_INJECTION_PATTERNS
    )


def validate_chmod_permissions(permissions: str) -> bool:
    """Validate chmod permission string.

    Args:
        permissions: Permission string to validate

    Returns:
        bool: True if permissions are valid
    """
    return any(
        re.match(pattern, permissions)
        for pattern in SecurityPatternsConfig.CHMOD_ALLOWED_PATTERNS
    )


def validate_chown_owner(owner: str) -> bool:
    """Validate chown owner string.

    Args:
        owner: Owner string to validate

    Returns:
        bool: True if owner is valid
    """
    return any(
        re.match(pattern, owner)
        for pattern in SecurityPatternsConfig.CHOWN_ALLOWED_PATTERNS
    )


def validate_permission_command(command: list[str]) -> bool:
    """Validate permission-related commands (chmod, chown).

    Args:
        command: Command to validate

    Returns:
        bool: True if command is valid
    """
    if len(command) < 2:
        return False

    base_command = command[0].lower()

    if base_command == "chmod":
        permissions = command[1]
        return validate_chmod_permissions(permissions)

    if base_command == "chown":
        owner = command[1]
        return validate_chown_owner(owner)

    return False


# ///////////////////////////////////////////////////////////////
# PATH VALIDATION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def has_dangerous_file_patterns(file_path: str) -> bool:
    """Check if a file path contains dangerous patterns.

    Args:
        file_path: File path to check

    Returns:
        bool: True if dangerous patterns found
    """
    return any(
        re.search(pattern, file_path, re.IGNORECASE)
        for pattern in SecurityPatternsConfig.DANGEROUS_FILE_PATTERNS
    )


def has_excessive_traversal(file_path: str, max_traversal: int = 2) -> bool:
    """Check if a file path has excessive directory traversal.

    Args:
        file_path: File path to check
        max_traversal: Maximum allowed traversal levels

    Returns:
        bool: True if traversal is excessive
    """
    if ".." not in file_path:
        return False
    traversal_count = file_path.count("..")
    return traversal_count > max_traversal


def is_system_directory(path: Path) -> bool:
    """Check if a path is a system directory.

    Args:
        path: Path to check

    Returns:
        bool: True if it's a system directory
    """
    try:
        path_str = str(path.resolve())
        return any(
            path_str.startswith(system_dir)
            for system_dir in SecurityPatternsConfig.SYSTEM_DIRECTORIES
        )
    except Exception:
        # If path resolution fails, be conservative
        return True
