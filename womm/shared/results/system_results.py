#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM RESULTS - System Result Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System result classes for Works On My Machine.

This module contains result classes for system operations:
- System information
- PATH operations
- Environment refresh
- Environment verification
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass

# Local imports
from .base import BaseResult

# ///////////////////////////////////////////////////////////////
# SYSTEM INFO RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class SystemInfoResult(BaseResult):
    """Result for system information operations."""

    platform: str = ""
    platform_release: str = ""
    platform_version: str = ""
    architecture: str = ""
    processor: str = ""
    python_version: str = ""
    python_implementation: str = ""
    node: str = ""
    user: str = ""
    home: str = ""
    shell: str = ""
    terminal: str = ""
    path_separator: str = ""
    line_separator: str = ""
    package_managers: dict[str, dict[str, str | bool]] | None = None
    dev_environments: dict[str, dict[str, str | bool]] | None = None
    recommendations: dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.package_managers is None:
            self.package_managers = {}
        if self.dev_environments is None:
            self.dev_environments = {}
        if self.recommendations is None:
            self.recommendations = {}


# ///////////////////////////////////////////////////////////////
# PATH OPERATION RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class PathOperationResult(BaseResult):
    """Result for PATH operation results."""

    entry_path: str = ""
    operation: str = ""  # add, remove, verify
    path_modified: bool = False
    path_entries: list[str] | None = None
    modification_time: float = 0.0

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.path_entries is None:
            self.path_entries = []


# ///////////////////////////////////////////////////////////////
# ENVIRONMENT REFRESH RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class EnvironmentRefreshResult(BaseResult):
    """Result for environment refresh operations."""

    platform: str = ""
    refresh_method: str = ""  # registry, shell_config, etc.
    path_refreshed: bool = False
    environment_info: dict[str, str] | None = None
    refresh_time: float = 0.0

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.environment_info is None:
            self.environment_info = {}


# ///////////////////////////////////////////////////////////////
# ENVIRONMENT VERIFICATION RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class EnvironmentVerificationResult(BaseResult):
    """Result for environment verification operations."""

    command: str = ""
    command_accessible: bool = False
    verification_method: str = ""  # refresh_env_cmd, direct_test, etc.
    verification_time: float = 0.0
    temp_script_path: str | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.temp_script_path is None:
            self.temp_script_path = ""


# ///////////////////////////////////////////////////////////////
# SYSTEM DETECTION RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class SystemDetectionResult(BaseResult):
    """Result for system detection operations."""

    system_data: dict | None = None
    detection_time: float = 0.0

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.system_data is None:
            self.system_data = {}


# ///////////////////////////////////////////////////////////////
# PREREQUISITES CHECK RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class PrerequisitesCheckResult(BaseResult):
    """Result for prerequisites checking operations."""

    checked_tools: list[str] | None = None
    results: dict | None = None
    missing_tools: list[str] | None = None
    check_time: float = 0.0

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.checked_tools is None:
            self.checked_tools = []
        if self.results is None:
            self.results = {}
        if self.missing_tools is None:
            self.missing_tools = []


# ///////////////////////////////////////////////////////////////
# PREREQUISITES INSTALL RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class PrerequisitesInstallResult(BaseResult):
    """Result for prerequisites installation operations."""

    selected_tools: list[str] | None = None
    installation_results: dict | None = None
    failed_installations: list[str] | None = None
    install_time: float = 0.0

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.selected_tools is None:
            self.selected_tools = []
        if self.installation_results is None:
            self.installation_results = {}
        if self.failed_installations is None:
            self.failed_installations = []


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "EnvironmentRefreshResult",
    "EnvironmentVerificationResult",
    "PathOperationResult",
    "PrerequisitesCheckResult",
    "PrerequisitesInstallResult",
    "SystemDetectionResult",
    "SystemInfoResult",
]
