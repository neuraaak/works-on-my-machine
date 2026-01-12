#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM PATH SERVICE - User PATH Utilities (Singleton)
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
SystemPathService - cross-platform PATH management helpers for WOMM.

Provides registry (Windows) and shell-file (Unix) operations to read,
add, or remove PATH entries. Stateless utilities live in
`womm/utils/system/system_path.py`.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import os
import platform
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.system import (
    FileSystemServiceError,
    RegistryServiceError,
    UserPathServiceError,
)
from ...shared.results.base import CommandResult
from ...shared.results.system_results import PathOperationResult
from ...utils.system import (
    deduplicate_path_entries,
    extract_path_from_reg_output,
)
from ..common.command_runner_service import CommandRunnerService

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)
_command_runner = CommandRunnerService()


# ///////////////////////////////////////////////////////////////
# PUBLIC SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class SystemPathService:
    """Cross-platform PATH management (singleton)."""

    _instance: ClassVar[SystemPathService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> SystemPathService:
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if SystemPathService._initialized:
            return
        SystemPathService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def get_current_system_path(self) -> PathOperationResult:
        """
        Get current system PATH value.

        Returns:
            PathOperationResult: Result with current PATH entries

        Raises:
            RegistryError: If registry query fails critically
            UserPathError: If PATH extraction fails critically
        """
        import time

        start_time = time.time()
        try:
            if platform.system() == "Windows":
                query = self._query_registry_path()
                try:
                    path_str = extract_path_from_reg_output(query.stdout)
                    path_entries = path_str.split(";") if path_str else []
                    return PathOperationResult(
                        success=True,
                        message="PATH retrieved successfully from registry",
                        entry_path="",
                        operation="get",
                        path_modified=False,
                        path_entries=[p.strip() for p in path_entries if p.strip()],
                        modification_time=time.time() - start_time,
                    )
                except Exception as e:
                    # Business logic error - return result
                    return PathOperationResult(
                        success=False,
                        message=f"Failed to extract PATH from registry output: {e}",
                        error=str(e),
                        entry_path="",
                        operation="get",
                        path_modified=False,
                        path_entries=[],
                        modification_time=time.time() - start_time,
                    )
            # Unix systems
            path_str = os.environ.get("PATH", "")
            path_entries = path_str.split(":") if path_str else []
            return PathOperationResult(
                success=True,
                message="PATH retrieved successfully from environment",
                entry_path="",
                operation="get",
                path_modified=False,
                path_entries=[p.strip() for p in path_entries if p.strip()],
                modification_time=time.time() - start_time,
            )

        except (RegistryServiceError, ValidationServiceError):
            # Re-raise programming errors and critical errors
            raise
        except Exception as e:
            # Wrap unexpected external exceptions - critical error
            raise UserPathServiceError(
                message=f"Failed to get current system PATH: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def setup_windows_path(
        self, entry_path: str, original_path: str
    ) -> PathOperationResult:
        """
        Setup WOMM in Windows PATH (user registry HKCU).

        Args:
            entry_path: Path entry to add
            original_path: Original PATH value

        Returns:
            PathOperationResult: Result of the PATH setup operation

        Raises:
            ValidationError: If entry_path is invalid (programming error)
            RegistryError: If registry operations fail critically
        """
        import time

        start_time = time.time()
        try:
            # Validation errors are programming errors - raise exception
            self._validate_entry(entry_path, "Windows PATH setup")
            if not original_path:
                raise ValidationServiceError(
                    message="Original path cannot be empty",
                    operation="setup_windows_path",
                    details="Empty original path provided for Windows PATH setup",
                )

            query = self._query_registry_path()
            current_path = extract_path_from_reg_output(self._ensure_str(query.stdout))

            current_entries = self._normalize_list(current_path)
            normalized_womm = str(Path(entry_path))

            # Business logic: path already present - return success result
            if normalized_womm in current_entries:
                return PathOperationResult(
                    success=True,
                    message=f"PATH entry already present: {normalized_womm}",
                    entry_path=normalized_womm,
                    operation="add",
                    path_modified=False,
                    path_entries=current_entries,
                    modification_time=time.time() - start_time,
                )

            # Add new entry
            updated_entries = [*current_entries, normalized_womm]
            updated_path = deduplicate_path_entries(";".join(updated_entries))

            self._write_registry_path(updated_path)

            return PathOperationResult(
                success=True,
                message=f"PATH entry added successfully: {normalized_womm}",
                entry_path=normalized_womm,
                operation="add",
                path_modified=True,
                path_entries=updated_entries,
                modification_time=time.time() - start_time,
            )

        except (ValidationServiceError, RegistryServiceError):
            # Re-raise programming errors and critical errors
            raise
        except Exception as e:
            # Wrap unexpected external exceptions - critical error
            raise UserPathServiceError(
                message=f"Unexpected error during Windows PATH setup: {e}",
                details=(
                    f"Exception type: {type(e).__name__}, "
                    f"Entry path: {entry_path}, Original PATH: {original_path}"
                ),
            ) from e

    def remove_from_windows_path(self, entry_path: str) -> PathOperationResult:
        """
        Remove WOMM from Windows PATH (user registry HKCU).

        Args:
            entry_path: Path entry to remove

        Returns:
            PathOperationResult: Result of the PATH removal operation

        Raises:
            ValidationError: If entry_path is invalid (programming error)
            RegistryError: If registry operations fail critically
        """
        import time

        start_time = time.time()
        try:
            # Validation errors are programming errors - raise exception
            self._validate_entry(entry_path, "Windows PATH removal")

            query = self._query_registry_path()
            current_path = extract_path_from_reg_output(self._ensure_str(query.stdout))

            def _norm(p: str) -> str:
                try:
                    return str(Path(p).resolve()) if p else ""
                except Exception as e:
                    logger.warning(f"Failed to resolve path '{p}': {e}")
                    return p

            path_entries = [p.strip() for p in current_path.split(";") if p.strip()]
            normalized_womm = _norm(entry_path)

            updated_entries: list[str] = []
            removed_paths: list[str] = []

            for entry in path_entries:
                normalized_entry = _norm(entry)
                if normalized_entry and normalized_entry != normalized_womm:
                    updated_entries.append(entry)
                elif normalized_entry == normalized_womm:
                    removed_paths.append(entry)

            # Business logic: path not found - return success result
            if not removed_paths:
                return PathOperationResult(
                    success=True,
                    message=f"PATH entry not found: {entry_path}",
                    entry_path=entry_path,
                    operation="remove",
                    path_modified=False,
                    path_entries=path_entries,
                    modification_time=time.time() - start_time,
                )

            # Remove entry
            updated_path = ";".join(updated_entries)
            self._write_registry_path(updated_path)

            return PathOperationResult(
                success=True,
                message=f"PATH entry removed successfully: {entry_path}",
                entry_path=entry_path,
                operation="remove",
                path_modified=True,
                path_entries=updated_entries,
                modification_time=time.time() - start_time,
            )

        except (ValidationServiceError, RegistryServiceError):
            # Re-raise programming errors and critical errors
            raise
        except Exception as e:
            # Wrap unexpected external exceptions - critical error
            raise UserPathServiceError(
                message=f"Unexpected error during Windows PATH removal: {e}",
                details=(
                    f"Exception type: {type(e).__name__}, Entry path: {entry_path}"
                ),
            ) from e

    def setup_unix_path(
        self, entry_path: str, original_path: str
    ) -> PathOperationResult:
        """
        Setup WOMM in Unix PATH via shell rc files.

        Args:
            entry_path: Path entry to add
            original_path: Original PATH value

        Returns:
            PathOperationResult: Result of the PATH setup operation

        Raises:
            ValidationError: If entry_path is invalid (programming error)
            FileSystemError: If file operations fail critically
        """
        import time

        start_time = time.time()
        try:
            # Validation errors are programming errors - raise exception
            self._validate_entry(entry_path, "Unix PATH setup")
            if not original_path:
                raise ValidationServiceError(
                    message="Original path cannot be empty",
                    operation="setup_unix_path",
                    details="Empty original path provided for Unix PATH setup",
                )

            shell_rc_files = [
                Path.home() / ".bashrc",
                Path.home() / ".zshrc",
                Path.home() / ".profile",
            ]

            target_rc = next((rc for rc in shell_rc_files if rc.exists()), None) or (
                Path.home() / ".bashrc"
            )

            womm_export_line = f'export PATH="{entry_path}:$PATH"'
            womm_path_comment = "# Added by Works On My Machine installer"

            # Business logic: path already present - return success result
            if target_rc.exists():
                with open(target_rc, encoding="utf-8") as f:
                    if entry_path in f.read():
                        return PathOperationResult(
                            success=True,
                            message=f"PATH entry already present in {target_rc}: {entry_path}",
                            entry_path=entry_path,
                            operation="add",
                            path_modified=False,
                            path_entries=[],
                            modification_time=time.time() - start_time,
                        )

            # Add new entry
            try:
                with open(target_rc, "a", encoding="utf-8") as f:
                    f.write(f"\n{womm_path_comment}\n{womm_export_line}\n")
            except (PermissionError, OSError) as e:
                # Critical file system error - raise exception
                raise FileSystemServiceError(
                    file_path=str(target_rc),
                    operation="write",
                    reason="Cannot write to shell configuration file",
                    details=f"Error: {e}",
                ) from e

            return PathOperationResult(
                success=True,
                message=f"PATH entry added successfully to {target_rc}: {entry_path}",
                entry_path=entry_path,
                operation="add",
                path_modified=True,
                path_entries=[entry_path],
                modification_time=time.time() - start_time,
            )

        except (ValidationServiceError, FileSystemServiceError):
            # Re-raise programming errors and critical errors
            raise
        except Exception as e:
            # Wrap unexpected external exceptions - critical error
            raise UserPathServiceError(
                message=f"Unexpected error during Unix PATH setup: {e}",
                details=(
                    f"Exception type: {type(e).__name__}, "
                    f"Entry path: {entry_path}, Original PATH: {original_path}"
                ),
            ) from e

    def remove_from_unix_path(self, entry_path: str) -> PathOperationResult:
        """
        Remove WOMM from Unix PATH via shell rc files.

        Args:
            entry_path: Path entry to remove

        Returns:
            PathOperationResult: Result of the PATH removal operation

        Raises:
            ValidationError: If entry_path is invalid (programming error)
            FileSystemError: If file operations fail critically
        """
        import time

        start_time = time.time()
        try:
            # Validation errors are programming errors - raise exception
            self._validate_entry(entry_path, "Unix PATH removal")

            shell_rc_files = [
                Path.home() / ".bashrc",
                Path.home() / ".zshrc",
                Path.home() / ".profile",
            ]

            removed_from_files: list[str] = []
            path_entries: list[str] = []

            for rc_file in shell_rc_files:
                if not rc_file.exists():
                    continue

                try:
                    with open(rc_file, encoding="utf-8") as f:
                        lines = f.readlines()
                except (PermissionError, OSError) as e:
                    # Critical file system error - raise exception
                    raise FileSystemServiceError(
                        file_path=str(rc_file),
                        operation="read",
                        reason="Cannot read shell configuration file",
                        details=f"Error: {e}",
                    ) from e

                updated_lines: list[str] = []
                removed_lines: list[str] = []
                skip_next = False

                for line in lines:
                    line_stripped = line.strip()

                    if "Added by Works On My Machine installer" in line:
                        removed_lines.append(line_stripped)
                        skip_next = True
                        continue

                    if skip_next and "export PATH=" in line and entry_path in line:
                        removed_lines.append(line_stripped)
                        skip_next = False
                        continue

                    if "export PATH=" in line and entry_path in line:
                        removed_lines.append(line_stripped)
                        continue

                    updated_lines.append(line)
                    skip_next = False

                if removed_lines:
                    try:
                        with open(rc_file, "w", encoding="utf-8") as f:
                            f.writelines(updated_lines)
                    except (PermissionError, OSError) as e:
                        # Critical file system error - raise exception
                        raise FileSystemServiceError(
                            file_path=str(rc_file),
                            operation="write",
                            reason="Cannot write to shell configuration file",
                            details=f"Error: {e}",
                        ) from e

                    removed_from_files.append(str(rc_file))

            # Business logic: path not found - return success result
            if not removed_from_files:
                return PathOperationResult(
                    success=True,
                    message=f"PATH entry not found in any shell config file: {entry_path}",
                    entry_path=entry_path,
                    operation="remove",
                    path_modified=False,
                    path_entries=path_entries,
                    modification_time=time.time() - start_time,
                )

            # Entry removed
            return PathOperationResult(
                success=True,
                message=f"PATH entry removed successfully from {len(removed_from_files)} file(s): {entry_path}",
                entry_path=entry_path,
                operation="remove",
                path_modified=True,
                path_entries=path_entries,
                modification_time=time.time() - start_time,
            )

        except (ValidationServiceError, FileSystemServiceError):
            # Re-raise programming errors and critical errors
            raise
        except Exception as e:
            # Wrap unexpected external exceptions - critical error
            raise UserPathServiceError(
                message=f"Unexpected error during Unix PATH removal: {e}",
                details=(
                    f"Exception type: {type(e).__name__}, Entry path: {entry_path}"
                ),
            ) from e

    def remove_from_path(self, entry_path: str) -> PathOperationResult:
        """
        Remove WOMM from PATH (cross-platform).

        Args:
            entry_path: Path entry to remove

        Returns:
            PathOperationResult: Result of the PATH removal operation

        Raises:
            ValidationError: If entry_path is invalid (programming error)
            RegistryError: If registry operations fail critically (Windows)
            FileSystemError: If file operations fail critically (Unix)
        """
        try:
            # Validation errors are programming errors - raise exception
            self._validate_entry(entry_path, "PATH removal")

            if platform.system() == "Windows":
                return self.remove_from_windows_path(entry_path)

            return self.remove_from_unix_path(entry_path)

        except (
            ValidationServiceError,
            RegistryServiceError,
            FileSystemServiceError,
        ):
            # Re-raise programming errors and critical errors
            raise
        except Exception as e:
            # Wrap unexpected external exceptions - critical error
            raise UserPathServiceError(
                message=f"Unexpected error during PATH removal: {e}",
                details=(
                    f"Exception type: {type(e).__name__}, Entry path: {entry_path}, "
                    f"Platform: {platform.system()}"
                ),
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _query_registry_path(self) -> CommandResult:
        """Query Windows registry for PATH value.

        Returns:
            CommandResult: Result of registry query command

        Raises:
            RegistryError: If registry query fails
        """
        try:
            result = _command_runner.run_silent(
                ["reg", "query", "HKCU\\Environment", "/v", "PATH"],
                capture_output=True,
            )
        except Exception as e:
            raise RegistryServiceError(
                registry_key="HKCU\\Environment",
                operation="query",
                reason=f"Failed to execute registry query: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

        if result.returncode != 0:
            raise RegistryServiceError(
                registry_key="HKCU\\Environment",
                operation="query",
                reason="Failed to query Windows user PATH from registry",
                details=f"Return code: {result.returncode}",
            )

        return result

    def _write_registry_path(self, updated_path: str) -> None:
        """Write PATH value to Windows registry."""
        reg_result = _command_runner.run_silent(
            [
                "reg",
                "add",
                "HKCU\\Environment",
                "/v",
                "PATH",
                "/t",
                "REG_EXPAND_SZ",
                "/d",
                updated_path,
                "/f",
            ],
            capture_output=True,
        )

        if reg_result.returncode != 0:
            stderr_str = self._ensure_str(reg_result.stderr)
            raise RegistryServiceError(
                registry_key="HKCU\\Environment",
                operation="update",
                reason="Failed to update PATH in registry",
                details=f"Return code: {reg_result.returncode}, Stderr: {stderr_str}",
            )

    @staticmethod
    def _normalize_list(path_str: str) -> list[str]:
        """Normalize PATH entries list."""
        try:
            entries = [p.strip() for p in path_str.split(";") if p.strip()]
            return [str(Path(p)) for p in entries]
        except Exception as e:
            raise UserPathServiceError(
                message="Failed to normalize PATH entries",
                details=f"Exception type: {type(e).__name__}, Path string: {path_str}",
            ) from e

    @staticmethod
    def _ensure_str(value: str | bytes) -> str:
        """Ensure string value, decoding bytes if needed."""
        return value.decode() if isinstance(value, bytes) else value

    @staticmethod
    def _validate_entry(entry_path: str, context: str) -> None:
        """Validate entry path.

        Args:
            entry_path: Path entry to validate
            context: Context for validation error message

        Raises:
            ValidationError: If entry_path is invalid (programming error)
        """
        if not entry_path:
            raise ValidationServiceError(
                message="Entry path cannot be empty",
                operation=context,
                details=f"Empty entry path provided for {context}",
            )
