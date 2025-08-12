#!/usr/bin/env python3
"""
Security utilities for WOMM CLI.
Provides security validation and secure command execution.
Assume security modules are available (no fallbacks).
"""

from womm.core.security.security_validator import (
    security_validator,
    validate_user_input,
)
from womm.core.utils.cli_manager import run_secure


def run_secure_command(cmd, description):
    """Secure command execution using the CLI manager with validation."""
    result = run_secure(cmd, description)
    if not hasattr(result, "success"):
        result.success = result.returncode == 0
    return result


__all__ = [
    "security_validator",
    "validate_user_input",
    "run_secure_command",
]
