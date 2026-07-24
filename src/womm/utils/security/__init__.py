#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UTILS SECURITY - Security Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for security validation operations.

This package contains stateless utility functions for security
validation and command/path validation operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .security_validation_utils import (
    has_dangerous_command_patterns,
    has_dangerous_file_patterns,
    has_excessive_traversal,
    is_dangerous_argument,
    is_system_directory,
    validate_chmod_permissions,
    validate_chown_owner,
    validate_permission_command,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "has_dangerous_command_patterns",
    "has_dangerous_file_patterns",
    "has_excessive_traversal",
    "is_dangerous_argument",
    "is_system_directory",
    "validate_chmod_permissions",
    "validate_chown_owner",
    "validate_permission_command",
]
