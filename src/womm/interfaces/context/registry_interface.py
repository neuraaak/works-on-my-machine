#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT REGISTRY INTERFACE - Context Menu Backup Management
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Backup manager for context menu operations.

This module provides comprehensive backup management functionality
for Windows context menu entries, including creation, validation,
listing, and cleanup of backup files.

This interface never raises: every public method returns a typed Result.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Local imports
from ...shared.configs.context import ContextTypesConfig
from ...shared.configs.womm_setup import WOMMDeploymentConfig
from ...shared.paths import registry_backups_dir
from ...shared.results import (
    BackupCleanupResult,
    BackupDataResult,
    BackupFileInfo,
    BackupFileListResult,
    BackupFileResult,
)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class ContextRegistryInterface:
    """Manages context menu backup operations."""

    # Backup file format version
    BACKUP_VERSION = "1.0"

    # Maximum number of backup files to keep
    MAX_BACKUP_FILES = 10

    # Backup file retention period (days)
    BACKUP_RETENTION_DAYS = 30

    def __init__(self):
        """Initialize the backup manager."""
        self.logger = logging.getLogger(__name__)
        self.backup_dir = self.get_backup_directory()

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def get_backup_directory(self) -> Path:
        """
        Get the backup directory path, creating it if needed.

        Registry backups are user data: they live under ``~/.womm/backups/
        registry``. Falls back to the current directory only when that
        location is unwritable; never raises.
        """
        try:
            return registry_backups_dir()
        except OSError as e:
            self.logger.warning(f"Could not access WOMM backup directory: {e}")

        return Path(".")

    def create_backup_file(
        self,
        entries: dict,
        custom_filename: str | None = None,
        add_timestamp: bool = True,
    ) -> BackupFileResult:
        """
        Create a backup file with context menu entries.

        Args:
            entries: Dictionary containing context menu entries
            custom_filename: Optional custom filename (without extension)
            add_timestamp: Whether to add timestamp to filename

        Returns:
            BackupFileResult: written path and metadata; failure carries the error.
        """
        if not isinstance(entries, dict):
            return BackupFileResult(
                success=False,
                error=f"Entries must be a dictionary, got {type(entries).__name__}",
            )

        # Generate filename
        base_name = custom_filename or "context_menu_backup"

        if add_timestamp:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{base_name}_{timestamp}.json"
        else:
            filename = f"{base_name}.json"

        filepath = self.backup_dir / filename

        # Create backup data with metadata
        backup_data = self._create_backup_data(entries)

        # Write backup file
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
        except (OSError, TypeError, ValueError) as e:
            return BackupFileResult(
                success=False,
                filepath=str(filepath),
                error=f"Failed to write backup file: {e}",
            )

        return BackupFileResult(
            success=True,
            message=f"Backup written to {filepath}",
            filepath=str(filepath),
            metadata=backup_data["metadata"],
            data=backup_data,
        )

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _create_backup_data(self, entries: dict) -> dict:
        """
        Create backup data structure with metadata.

        Args:
            entries: Context menu entries

        Returns:
            Backup data dictionary with metadata
        """
        # Count total entries
        total_entries = sum(
            len(entries.get(context_type, []))
            for context_type in ["directory", "background"]
        )

        # Create metadata
        metadata = {
            "version": self.BACKUP_VERSION,
            "timestamp": datetime.now().isoformat(),
            "platform": "Windows",
            "total_entries": total_entries,
            "context_types": list(entries.keys()),
            "entry_counts": {
                context_type: len(entries.get(context_type, []))
                for context_type in ["directory", "background"]
            },
        }

        return {"metadata": metadata, "entries": entries}

    def list_backup_files(self, include_metadata: bool = True) -> BackupFileListResult:
        """
        List all available backup files with optional metadata.

        A backup whose metadata cannot be read is still listed, with the
        metadata fields left at their defaults.

        Args:
            include_metadata: Whether to include backup metadata

        Returns:
            BackupFileListResult: the discovered backups; failure carries the error.
        """
        pattern = "context_menu_backup_*.json"
        try:
            files = sorted(
                self.backup_dir.glob(pattern),
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            )
        except OSError as e:
            return BackupFileListResult(
                success=False,
                backup_directory=str(self.backup_dir),
                error=f"Could not access backup directory: {e}",
            )

        backups: list[BackupFileInfo] = []
        for file in files:
            try:
                stat = file.stat()
            except OSError as e:
                self.logger.warning(f"Failed to stat backup file {file.name}: {e}")
                continue

            info = BackupFileInfo(
                filename=file.name,
                filepath=str(file),
                size_bytes=stat.st_size,
                modified_time=datetime.fromtimestamp(stat.st_mtime),
            )

            if include_metadata:
                try:
                    with open(file, encoding="utf-8") as f:
                        metadata = json.load(f).get("metadata", {})
                    info.entry_count = metadata.get("total_entries", 0)
                    info.backup_version = metadata.get("version", "unknown")
                    info.backup_timestamp = metadata.get("timestamp", "unknown")
                    info.context_types = metadata.get("context_types", [])
                except (json.JSONDecodeError, OSError, AttributeError) as e:
                    self.logger.warning(
                        f"Failed to read metadata from {file.name}: {e}"
                    )

            backups.append(info)

        return BackupFileListResult(
            success=True,
            message=f"Found {len(backups)} backup file(s)",
            backup_directory=str(self.backup_dir),
            backups=backups,
        )

    def load_backup_file(self, filepath: str) -> BackupDataResult:
        """
        Load and validate a backup file.

        Args:
            filepath: Path to the backup file

        Returns:
            BackupDataResult: the parsed backup; failure carries the error.
        """
        if not filepath:
            return BackupDataResult(
                success=False, error="Filepath cannot be None or empty"
            )

        backup_path = Path(filepath)
        if not backup_path.exists():
            return BackupDataResult(
                success=False,
                filepath=filepath,
                error=f"Backup file not found: {filepath}",
            )

        try:
            with open(backup_path, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            return BackupDataResult(
                success=False,
                filepath=filepath,
                error=f"Could not read backup file: {e}",
            )

        # Validate backup format
        try:
            self._validate_backup_data(data)
        except ValueError as e:
            return BackupDataResult(
                success=False, filepath=filepath, error=f"Invalid backup file: {e}"
            )

        return BackupDataResult(
            success=True,
            message=f"Loaded backup {backup_path.name}",
            filepath=filepath,
            data=data,
            metadata=data.get("metadata", {}),
        )

    def _validate_backup_data(self, data: dict) -> None:
        """
        Validate backup data structure.

        Args:
            data: Backup data to validate

        Raises:
            ValueError: If data is None or invalid
        """
        # Input validation
        if data is None:
            raise ValueError("Backup data cannot be None")

        if not isinstance(data, dict):
            raise ValueError(
                f"Backup data must be a dictionary, got {type(data).__name__}"
            )

        # Check required top-level keys
        required_keys = WOMMDeploymentConfig.get_backup_required_keys()
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")

        # Validate metadata
        metadata = data["metadata"]
        required_metadata = WOMMDeploymentConfig.get_backup_required_metadata()
        for key in required_metadata:
            if key not in metadata:
                raise ValueError(f"Missing metadata key: {key}")

        # Validate entries structure
        entries = data["entries"]
        if not isinstance(entries, dict):
            raise ValueError("Entries must be a dictionary")

        # Check for expected context types
        expected_types = ContextTypesConfig.ALL_TYPES
        for context_type in expected_types:
            if context_type not in entries:
                raise ValueError(f"Missing context type: {context_type}")

        # Validate individual entries
        for context_type, context_entries in entries.items():
            if not isinstance(context_entries, list):
                raise ValueError(f"Context entries must be a list: {context_type}")

            for entry in context_entries:
                if not isinstance(entry, dict):
                    raise ValueError(f"Entry must be a dictionary in {context_type}")

                # Check required entry fields
                required_entry_fields = ["key_name", "display_name"]
                for field in required_entry_fields:
                    if field not in entry:
                        raise ValueError(f"Missing entry field: {field}")

    def cleanup_old_backups(
        self, max_files: int | None = None, retention_days: int | None = None
    ) -> BackupCleanupResult:
        """
        Clean up old backup files.

        Files that cannot be deleted are logged and counted as kept.

        Args:
            max_files: Maximum number of backup files to keep
            retention_days: Number of days to keep backups

        Returns:
            BackupCleanupResult: deleted and kept files; failure carries the error.
        """
        if max_files is not None and (not isinstance(max_files, int) or max_files < 0):
            return BackupCleanupResult(
                success=False,
                error=f"max_files must be a positive integer, got {max_files}",
            )

        if retention_days is not None and (
            not isinstance(retention_days, int) or retention_days < 0
        ):
            return BackupCleanupResult(
                success=False,
                error=(
                    f"retention_days must be a positive integer, got {retention_days}"
                ),
            )

        if max_files is None:
            max_files = self.MAX_BACKUP_FILES
        if retention_days is None:
            retention_days = self.BACKUP_RETENTION_DAYS

        listing = self.list_backup_files(include_metadata=False)
        if not listing.success:
            return BackupCleanupResult(success=False, error=listing.error)

        deleted_files: list[str] = []
        kept_files: list[str] = []

        # Sort by modification time (oldest first)
        backups = sorted(
            listing.backups or [], key=lambda b: b.modified_time or datetime.min
        )
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        for info in backups:
            expired = (
                info.modified_time is not None and info.modified_time < cutoff_date
            )
            over_limit = len(kept_files) >= max_files

            if not (expired or over_limit):
                kept_files.append(info.filename)
                continue

            try:
                Path(info.filepath).unlink()
                deleted_files.append(info.filename)
            except OSError as e:
                self.logger.warning(
                    f"Could not delete backup file {info.filename}: {e}"
                )
                kept_files.append(info.filename)

        return BackupCleanupResult(
            success=True,
            message=f"Deleted {len(deleted_files)} backup(s), kept {len(kept_files)}",
            deleted_files=deleted_files,
            kept_files=kept_files,
        )

    def get_backup_info(self, filepath: str) -> BackupDataResult:
        """
        Get detailed information about a backup file.

        Args:
            filepath: Path to the backup file

        Returns:
            BackupDataResult: metadata plus per-context entry statistics;
            failure carries the error.
        """
        loaded = self.load_backup_file(filepath)
        if not loaded.success:
            return loaded

        data = loaded.data or {}
        entries = data.get("entries", {})

        # Calculate additional statistics
        entry_stats = {
            context_type: {
                "count": len(context_entries),
                "sample_keys": [
                    entry.get("key_name", "unknown") for entry in context_entries[:5]
                ],
            }
            for context_type, context_entries in entries.items()
        }

        loaded.entry_stats = entry_stats
        return loaded

    def create_backup_copy(
        self, source_filepath: str, destination_filepath: str
    ) -> BackupFileResult:
        """
        Create a copy of a backup file.

        Args:
            source_filepath: Source backup file path
            destination_filepath: Destination backup file path

        Returns:
            BackupFileResult: the destination path; failure carries the error.
        """
        if not source_filepath:
            return BackupFileResult(
                success=False, error="Source filepath cannot be None or empty"
            )

        if not destination_filepath:
            return BackupFileResult(
                success=False, error="Destination filepath cannot be None or empty"
            )

        source_path = Path(source_filepath)
        destination_path = Path(destination_filepath)

        if not source_path.exists():
            return BackupFileResult(
                success=False, error=f"Source file not found: {source_filepath}"
            )

        try:
            # Create destination directory if needed
            destination_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, destination_path)
        except OSError as e:
            return BackupFileResult(
                success=False,
                filepath=str(destination_path),
                error=f"Failed to copy backup file: {e}",
            )

        return BackupFileResult(
            success=True,
            message=f"Copied backup to {destination_path}",
            filepath=str(destination_path),
        )

    def merge_backups(
        self, backup_filepaths: list[str], output_filepath: str
    ) -> BackupFileResult:
        """
        Merge multiple backup files into a single backup.

        Args:
            backup_filepaths: List of backup file paths to merge
            output_filepath: Output backup file path

        Returns:
            BackupFileResult: the written merge; failure carries the error.
        """
        if not backup_filepaths:
            return BackupFileResult(
                success=False, error="Backup filepaths list cannot be empty"
            )

        if not output_filepath:
            return BackupFileResult(
                success=False, error="Output filepath cannot be None or empty"
            )

        merged_entries: dict[str, list] = {
            ctx_type: [] for ctx_type in ContextTypesConfig.ALL_TYPES
        }
        merged_from: list[str] = []

        # Load and merge each backup
        for filepath in backup_filepaths:
            loaded = self.load_backup_file(filepath)
            if not loaded.success:
                return BackupFileResult(
                    success=False,
                    error=f"Could not merge {filepath}: {loaded.error}",
                )

            data = loaded.data or {}

            # Add to merged entries (avoid duplicates by key_name)
            existing_keys = {
                entry.get("key_name")
                for context_type in ["directory", "background"]
                for entry in merged_entries[context_type]
            }

            for context_type in ["directory", "background"]:
                for entry in data.get("entries", {}).get(context_type, []):
                    key_name = entry.get("key_name")
                    if key_name and key_name not in existing_keys:
                        merged_entries[context_type].append(entry)
                        existing_keys.add(key_name)

            merged_from.append(filepath)

        # Save merged backup — create_backup_file rebuilds the metadata block
        written = self.create_backup_file(
            merged_entries, output_filepath, add_timestamp=False
        )
        if not written.success:
            return written

        written.message = f"Merged {len(merged_from)} backup(s) into {written.filepath}"
        return written
