#!/usr/bin/env python3
"""
Security utilities for WOMM CLI.
Provides security validation and secure command execution.
"""

import sys
from pathlib import Path

# Add shared modules to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))

# Import security modules
import importlib.util

# Check if security modules are available
SECURITY_AVAILABLE = (
    importlib.util.find_spec("shared.core.cli_manager") is not None and
    importlib.util.find_spec("shared.security.security_validator") is not None
)

if SECURITY_AVAILABLE:
    from shared.security.security_validator import SecurityValidator
    security_validator = SecurityValidator()

    def validate_user_input(value, input_type):
        """Validate user input using security validator."""
        return security_validator.validate_user_input(value, input_type)

    def run_secure_command(cmd, description):
        """Secure command execution when security modules are available."""
        from shared.core.cli_manager import run_secure
        result = run_secure(cmd, description)
        # Ensure the result has a success attribute
        if not hasattr(result, "success"):
            result.success = result.returncode == 0
        return result

else:
    # Fallback functions if security modules are not available
    def validate_user_input(_value, _input_type):
        """Fallback validation function when security modules are not available."""
        return True, ""

    def run_secure_command(cmd, description):
        """Fallback secure command execution when security modules are not available."""
        from shared.core.cli_manager import run_secure
        result = run_secure(cmd, description)
        # Ensure the result has a success attribute
        if not hasattr(result, "success"):
            result.success = result.returncode == 0
        return result

    security_validator = None

# Export security functions
__all__ = [
    "SECURITY_AVAILABLE",
    "security_validator",
    "validate_user_input",
    "run_secure_command",
]
