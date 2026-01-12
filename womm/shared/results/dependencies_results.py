#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPENDENCIES RESULTS - Dependencies Result Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependencies result classes for Works On My Machine.

This module contains result classes for dependency management operations:
- Package manager operations
- Runtime management operations
- Development tools operations
- Dependency checking
- Installation operations
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
# DEPENDENCY CHECK RESULT
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


# ///////////////////////////////////////////////////////////////
# INSTALLATION RESULT
# ///////////////////////////////////////////////////////////////


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
# DEV TOOLS RESULT CLASS
# ///////////////////////////////////////////////////////////////


@dataclass
class DevToolResult(BaseResult):
    """Result of a development tool operation."""

    tool_name: str = ""
    language: str = ""
    tool_type: str = ""
    path: str | None = None


# ///////////////////////////////////////////////////////////////
# RUNTIME RESULT CLASS
# ///////////////////////////////////////////////////////////////


@dataclass
class RuntimeResult(BaseResult):
    """Result of a runtime operation."""

    runtime_name: str = ""
    version: str | None = None
    path: str | None = None


# ///////////////////////////////////////////////////////////////
# PACKAGE MANAGER RESULT CLASS
# ///////////////////////////////////////////////////////////////


@dataclass
class PackageManagerResult(BaseResult):
    """Result of a package manager operation."""

    package_manager_name: str = ""
    version: str | None = None
    platform: str | None = None
    priority: int | None = None
    panel: object | None = None


# ///////////////////////////////////////////////////////////////
# RUNTIME INSTALLATION RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class RuntimeInstallationResult(BaseResult):
    """Result of runtime installation check."""

    runtime_name: str = ""
    is_installed: bool = False
    version: str = ""


# ///////////////////////////////////////////////////////////////
# PACKAGE MANAGER AVAILABILITY RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class PackageManagerAvailabilityResult(BaseResult):
    """Result of package manager availability check."""

    manager_name: str = ""
    is_available: bool = False
    version: str = ""


# ///////////////////////////////////////////////////////////////
# PACKAGE MANAGER PLATFORM RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class PackageManagerPlatformResult(BaseResult):
    """Result for checking if package manager is for current platform."""

    manager_name: str = ""
    is_for_current_platform: bool = False
    current_platform: str = ""


# ///////////////////////////////////////////////////////////////
# DEV TOOL AVAILABILITY RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class DevToolAvailabilityResult(BaseResult):
    """Result of development tool availability check."""

    tool_name: str = ""
    is_available: bool = False
    language: str = ""


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "DependencyCheckResult",
    "DevToolAvailabilityResult",
    "DevToolResult",
    "InstallationResult",
    "PackageManagerAvailabilityResult",
    "PackageManagerPlatformResult",
    "PackageManagerResult",
    "RuntimeInstallationResult",
    "RuntimeResult",
]
