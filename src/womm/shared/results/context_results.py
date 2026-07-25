#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT RESULTS - Context Result Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context result classes for Works On My Machine.

This module contains result classes for context menu operations:
- Context registry operations
- Context validation operations
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from typing import Any

# Local imports
from .base import BaseResult
from .security_results import ValidationResult

# ///////////////////////////////////////////////////////////////
# CONTEXT REGISTRY RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class ContextRegistryResult(BaseResult):
    """Result for context menu registry operations."""

    registry_path: str = ""
    command: str = ""
    display_name: str = ""
    icon_path: str | None = None
    entries: list[dict[str, str | None]] | None = None
    backup_data: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.entries is None:
            self.entries = []
        if self.backup_data is None:
            self.backup_data = {}


# ///////////////////////////////////////////////////////////////
# CONTEXT VALIDATION RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class ContextValidationResult(ValidationResult):
    """Result for context menu validation operations."""

    script_path: str = ""
    extension: str = ""
    file_size: int = 0
    label: str = ""
    registry_key: str = ""
    icon_path: str = ""
    icon_type: str = ""  # file, special, etc.
    has_permissions: bool = False
    compatible: bool = False
    windows_version: str = ""


# ///////////////////////////////////////////////////////////////
# SCRIPT REGISTRATION RESULTS
# ///////////////////////////////////////////////////////////////


@dataclass
class ScriptRegistrationResult(BaseResult):
    """Result for script registration in context menu."""

    script_path: str = ""
    script_type: str = ""
    label: str = ""
    icon_path: str | None = None
    registry_key: str = ""
    command: str = ""
    context_info: str = ""
    dry_run: bool = False
    success_count: int = 0
    total_paths: int = 0


@dataclass
class ScriptUnregistrationResult(BaseResult):
    """Result for script unregistration from context menu."""

    key_name: str = ""
    success_count: int = 0
    total_types: int = 0
    permission_errors: list[str] | None = None
    not_found_count: int = 0

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.permission_errors is None:
            self.permission_errors = []


# ///////////////////////////////////////////////////////////////
# BACKUP/RESTORE RESULTS
# ///////////////////////////////////////////////////////////////


@dataclass
class ContextBackupResult(BaseResult):
    """Result for context menu backup operation."""

    backup_file: str = ""
    entry_count: int = 0


@dataclass
class ContextRestoreResult(BaseResult):
    """Result for context menu restore operation."""

    backup_file: str = ""
    entry_count: int = 0


# ///////////////////////////////////////////////////////////////
# ENTRIES RESULTS
# ///////////////////////////////////////////////////////////////


@dataclass
class ContextEntriesResult(BaseResult):
    """Result for listing context menu entries."""

    entries: dict[str, list[dict[str, str | None]]] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.entries is None:
            self.entries = {}


@dataclass
class ContextStatusResult(BaseResult):
    """Result for context menu status check."""

    total_entries: int = 0
    entries_by_type: dict[str, int] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.entries_by_type is None:
            self.entries_by_type = {}


# ///////////////////////////////////////////////////////////////
# SETUP RESULTS
# ///////////////////////////////////////////////////////////////


@dataclass
class ContextSetupResult(BaseResult):
    """Result for quick setup of context menu tools."""

    success_count: int = 0
    total_tools: int = 0
    tools_registered: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.tools_registered is None:
            self.tools_registered = []


@dataclass
class ContextCherryPickResult(BaseResult):
    """Result for cherry-picking context menu entries from backups."""

    success_count: int = 0
    total_selected: int = 0
    selected_entries: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.selected_entries is None:
            self.selected_entries = []


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ContextBackupResult",
    "ContextCherryPickResult",
    "ContextEntriesResult",
    "ContextRegistryResult",
    "ContextSetupResult",
    "ContextStatusResult",
    "ContextValidationResult",
    "ContextRestoreResult",
    "ScriptRegistrationResult",
    "ScriptUnregistrationResult",
]
