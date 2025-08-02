"""
Shared modules for Works On My Machine.

This package contains all shared utilities and tools used across the WOMM project.
"""

__version__ = "1.2.1"
__author__ = "Neuraaak"

# Core modules - only import the most essential functions
from .core.cli_manager import (
    CLIManager,
    CommandResult,
    check_tool_available,
    get_tool_version,
    run_command,
    run_interactive,
    run_silent,
)

# Note: Other modules are available but not imported by default to avoid circular dependencies
# Import them directly when needed:
# from shared.security.security_validator import security_validator
# from shared.tools.cspell_manager import install_cspell_global
# etc.

__all__ = [
    # Core
    "run_command",
    "run_silent",
    "run_interactive",
    "check_tool_available",
    "get_tool_version",
    "CLIManager",
    "CommandResult",
]
