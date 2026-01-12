#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INSTALLATION RESULTS - Installation Result Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Installation result classes for Works On My Machine.

This module contains result classes for installation operations:
- Installation verification
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
# INSTALLATION VERIFICATION RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class InstallationResult(BaseResult):
    """Result for installation operations."""

    target_path: str = ""
    installation_location: str = ""
    files_copied: int = 0
    path_configured: bool = False
    executable_created: bool = False
    verification_passed: bool = False
    installation_time: float = 0.0
    details: dict | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.details is None:
            self.details = {}


@dataclass
class UninstallationResult(BaseResult):
    """Result for uninstallation operations."""

    removed_path: str = ""
    files_removed: int = 0
    path_cleaned: bool = False
    verification_passed: bool = False
    uninstallation_time: float = 0.0
    details: dict | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.details is None:
            self.details = {}


@dataclass
class WOMMInstallerVerificationResult(BaseResult):
    """Result for installation verification operations."""

    entry_path: str = ""
    path_configured: bool = False
    commands_accessible: bool = False
    executable_works: bool = False
    path_entries: list[str] | None = None
    accessible_commands: list[str] | None = None
    verification_time: float = 0.0

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.path_entries is None:
            self.path_entries = []
        if self.accessible_commands is None:
            self.accessible_commands = []


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "InstallationResult",
    "UninstallationResult",
    "WOMMInstallerVerificationResult",
]
