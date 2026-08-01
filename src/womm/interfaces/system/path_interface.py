#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM PATH INTERFACE - User PATH Manager Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System PATH Interface for Works On My Machine.

Orchestrates SystemPathService and translates its exceptions into a Result.
This interface carries no UI: it does not print, log, or drive interactive
menus — the command layer owns presentation and user interaction. It never
re-raises; service exceptions are converted into the relevant Result.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import logging
import os
import platform
import shutil
from datetime import datetime
from pathlib import Path

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.system import SystemServiceError
from ...services import CommandRunnerService, SystemPathService
from ...shared.paths import path_backups_dir
from ...shared.results import (
    PathBackupContentResult,
    PathBackupInfo,
    PathBackupListResult,
    PathBackupResult,
    PathOperationResult,
)

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class SystemPathInterface:
    """Orchestrates SystemPathService and returns a Result.

    Pure orchestration: no UI, no re-raise. Service exceptions
    (``SystemServiceError``, ``ValidationServiceError``) are translated
    into the relevant Result. Unexpected errors are not swallowed — they
    propagate.
    """

    def __init__(self) -> None:
        """Initialize PATH backup and modification services."""
        self._path_service = SystemPathService()
        self._command_runner = CommandRunnerService()
        self.backup_dir = path_backups_dir()
        self.latest_backup = self.backup_dir / ".path.json"
        self.platform = platform.system()

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS - PATH MODIFICATION
    # ///////////////////////////////////////////////////////////////

    def add_to_path(self, entry: Path) -> PathOperationResult:
        """
        Add an explicit entry to PATH environment variable.

        Returns:
            PathOperationResult: success/failure; failure carries the error.
        """
        entry_path = str(entry.expanduser().resolve())

        try:
            current_path_result = self._path_service.get_current_system_path()
        except (SystemServiceError, ValidationServiceError) as e:
            return PathOperationResult(
                success=False,
                message="Failed to get current PATH",
                error=str(e),
                entry_path=entry_path,
                operation="add",
            )

        if not current_path_result.success:
            return PathOperationResult(
                success=False,
                message=current_path_result.message or "Failed to get current PATH",
                error=current_path_result.error or "",
                entry_path=entry_path,
                operation="add",
            )

        sep = os.pathsep or (";" if self.platform == "Windows" else ":")
        original_path = sep.join(current_path_result.path_entries or [])

        try:
            if self.platform == "Windows":
                return self._path_service.setup_windows_path(entry_path, original_path)
            return self._path_service.setup_unix_path(entry_path, original_path)
        except (SystemServiceError, ValidationServiceError) as e:
            return PathOperationResult(
                success=False,
                message="Failed to add entry to PATH",
                error=str(e),
                entry_path=entry_path,
                operation="add",
            )

    def remove_from_path(self, entry: Path) -> PathOperationResult:
        """
        Remove an explicit entry from PATH environment variable.

        Returns:
            PathOperationResult: success/failure; failure carries the error.
        """
        entry_path = str(entry.expanduser().resolve())

        try:
            if self.platform == "Windows":
                return self._path_service.remove_from_windows_path(entry_path)
            return self._path_service.remove_from_unix_path(entry_path)
        except (SystemServiceError, ValidationServiceError) as e:
            return PathOperationResult(
                success=False,
                message="Failed to remove entry from PATH",
                error=str(e),
                entry_path=entry_path,
                operation="remove",
            )

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS - PATH INSPECTION
    # ///////////////////////////////////////////////////////////////

    def list_path_entries(self) -> PathOperationResult:
        """
        List the entries of the current user PATH.

        Returns:
            PathOperationResult: ``path_entries`` holds the current PATH on
            success; failure carries the error.
        """
        try:
            return self._path_service.get_current_system_path()
        except (SystemServiceError, ValidationServiceError) as e:
            return PathOperationResult(
                success=False,
                message="Failed to read the current PATH",
                error=str(e),
                operation="list",
            )

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS - BACKUP MANAGEMENT
    # ///////////////////////////////////////////////////////////////

    def list_backups(self) -> PathBackupListResult:
        """
        List available PATH backup files.

        Returns:
            PathBackupListResult: backups found (possibly empty); failure only
            when the backup directory cannot be scanned.
        """
        if not self.backup_dir.exists():
            return PathBackupListResult(
                success=True,
                message="No backup directory found",
                backup_location=str(self.backup_dir),
                backups=[],
            )

        try:
            backup_files = sorted(
                self.backup_dir.glob(".path_*.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
        except OSError as e:
            return PathBackupListResult(
                success=False,
                message="Failed to scan backup directory",
                error=str(e),
                backup_location=str(self.backup_dir),
            )

        backups: list[PathBackupInfo] = []
        for backup_file in backup_files:
            try:
                stat = backup_file.stat()
                data = json.loads(backup_file.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.warning(f"Skipping unreadable backup {backup_file.name}: {e}")
                continue

            backups.append(
                PathBackupInfo(
                    name=backup_file.name,
                    path=str(backup_file),
                    size=stat.st_size,
                    modified=datetime.fromtimestamp(stat.st_mtime).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    path_entries=len(data.get("entries", [])),
                )
            )

        return PathBackupListResult(
            success=True,
            message=f"Found {len(backups)} backup(s)",
            backup_location=str(self.backup_dir),
            backups=backups,
        )

    def _resolve_backup_name(self, name: str) -> Path | None:
        """Resolve a backup name inside the backup directory.

        Args:
            name: Bare file name, as listed by ``list_backups()``.

        Returns:
            The resolved path, or None when the name is unsafe, absent, or
            not a regular file. Callers must not disclose the resolved path.
        """
        if not name or ".." in name or "/" in name or "\\" in name:
            return None
        if Path(name).is_absolute() or Path(name).drive:
            return None

        try:
            candidate = (self.backup_dir / name).resolve()
            root = self.backup_dir.resolve()
        except OSError:
            return None

        if not candidate.is_relative_to(root):
            return None
        if not candidate.is_file():
            return None
        # resolve() followed the symlink; is_relative_to already rejected any
        # target outside root, so reaching here means the file is contained.
        return candidate

    def read_backup(self, name: str) -> PathBackupContentResult:
        """
        Read the content of a single PATH backup file.

        Args:
            name: Bare backup file name, as listed by ``list_backups()``.
                Path separators, parent references and absolute paths are
                rejected.

        Returns:
            PathBackupContentResult: the backup's metadata and entries, or a
            failure carrying the reason.
        """
        backup_file = self._resolve_backup_name(name)
        if backup_file is None:
            return PathBackupContentResult(
                success=False,
                message=f"No readable backup named {name!r}",
                name=name,
            )

        try:
            data = json.loads(backup_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
            return PathBackupContentResult(
                success=False,
                message=f"Failed to read backup file: {name}",
                error=str(e),
                name=name,
            )

        if not isinstance(data, dict):
            return PathBackupContentResult(
                success=False,
                message=f"Malformed backup file: {name}",
                error="Backup payload is not an object",
                name=name,
            )

        entries = data.get("entries", [])
        if not isinstance(entries, list):
            entries = []

        return PathBackupContentResult(
            success=True,
            message=f"Read {len(entries)} entries from {name}",
            name=name,
            backup_file=str(backup_file),
            timestamp=str(data.get("timestamp", "")),
            platform=str(data.get("platform", "")),
            separator=str(data.get("separator", "")),
            length=int(data.get("length", 0) or 0),
            entries=[str(entry) for entry in entries],
        )

    def create_backup(self) -> PathBackupResult:
        """
        Create a new PATH backup (JSON file with timestamp).

        Returns:
            PathBackupResult: success/failure; failure carries the error.
        """
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            return PathBackupResult(
                success=False,
                message="Failed to create backup directory",
                error=str(e),
                backup_location=str(self.backup_dir),
            )

        try:
            path_result = self._path_service.get_current_system_path()
        except (SystemServiceError, ValidationServiceError) as e:
            return PathBackupResult(
                success=False,
                message="Failed to get current PATH",
                error=str(e),
                backup_location=str(self.backup_dir),
            )

        if not path_result.success:
            return PathBackupResult(
                success=False,
                message=path_result.message or "Failed to get current PATH",
                error=path_result.error or "",
                backup_location=str(self.backup_dir),
            )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_json = self.backup_dir / f".path_{timestamp}.json"
        sep = os.pathsep or (";" if self.platform == "Windows" else ":")
        entries = path_result.path_entries or []
        current_path = sep.join(entries)
        payload = {
            "type": "womm_path_backup",
            "version": 1,
            "timestamp": timestamp,
            "platform": self.platform,
            "separator": sep,
            "path_string": current_path,
            "entries": entries,
            "length": len(current_path),
        }

        try:
            with open(backup_json, "w", encoding="utf-8") as jf:
                json.dump(payload, jf, indent=2, ensure_ascii=False)
        except (OSError, TypeError, ValueError) as e:
            return PathBackupResult(
                success=False,
                message="Failed to write backup file",
                error=str(e),
                backup_location=str(self.backup_dir),
            )

        try:
            if self.latest_backup.exists():
                self.latest_backup.unlink()
            shutil.copy2(backup_json, self.latest_backup)
        except OSError as e:
            logger.warning(f"Failed to update latest backup reference: {e}")

        return PathBackupResult(
            success=True,
            message=f"PATH backup created: {backup_json.name}",
            backup_location=str(self.backup_dir),
            backup_file=str(backup_json),
            entries_count=len(entries),
        )

    def restore_backup(self, backup_file: Path) -> PathOperationResult:
        """
        Restore PATH from a specific backup file.

        Args:
            backup_file: Backup JSON file to restore from (as returned by
                ``list_backups()``).

        Returns:
            PathOperationResult: success/failure; failure carries the error.
        """
        try:
            data = json.loads(backup_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
            return PathOperationResult(
                success=False,
                message=f"Failed to read backup file: {backup_file.name}",
                error=str(e),
                entry_path=str(backup_file),
                operation="restore",
            )

        path_value = data.get("path_string", "")
        entries = data.get("entries", [])

        if self.platform == "Windows":
            try:
                result = self._command_runner.run_silent(
                    [
                        "reg",
                        "add",
                        "HKCU\\Environment",
                        "/v",
                        "PATH",
                        "/t",
                        "REG_EXPAND_SZ",
                        "/d",
                        path_value,
                        "/f",
                    ]
                )
            except Exception as e:
                return PathOperationResult(
                    success=False,
                    message="Failed to execute registry update",
                    error=str(e),
                    entry_path=str(backup_file),
                    operation="restore",
                )

            if result.returncode != 0:
                return PathOperationResult(
                    success=False,
                    message="Failed to restore Windows user PATH",
                    error=f"Return code: {result.returncode}",
                    entry_path=str(backup_file),
                    operation="restore",
                )
        else:
            os.environ["PATH"] = path_value

        return PathOperationResult(
            success=True,
            message=f"PATH restored successfully from {backup_file.name}",
            entry_path=str(backup_file),
            operation="restore",
            path_modified=True,
            path_entries=entries,
        )


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["SystemPathInterface"]
