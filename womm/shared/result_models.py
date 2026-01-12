#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# RESULTS - Result Classes (Unified Export)
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Result classes for Works On My Machine.

This module provides a unified export of all result classes from
base, services, and interfaces modules for backward compatibility.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path
from typing import Any

# Local imports
from .results import (
    BaseResult,
    CommandResult,
    ConfigurationResult,
    ContextRegistryResult,
    ContextValidationResult,
    CSpellConfigResult,
    DependencyCheckResult,
    DevToolResult,
    DictionaryResult,
    FileOperationResult,
    FileScanResult,
    InstallationResult,
    LintSummaryResult,
    PackageManagerResult,
    PathOperationResult,
    ProjectDetectionResult,
    RuntimeResult,
    SecurityResult,
    SetupResult,
    SpellCheckResult,
    SpellResult,
    SpellSummary,
    SystemInfoResult,
    ToolResult,
    ValidationResult,
    WOMMInstallerVerificationResult,
)

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


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "BaseResult",
    "CSpellConfigResult",
    "CommandResult",
    "ConfigurationResult",
    "ContextRegistryResult",
    "ContextValidationResult",
    "DependencyCheckResult",
    "DevToolResult",
    "DictionaryResult",
    "FileOperationResult",
    "FileScanResult",
    "InstallationResult",
    "LintSummaryResult",
    "PackageManagerResult",
    "PathOperationResult",
    "ProjectDetectionResult",
    "RuntimeResult",
    "SecurityResult",
    "SetupResult",
    "SpellCheckResult",
    "SpellResult",
    "SpellSummary",
    "SystemInfoResult",
    "ToolResult",
    "ValidationResult",
    "WOMMInstallerVerificationResult",
    "create_dependency_check_error",
    "create_dependency_check_success",
    "create_error_result",
    "create_setup_error",
    "create_setup_success",
    "create_success_result",
]
