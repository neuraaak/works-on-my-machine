#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# RESULTS - Result Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Result classes for Works On My Machine.

This module provides structured data objects for all WOMM operations.
Defines standardized result classes for consistent return values across the system.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Type checking imports
if TYPE_CHECKING:
    from ..core.utils.lint.lint_utils import ToolResult

# ///////////////////////////////////////////////////////////////
# BASE RESULT CLASSES
# ///////////////////////////////////////////////////////////////


@dataclass
class BaseResult:
    """Base result class with common attributes."""

    success: bool
    message: str = ""
    error: str = ""

    def __bool__(self) -> bool:
        """Return success status as boolean."""
        return self.success

    def __str__(self) -> str:
        """Return string representation."""
        if self.success:
            return f"Success: {self.message}"
        else:
            return f"Failed: {self.error}"


# ///////////////////////////////////////////////////////////////
# DEPENDENCY MANAGEMENT RESULTS
# ///////////////////////////////////////////////////////////////


@dataclass
class DependencyCheckResult(BaseResult):
    """Result for dependency checking operations."""

    missing: list[str] | None = None
    available: list[str] | None = None
    all_available: bool = True

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.missing is None:
            self.missing = []
        if self.available is None:
            self.available = []
        self.all_available = len(self.missing) == 0


@dataclass
class InstallationResult(BaseResult):
    """Result for dependency installation operations."""

    installed: list[str] | None = None
    failed: list[str] | None = None
    skipped: list[str] | None = None
    installation_method: str = ""

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.installed is None:
            self.installed = []
        if self.failed is None:
            self.failed = []
        if self.skipped is None:
            self.skipped = []


# ///////////////////////////////////////////////////////////////
# PROJECT MANAGEMENT RESULTS
# ///////////////////////////////////////////////////////////////


@dataclass
class SetupResult(BaseResult):
    """Result for project setup operations."""

    project_path: Path | None = None
    project_name: str = ""
    files_created: list[str] | None = None
    tools_configured: list[str] | None = None
    warnings: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.files_created is None:
            self.files_created = []
        if self.tools_configured is None:
            self.tools_configured = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class ProjectDetectionResult(BaseResult):
    """Result for project type detection."""

    project_type: str = ""
    confidence: float = 0.0
    detected_files: list[str] | None = None
    configuration_files: dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.detected_files is None:
            self.detected_files = []
        if self.configuration_files is None:
            self.configuration_files = {}


# ///////////////////////////////////////////////////////////////
# VALIDATION AND SECURITY RESULTS
# ///////////////////////////////////////////////////////////////


@dataclass
class ValidationResult(BaseResult):
    """Result for input validation operations."""

    input_type: str = ""
    input_value: str = ""
    validation_rules: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.validation_rules is None:
            self.validation_rules = []


@dataclass
class SecurityResult(BaseResult):
    """Result for security validation operations."""

    security_level: str = "low"  # low, medium, high
    threats_detected: list[str] | None = None
    recommendations: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.threats_detected is None:
            self.threats_detected = []
        if self.recommendations is None:
            self.recommendations = []


# ///////////////////////////////////////////////////////////////
# FILE AND COMMAND OPERATION RESULTS
# ///////////////////////////////////////////////////////////////


@dataclass
class FileOperationResult(BaseResult):
    """Result for file operations."""

    operation: str = ""  # copy, create, delete, etc.
    source_path: Path | None = None
    destination_path: Path | None = None
    file_size: int = 0
    operation_time: float = 0.0


@dataclass
class CommandExecutionResult(BaseResult):
    """Result for command execution."""

    command: list[str] | None = None
    return_code: int = 0
    stdout: str = ""
    stderr: str = ""
    execution_time: float = 0.0
    security_validated: bool = False

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.command is None:
            self.command = []


# ///////////////////////////////////////////////////////////////
# CONFIGURATION RESULTS
# ///////////////////////////////////////////////////////////////


@dataclass
class ConfigurationResult(BaseResult):
    """Result for configuration operations."""

    config_type: str = ""  # vscode, git, cspell, etc.
    config_files: list[str] | None = None
    settings_applied: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.config_files is None:
            self.config_files = []
        if self.settings_applied is None:
            self.settings_applied = {}


# ///////////////////////////////////////////////////////////////
# LINTING AND SPELL CHECKING RESULTS
# ///////////////////////////////////////////////////////////////


@dataclass
class LintSummary(BaseResult):
    """Summary of all linting operations."""

    total_files: int = 0
    total_issues: int = 0
    total_fixed: int = 0
    tool_results: dict[str, "ToolResult"] = field(default_factory=dict)
    scan_summary: dict[str, Any] | None = None


@dataclass
class ToolResult(BaseResult):
    """Result of a tool execution."""

    tool_name: str = ""
    files_checked: int = 0
    issues_found: int = 0
    fixed_issues: int = 0
    data: Any | None = None


@dataclass
class SpellResult(BaseResult):
    """Result of a spell checking operation."""

    data: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.data is None:
            self.data = {}


@dataclass
class SpellSummary(BaseResult):
    """Summary of spell checking operations."""

    total_files: int = 0
    files_with_errors: int = 0
    total_errors: int = 0
    errors_by_file: dict[str, Any] | None = None
    suggestions: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.errors_by_file is None:
            self.errors_by_file = {}
        if self.suggestions is None:
            self.suggestions = []


# ///////////////////////////////////////////////////////////////
# FACTORY FUNCTIONS
# ///////////////////////////////////////////////////////////////


def create_success_result(message: str = "", **kwargs: Any) -> BaseResult:
    """Create a successful result.

    Args:
        message: Success message
        **kwargs: Additional attributes for the result

    Returns:
        BaseResult: A successful result object
    """
    return BaseResult(success=True, message=message, **kwargs)


def create_error_result(error: str = "", **kwargs: Any) -> BaseResult:
    """Create an error result.

    Args:
        error: Error message
        **kwargs: Additional attributes for the result

    Returns:
        BaseResult: An error result object
    """
    return BaseResult(success=False, error=error, **kwargs)


def create_dependency_check_success(
    available: list[str], missing: list[str] | None = None
) -> DependencyCheckResult:
    """Create a successful dependency check result.

    Args:
        available: List of available dependencies
        missing: List of missing dependencies

    Returns:
        DependencyCheckResult: A successful dependency check result
    """
    if missing is None:
        missing = []
    return DependencyCheckResult(
        success=True,
        message=f"Found {len(available)} available dependencies",
        available=available,
        missing=missing,
        all_available=len(missing) == 0,
    )


def create_dependency_check_error(
    error: str, available: list[str] | None = None, missing: list[str] | None = None
) -> DependencyCheckResult:
    """Create an error dependency check result.

    Args:
        error: Error message
        available: List of available dependencies
        missing: List of missing dependencies

    Returns:
        DependencyCheckResult: An error dependency check result
    """
    if available is None:
        available = []
    if missing is None:
        missing = []
    return DependencyCheckResult(
        success=False,
        error=error,
        available=available,
        missing=missing,
        all_available=False,
    )


def create_setup_success(
    project_path: Path, project_name: str, files_created: list[str] | None = None
) -> SetupResult:
    """Create a successful setup result.

    Args:
        project_path: Path to the project directory
        project_name: Name of the project
        files_created: List of files created during setup

    Returns:
        SetupResult: A successful setup result
    """
    if files_created is None:
        files_created = []
    return SetupResult(
        success=True,
        message=f"Project '{project_name}' setup completed successfully",
        project_path=project_path,
        project_name=project_name,
        files_created=files_created,
    )


def create_setup_error(error: str, project_name: str = "") -> SetupResult:
    """Create an error setup result.

    Args:
        error: Error message
        project_name: Name of the project

    Returns:
        SetupResult: An error setup result
    """
    return SetupResult(success=False, error=error, project_name=project_name)
