#!/usr/bin/env python3
"""
Backup manager for context menu operations.

This module provides comprehensive backup management functionality
for Windows context menu entries, including creation, validation,
listing, and cleanup of backup files.
"""

import json
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from ...exceptions.context import (
    ContextUtilityError,
    MenuInterfaceError,
    ValidationInterfaceError,
)
from ...shared.configs.context import ContextTypesConfig
from ...shared.configs.womm_setup import WOMMDeploymentConfig
from ..womm_setup.installer_interface import get_default_womm_path

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
        self.backup_dir = self._get_backup_directory()

    def _get_backup_directory(self) -> Path:
        """Get the backup directory path."""
        try:
            womm_path = get_default_womm_path()
            if womm_path.exists():
                backup_dir = womm_path / ".backup" / "context_menu"
                backup_dir.mkdir(parents=True, exist_ok=True)
                return backup_dir
        except Exception as e:
            self.logger.warning(f"Could not access WOMM backup directory: {e}")
            # Fallback to current directory
            return Path(".")

        return Path(".")

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def create_backup_file(
        self,
        entries: dict,
        custom_filename: str | None = None,
        add_timestamp: bool = True,
    ) -> tuple[bool, str, dict]:
        """
        Create a backup file with context menu entries.

        Args:
            entries: Dictionary containing context menu entries
            custom_filename: Optional custom filename (without extension)
            add_timestamp: Whether to add timestamp to filename

        Returns:
            Tuple of (success, filepath, metadata)

        Raises:
            ValidationError: If entries is None or empty
            ContextMenuError: If backup creation fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if entries is None:
                raise ValidationInterfaceError(
                    "backup_entries", "entries", "Entries dictionary cannot be None"
                )

            if not isinstance(entries, dict):
                raise ValidationInterfaceError(
                    "backup_entries",
                    "entries",
                    f"Entries must be a dictionary, got {type(entries).__name__}",
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
            except (PermissionError, OSError) as e:
                raise MenuInterfaceError(
                    "create", str(filepath), f"Failed to write backup file: {e}"
                ) from e
            except (TypeError, ValueError) as e:
                raise MenuInterfaceError(
                    "create", str(filepath), f"Failed to serialize backup data: {e}"
                ) from e

            return True, str(filepath), backup_data["metadata"]

        except (ValidationInterfaceError, MenuInterfaceError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error during backup creation: {e}",
                details=f"Entries keys: {list(entries.keys()) if entries else 'None'}",
            ) from e

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

        Raises:
            ContextUtilityError: For unexpected errors
        """
        try:
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
        except Exception as e:
            raise ContextUtilityError(
                f"Failed to create backup data structure: {e}",
                details=f"Entries structure: {type(entries)}",
            ) from e

    def list_backup_files(self, include_metadata: bool = True) -> list[dict]:
        """
        List all available backup files with optional metadata.

        Args:
            include_metadata: Whether to include backup metadata

        Returns:
            List of backup file information dictionaries

        Raises:
            ContextMenuError: If backup directory access fails
            ContextUtilityError: For unexpected errors
        """
        backup_files = []

        try:
            # Find all backup files
            pattern = "context_menu_backup_*.json"
            try:
                files = sorted(
                    self.backup_dir.glob(pattern),
                    key=lambda x: x.stat().st_mtime,
                    reverse=True,
                )
            except (PermissionError, OSError) as e:
                raise MenuInterfaceError(
                    "list",
                    str(self.backup_dir),
                    f"Failed to access backup directory: {e}",
                ) from e

            for file in files:
                try:
                    file_info = {
                        "filename": file.name,
                        "filepath": str(file),
                        "size_bytes": file.stat().st_size,
                        "modified_time": datetime.fromtimestamp(file.stat().st_mtime),
                        "size_kb": file.stat().st_size / 1024,
                    }

                    if include_metadata:
                        try:
                            with open(file, encoding="utf-8") as f:
                                data = json.load(f)

                            metadata = data.get("metadata", {})
                            file_info.update(
                                {
                                    "entry_count": metadata.get("total_entries", 0),
                                    "backup_version": metadata.get(
                                        "version", "unknown"
                                    ),
                                    "backup_timestamp": metadata.get(
                                        "timestamp", "unknown"
                                    ),
                                    "context_types": metadata.get("context_types", []),
                                }
                            )
                        except (json.JSONDecodeError, PermissionError, OSError) as e:
                            self.logger.warning(
                                f"Failed to read metadata from {file.name}: {e}"
                            )
                            file_info.update(
                                {
                                    "entry_count": 0,
                                    "backup_version": "unknown",
                                    "backup_timestamp": "unknown",
                                    "context_types": [],
                                }
                            )

                    backup_files.append(file_info)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to process backup file {file.name}: {e}"
                    )

        except MenuInterfaceError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error listing backup files: {e}",
                details=f"Backup directory: {self.backup_dir}",
            ) from e

        return backup_files

    def load_backup_file(self, filepath: str) -> tuple[bool, dict, str]:
        """
        Load and validate a backup file.

        Args:
            filepath: Path to the backup file

        Returns:
            Tuple of (success, data, error_message)

        Raises:
            ValidationError: If filepath is None or empty
            ContextMenuError: If backup loading fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not filepath:
                raise ValidationInterfaceError(
                    "backup_filepath", "filepath", "Filepath cannot be None or empty"
                )

            backup_path = Path(filepath)
            if not backup_path.exists():
                raise MenuInterfaceError("load", filepath, "Backup file not found")

            try:
                with open(backup_path, encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                raise MenuInterfaceError(
                    "load", filepath, f"Invalid JSON format: {e}"
                ) from e
            except (PermissionError, OSError) as e:
                raise MenuInterfaceError(
                    "load", filepath, f"Failed to read backup file: {e}"
                ) from e

            # Validate backup format
            self._validate_backup_data(data)

            return True, data, ""

        except (ValidationInterfaceError, MenuInterfaceError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error loading backup file: {e}",
                details=f"Filepath: {filepath}",
            ) from e

    def _validate_backup_data(self, data: dict) -> None:
        """
        Validate backup data structure.

        Args:
            data: Backup data to validate

        Raises:
            ValidationError: If data is None or invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if data is None:
                raise ValidationInterfaceError(
                    "backup_data", "data", "Backup data cannot be None"
                )

            if not isinstance(data, dict):
                raise ValidationInterfaceError(
                    "backup_data",
                    "data",
                    f"Backup data must be a dictionary, got {type(data).__name__}",
                )

            # Check required top-level keys
            required_keys = WOMMDeploymentConfig.get_backup_required_keys()
            for key in required_keys:
                if key not in data:
                    raise ValidationInterfaceError(
                        "backup_data", "data", f"Missing required key: {key}"
                    )

            # Validate metadata
            metadata = data["metadata"]
            required_metadata = WOMMDeploymentConfig.get_backup_required_metadata()
            for key in required_metadata:
                if key not in metadata:
                    raise ValidationInterfaceError(
                        "backup_data", "data", f"Missing metadata key: {key}"
                    )

            # Validate entries structure
            entries = data["entries"]
            if not isinstance(entries, dict):
                raise ValidationInterfaceError(
                    "backup_data", "data", "Entries must be a dictionary"
                )

            # Check for expected context types
            expected_types = ContextTypesConfig.ALL_TYPES
            for context_type in expected_types:
                if context_type not in entries:
                    raise ValidationInterfaceError(
                        "backup_data", "data", f"Missing context type: {context_type}"
                    )

            # Validate individual entries
            for context_type, context_entries in entries.items():
                if not isinstance(context_entries, list):
                    raise ValidationInterfaceError(
                        "backup_data",
                        "data",
                        f"Context entries must be a list: {context_type}",
                    )

                for entry in context_entries:
                    if not isinstance(entry, dict):
                        raise ValidationInterfaceError(
                            "backup_data",
                            "data",
                            f"Entry must be a dictionary in {context_type}",
                        )

                    # Check required entry fields
                    required_entry_fields = ["key_name", "display_name"]
                    for field in required_entry_fields:
                        if field not in entry:
                            raise ValidationInterfaceError(
                                "backup_data", "data", f"Missing entry field: {field}"
                            )

        except ValidationInterfaceError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error during backup validation: {e}",
                details=f"Data type: {type(data)}",
            ) from e

    def cleanup_old_backups(
        self, max_files: int | None = None, retention_days: int | None = None
    ) -> dict:
        """
        Clean up old backup files.

        Args:
            max_files: Maximum number of backup files to keep
            retention_days: Number of days to keep backups

        Returns:
            Cleanup result dictionary

        Raises:
            ValidationError: If parameters are invalid
            ContextMenuError: If cleanup operations fail
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if max_files is not None and (
                not isinstance(max_files, int) or max_files < 0
            ):
                raise ValidationInterfaceError(
                    "cleanup_parameters",
                    "max_files",
                    f"max_files must be a positive integer, got {max_files}",
                )

            if retention_days is not None and (
                not isinstance(retention_days, int) or retention_days < 0
            ):
                raise ValidationInterfaceError(
                    "cleanup_parameters",
                    "retention_days",
                    f"retention_days must be a positive integer, got {retention_days}",
                )

            if max_files is None:
                max_files = self.MAX_BACKUP_FILES
            if retention_days is None:
                retention_days = self.BACKUP_RETENTION_DAYS

            backup_files = self.list_backup_files(include_metadata=False)
            deleted_files = []
            kept_files = []

            # Sort by modification time (oldest first)
            backup_files.sort(key=lambda x: x["modified_time"])

            cutoff_date = datetime.now() - timedelta(days=retention_days)

            for file_info in backup_files:
                file_path = Path(file_info["filepath"])
                should_delete = False

                # Check retention period
                if file_info["modified_time"] < cutoff_date:
                    should_delete = True

                # Check max files limit
                if len(kept_files) >= max_files:
                    should_delete = True

                if should_delete:
                    try:
                        file_path.unlink()
                        deleted_files.append(file_info["filename"])
                    except (PermissionError, OSError) as e:
                        self.logger.warning(
                            f"Could not delete backup file {file_info['filename']}: {e}"
                        )
                else:
                    kept_files.append(file_info["filename"])

            return {
                "success": True,
                "deleted_files": deleted_files,
                "kept_files": kept_files,
                "deleted_count": len(deleted_files),
                "kept_count": len(kept_files),
            }

        except (ValidationInterfaceError, MenuInterfaceError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error during backup cleanup: {e}",
                details=f"max_files: {max_files}, retention_days: {retention_days}",
            ) from e

    def get_backup_info(self, filepath: str) -> dict:
        """
        Get detailed information about a backup file.

        Args:
            filepath: Path to the backup file

        Returns:
            Backup information dictionary

        Raises:
            ValidationError: If filepath is None or empty
            ContextMenuError: If backup info retrieval fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not filepath:
                raise ValidationInterfaceError(
                    "backup_filepath", "filepath", "Filepath cannot be None or empty"
                )

            success, data, error = self.load_backup_file(filepath)
            if not success:
                return {"error": error}

            metadata = data.get("metadata", {})
            entries = data.get("entries", {})

            # Calculate additional statistics
            entry_stats = {}
            for context_type, context_entries in entries.items():
                entry_stats[context_type] = {
                    "count": len(context_entries),
                    "sample_keys": [
                        entry.get("key_name", "unknown")
                        for entry in context_entries[:5]
                    ],
                }

            return {
                "success": True,
                "filepath": filepath,
                "metadata": metadata,
                "entry_stats": entry_stats,
                "total_entries": metadata.get("total_entries", 0),
                "backup_version": metadata.get("version", "unknown"),
                "created": metadata.get("timestamp", "unknown"),
                "platform": metadata.get("platform", "unknown"),
            }

        except (ValidationInterfaceError, MenuInterfaceError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting backup info: {e}",
                details=f"Filepath: {filepath}",
            ) from e

    def create_backup_copy(
        self, source_filepath: str, destination_filepath: str
    ) -> tuple[bool, str]:
        """
        Create a copy of a backup file.

        Args:
            source_filepath: Source backup file path
            destination_filepath: Destination backup file path

        Returns:
            Tuple of (success, error_message)

        Raises:
            ValidationError: If filepaths are None or empty
            ContextMenuError: If backup copy operation fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not source_filepath:
                raise ValidationInterfaceError(
                    "backup_filepath",
                    "source_filepath",
                    "Source filepath cannot be None or empty",
                )

            if not destination_filepath:
                raise ValidationInterfaceError(
                    "backup_filepath",
                    "destination_filepath",
                    "Destination filepath cannot be None or empty",
                )

            source_path = Path(source_filepath)
            destination_path = Path(destination_filepath)

            if not source_path.exists():
                raise MenuInterfaceError(
                    "copy", source_filepath, "Source file not found"
                )

            # Create destination directory if needed
            try:
                destination_path.parent.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                raise MenuInterfaceError(
                    "copy",
                    str(destination_path.parent),
                    f"Failed to create destination directory: {e}",
                ) from e

            # Copy the file
            try:
                shutil.copy2(source_path, destination_path)
            except (PermissionError, OSError) as e:
                raise MenuInterfaceError(
                    "copy",
                    f"{source_filepath} -> {destination_filepath}",
                    f"Failed to copy backup file: {e}",
                ) from e

            return True, ""

        except (ValidationInterfaceError, MenuInterfaceError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error copying backup file: {e}",
                details=f"Source: {source_filepath}, Destination: {destination_filepath}",
            ) from e

    def merge_backups(
        self, backup_filepaths: list[str], output_filepath: str
    ) -> tuple[bool, str, dict]:
        """
        Merge multiple backup files into a single backup.

        Args:
            backup_filepaths: List of backup file paths to merge
            output_filepath: Output backup file path

        Returns:
            Tuple of (success, error_message, merged_data)

        Raises:
            ValidationError: If parameters are invalid
            ContextMenuError: If merge operation fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not backup_filepaths:
                raise ValidationInterfaceError(
                    "merge_parameters",
                    "backup_filepaths",
                    "Backup filepaths list cannot be empty",
                )

            if not output_filepath:
                raise ValidationInterfaceError(
                    "merge_parameters",
                    "output_filepath",
                    "Output filepath cannot be None or empty",
                )

            merged_entries = {ctx_type: [] for ctx_type in ContextTypesConfig.ALL_TYPES}
            merged_from: list[str] = []
            merged_metadata = {
                "version": self.BACKUP_VERSION,
                "timestamp": datetime.now().isoformat(),
                "platform": "Windows",
                "merged_from": merged_from,
                "total_entries": 0,
            }

            # Load and merge each backup
            for filepath in backup_filepaths:
                success, data, error = self.load_backup_file(filepath)
                if not success:
                    raise MenuInterfaceError(
                        "merge", filepath, f"Error loading backup: {error}"
                    )

                # Add to merged entries (avoid duplicates by key_name)
                existing_keys = set()
                for context_type in ["directory", "background"]:
                    existing_keys.update(
                        entry.get("key_name") for entry in merged_entries[context_type]
                    )

                for context_type in ["directory", "background"]:
                    for entry in data.get("entries", {}).get(context_type, []):
                        key_name = entry.get("key_name")
                        if key_name and key_name not in existing_keys:
                            merged_entries[context_type].append(entry)
                            existing_keys.add(key_name)

                # Update metadata
                merged_from.append(filepath)

            # Calculate total entries
            total_entries = sum(
                len(merged_entries[context_type])
                for context_type in ["directory", "background"]
            )
            merged_metadata["total_entries"] = total_entries

            # Create merged backup data
            merged_data = {"metadata": merged_metadata, "entries": merged_entries}

            # Save merged backup
            success, filepath, _ = self.create_backup_file(
                merged_entries, output_filepath, add_timestamp=False
            )
            if not success:
                raise MenuInterfaceError(
                    "merge", output_filepath, f"Error saving merged backup: {filepath}"
                )

            return True, "", merged_data

        except (ValidationInterfaceError, MenuInterfaceError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error merging backups: {e}",
                details=f"Input files: {len(backup_filepaths)}, Output: {output_filepath}",
            ) from e
