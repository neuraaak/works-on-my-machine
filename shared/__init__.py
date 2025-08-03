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

# Result classes for structured returns
from .core.results import (
    BaseResult,
    CommandExecutionResult,
    ConfigurationResult,
    DependencyCheckResult,
    FileOperationResult,
    InstallationResult,
    ProjectDetectionResult,
    SecurityResult,
    SetupResult,
    ValidationResult,
    create_dependency_check_error,
    create_dependency_check_success,
    create_error_result,
    create_setup_error,
    create_setup_success,
    create_success_result,
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
    # Results
    "BaseResult",
    "DependencyCheckResult",
    "InstallationResult",
    "SetupResult",
    "ValidationResult",
    "SecurityResult",
    "ProjectDetectionResult",
    "FileOperationResult",
    "CommandExecutionResult",
    "ConfigurationResult",
    "create_success_result",
    "create_error_result",
    "create_dependency_check_success",
    "create_dependency_check_error",
    "create_setup_success",
    "create_setup_error",
]
