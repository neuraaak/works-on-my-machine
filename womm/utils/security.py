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
try:
    from shared.security.secure_cli_manager import run_secure_command
    from shared.security.security_validator import (
        security_validator,
        validate_user_input,
    )

    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False

    # Fallback functions if security modules are not available
    def validate_user_input(_value, _input_type):
        """Fallback validation function when security modules are not available."""
        return True, ""

    def run_secure_command(cmd, description):
        """Fallback secure command execution when security modules are not available."""
        from shared.core.cli_manager import run_command
        result = run_command(cmd, description)
        # Ensure the result has a success attribute
        if not hasattr(result, "success"):
            result.success = result.returncode == 0
        return result

# Export security functions
__all__ = [
    "SECURITY_AVAILABLE",
    "security_validator",
    "validate_user_input",
    "run_secure_command",
]
