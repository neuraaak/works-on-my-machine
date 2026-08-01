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
from datetime import datetime
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
    dry_run: bool = False
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

    @property
    def entries_by_type(self) -> dict[str, int]:
        """Entry count per context type, for the types actually present."""
        return {
            context_type: len(context_entries)
            for context_type, context_entries in (self.entries or {}).items()
        }

    @property
    def total_entries(self) -> int:
        """Total number of registered entries, across all context types."""
        return sum(
            len(context_entries) for context_entries in (self.entries or {}).values()
        )


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
class ScriptInfoResult(BaseResult):
    """Result for script type detection and command building."""

    script_path: str = ""
    script_type: str = ""
    extension: str = ""
    default_icon: str | None = None
    context_params: str = ""
    command: str = ""
    # Enriched by ContextMenuInterface.get_script_info(); left unset by the
    # detector itself, which knows nothing about icons or the registry.
    resolved_icon: str | None = None
    registry_key: str | None = None


@dataclass
class ScriptValidationResult(BaseResult):
    """Result for validating that a script can be registered."""

    script_path: str = ""
    script_type: str = ""
    command: str = ""
    permissions_ok: bool = False
    permissions_error: str = ""
    compatibility_ok: bool = False
    compatibility_error: str = ""


@dataclass
class BackupFileInfo:
    """A single registry backup file's metadata (plain record, not a Result)."""

    filename: str
    filepath: str
    size_bytes: int = 0
    modified_time: datetime | None = None
    entry_count: int = 0
    backup_version: str = "unknown"
    backup_timestamp: str = "unknown"
    context_types: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.context_types is None:
            self.context_types = []

    @property
    def size_kb(self) -> float:
        """File size in kilobytes."""
        return self.size_bytes / 1024


@dataclass
class BackupFileResult(BaseResult):
    """Result for creating, copying, or merging a registry backup file."""

    filepath: str = ""
    metadata: dict | None = None
    data: dict | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.metadata is None:
            self.metadata = {}
        if self.data is None:
            self.data = {}


@dataclass
class BackupFileListResult(BaseResult):
    """Result for listing registry backup files."""

    backup_directory: str = ""
    backups: list[BackupFileInfo] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.backups is None:
            self.backups = []


@dataclass
class BackupDataResult(BaseResult):
    """Result for loading or inspecting a registry backup file."""

    filepath: str = ""
    data: dict | None = None
    metadata: dict | None = None
    entry_stats: dict | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.data is None:
            self.data = {}
        if self.metadata is None:
            self.metadata = {}
        if self.entry_stats is None:
            self.entry_stats = {}


@dataclass
class BackupCleanupResult(BaseResult):
    """Result for pruning old registry backup files."""

    deleted_files: list[str] | None = None
    kept_files: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.deleted_files is None:
            self.deleted_files = []
        if self.kept_files is None:
            self.kept_files = []

    @property
    def deleted_count(self) -> int:
        """Number of backup files removed."""
        return len(self.deleted_files or [])

    @property
    def kept_count(self) -> int:
        """Number of backup files retained."""
        return len(self.kept_files or [])


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
    "BackupCleanupResult",
    "BackupDataResult",
    "BackupFileInfo",
    "BackupFileListResult",
    "BackupFileResult",
    "ContextBackupResult",
    "ContextCherryPickResult",
    "ContextEntriesResult",
    "ContextRegistryResult",
    "ContextRestoreResult",
    "ContextSetupResult",
    "ContextValidationResult",
    "ScriptInfoResult",
    "ScriptRegistrationResult",
    "ScriptUnregistrationResult",
    "ScriptValidationResult",
]
