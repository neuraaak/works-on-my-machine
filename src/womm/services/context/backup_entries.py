#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT BACKUP ENTRIES - Backup file reading and entry normalization
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Reading and normalization of context menu entries stored in backup files.

This module owns everything about *what* a backup file contains: locating the
files, tolerating the legacy list format, de-duplicating entries by key name,
and pulling a script path back out of a stored command. It never formats
anything for display and never touches the registry.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import logging
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

BACKUP_FILE_PATTERN = "context_menu_backup_*.json"
BACKUP_CONTEXT_TYPES = ("directory", "background", "file", "files", "root")

# ///////////////////////////////////////////////////////////////
# CLASSES
# ///////////////////////////////////////////////////////////////


class ContextBackupEntriesReader:
    """Reads context menu entries out of backup files."""

    def __init__(self, logger: logging.Logger | None = None):
        """
        Initialize the reader.

        Args:
            logger: Logger used for unreadable backup files
        """
        self.logger = logger or logging.getLogger(__name__)

    def collect_entries(self, backup_dir: Path) -> list[dict]:
        """
        Collect all unique context menu entries from a backup directory.

        Entries are tagged with their source file (``_source_backup``) and the
        context type they were stored under (``_context_type``). The first
        occurrence of a key name wins; unreadable files are skipped.

        Args:
            backup_dir: Directory holding the backup files

        Returns:
            List of unique entries with metadata
        """
        all_entries: dict[str, dict] = {}

        for backup_file in sorted(backup_dir.glob(BACKUP_FILE_PATTERN)):
            try:
                with open(backup_file, encoding="utf-8") as handle:
                    data = json.load(handle)
            except (OSError, ValueError) as e:
                self.logger.debug(f"Error reading {backup_file.name}: {e}")
                continue

            for context_type, entry in self._iter_entries(data):
                key_name = entry.get("key_name")
                if key_name and key_name not in all_entries:
                    entry["_source_backup"] = backup_file.name
                    entry["_context_type"] = context_type
                    all_entries[key_name] = entry

        return list(all_entries.values())

    @staticmethod
    def filter_available(all_entries: list[dict], current_keys: set[str]) -> list[dict]:
        """
        Filter out entries that are already installed.

        Args:
            all_entries: All entries from backups
            current_keys: Set of currently installed entry keys

        Returns:
            List of entries not yet installed
        """
        return [
            entry
            for entry in all_entries
            if entry.get("key_name") and entry.get("key_name") not in current_keys
        ]

    @staticmethod
    def extract_script_path(command: str) -> str | None:
        """
        Extract an existing script path from a stored command line.

        Args:
            command: Command line as stored in the backup

        Returns:
            The quoted path if it exists on disk, otherwise ``None``.
        """
        if '"' not in command:
            return None
        candidate = command.split('"')[1]
        if candidate and Path(candidate).exists():
            return candidate
        return None

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    @staticmethod
    def _iter_entries(data: object):
        """Yield ``(context_type, entry)`` pairs from backup file data."""
        if not isinstance(data, dict):
            return
        entries_dict = data.get("entries", {})
        if not isinstance(entries_dict, dict):
            # Legacy format: a bare list of directory entries
            entries_dict = {
                "directory": entries_dict if isinstance(entries_dict, list) else []
            }

        for context_type in BACKUP_CONTEXT_TYPES:
            entries = entries_dict.get(context_type, [])
            if not isinstance(entries, list):
                continue
            for entry in entries:
                if isinstance(entry, dict):
                    yield context_type, entry


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["ContextBackupEntriesReader"]
