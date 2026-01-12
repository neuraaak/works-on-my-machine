#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM PATH INTERFACE - User PATH Manager Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
User PATH Manager Interface for Works On My Machine.

Handles PATH backup, restoration, and management operations.
Provides a unified interface for cross-platform PATH management.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import os
import platform
import shutil
from datetime import datetime
from pathlib import Path

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.system import (
    FileSystemServiceError,
    RegistryServiceError,
    UserPathInterfaceError,
    UserPathServiceError,
)
from ...services import CommandRunnerService, SystemPathService
from ...shared.results.system_results import PathOperationResult
from ...ui.common.ezpl_bridge import (
    ezlogger,
    ezpl_bridge,
    ezprinter,
)
from ...ui.common.interactive_menu import InteractiveMenu, format_backup_item
from ...utils.womm_setup import get_womm_installation_path

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class SystemPathInterface:
    """Manages PATH operations for Works On My Machine.

    Provides cross-platform PATH management including backup, restoration,
    and modification operations with integrated UI feedback.
    """

    def __init__(self, target: str | None = None) -> None:
        """Initialize the path manager.

        Args:
            target: Custom target directory (default: ~/.womm)

        Raises:
            PathManagerInterfaceError: If path manager initialization fails
        """
        try:
            # Initialize services
            self._path_service = SystemPathService()
            self._command_runner = CommandRunnerService()

            # Input validation
            if target is not None and not isinstance(target, str):
                raise UserPathInterfaceError(
                    message="Target parameter must be a string",
                    operation="initialization",
                    path=str(target) if target else "",
                    details=f"Received type: {type(target).__name__}",
                )

            if target:
                self.target_path = Path(target).expanduser().resolve()
            else:
                # Use actual installation path if available, fallback to default
                self.target_path = get_womm_installation_path()

            self.backup_dir = self.target_path / ".backup"
            self.latest_backup = self.backup_dir / ".path.json"
            self.platform = platform.system()

        except UserPathInterfaceError:
            raise
        except Exception as e:
            ezlogger.error(f"Failed to initialize UserPathManagerInterface: {e}")
            raise UserPathInterfaceError(
                message=f"Path manager initialization failed: {e}",
                operation="initialization",
                path=str(target) if target else "",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def list_backup(self) -> None:
        """
        List available PATH backups with integrated UI.

        This method handles the complete UI flow for listing backup information.

        Raises:
            UserPathError: If backup listing fails
        """
        try:
            ezprinter.print_header("W.O.M.M PATH Backup List")

            # Get backup information
            result = self._list_backups()

            # Display results using console functions
            if result["success"]:
                ezprinter.system(f"Backup location: {result['backup_location']}")
                ezprinter.success("PATH backup information retrieved successfully!")

                if result["backups"]:
                    ezpl_bridge.console.print("")
                    # Create and display backup table
                    backup_table = ezprinter.create_backup_table(result["backups"])
                    ezpl_bridge.console.print(backup_table)
                else:
                    ezpl_bridge.console.print("")
                    ezprinter.system("No backup files found")
            else:
                ezprinter.error("Failed to retrieve backup information")
                for error in result["errors"]:
                    ezprinter.error(error)

        except UserPathInterfaceError:
            raise
        except (UserPathServiceError, FileSystemServiceError) as e:
            ezlogger.error(f"Service error in list_backup: {e}")
            raise UserPathInterfaceError(
                message=f"Backup listing failed: {e}",
                operation="list_backup",
                path=str(self.target_path),
                details=f"Service exception: {type(e).__name__}",
            ) from e
        except Exception as e:
            ezlogger.error(f"Unexpected error in list_backup: {e}")
            raise UserPathInterfaceError(
                message=f"Backup listing failed: {e}",
                operation="list_backup",
                path=str(self.target_path),
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def backup_path(self) -> None:
        """
        Create a new PATH backup with integrated UI.

        This method handles the complete UI flow for creating a new backup.

        Raises:
            UserPathError: If backup creation fails
            RegistryError: If registry operations fail
            FileSystemError: If file system operations fail
        """
        try:
            ezprinter.print_header("W.O.M.M PATH Backup Creation")

            # Create backup directory if it doesn't exist
            try:
                self.backup_dir.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                raise UserPathInterfaceError(
                    message=f"Failed to create backup directory: {e}",
                    operation="backup_path",
                    path=str(self.backup_dir),
                    details=f"Cannot create directory: {self.backup_dir}",
                ) from e

            # Get current PATH
            try:
                path_result = self._path_service.get_current_system_path()
            except (
                UserPathServiceError,
                RegistryServiceError,
                ValidationServiceError,
            ) as e:
                ezlogger.error(f"Service error in backup_path: {e}")
                raise UserPathInterfaceError(
                    message=f"Failed to get current PATH: {e}",
                    operation="backup_path",
                    path=str(self.target_path),
                    details=f"Service exception: {type(e).__name__}",
                ) from e

            # Check result
            if not path_result.success:
                ezprinter.error(f"Failed to get current PATH: {path_result.message}")
                raise UserPathInterfaceError(
                    message=path_result.message or "Failed to get current PATH",
                    operation="backup_path",
                    path=str(self.target_path),
                    details=path_result.error or "",
                )

            # Create JSON backup file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_json = self.backup_dir / f".path_{timestamp}.json"
            sep = os.pathsep or ";"
            current_path = sep.join(path_result.path_entries or [])
            entries = path_result.path_entries or []
            payload = {
                "type": "womm_path_backup",
                "version": 1,
                "timestamp": timestamp,
                "platform": self.platform,
                "target": str(self.target_path),
                "separator": sep,
                "path_string": current_path,
                "entries": entries,
                "length": len(current_path),
            }

            try:
                with open(backup_json, "w", encoding="utf-8") as jf:
                    json.dump(payload, jf, indent=2, ensure_ascii=False)
            except (PermissionError, OSError) as e:
                raise UserPathInterfaceError(
                    message=f"Failed to write backup file: {e}",
                    operation="backup_path",
                    path=str(backup_json),
                    details=f"Cannot write to backup file: {backup_json}",
                ) from e
            except (TypeError, ValueError) as e:
                raise UserPathInterfaceError(
                    message=f"Failed to serialize backup data: {e}",
                    operation="backup_path",
                    path=str(backup_json),
                    details="JSON serialization failed for backup payload",
                ) from e

            # Update latest backup reference (copy instead of symlink for Windows compatibility)
            try:
                if self.latest_backup.exists():
                    self.latest_backup.unlink()
                shutil.copy2(backup_json, self.latest_backup)
            except (PermissionError, OSError) as e:
                ezlogger.warning(f"Failed to update latest backup reference: {e}")
                # Continue without updating latest backup reference

            # Display success results
            ezprinter.success("PATH backup (JSON) created successfully!")
            ezprinter.system(f"Backup location: {self.backup_dir}")
            ezprinter.system(f"Backup file: {backup_json.name}")
            ezprinter.info(f"PATH length: {len(current_path)} characters")

        except UserPathInterfaceError:
            raise
        except (
            UserPathServiceError,
            RegistryServiceError,
            FileSystemServiceError,
        ) as e:
            ezlogger.error(f"Service error in backup_path: {e}")
            raise UserPathInterfaceError(
                message=f"PATH backup failed: {e}",
                operation="backup_path",
                path=str(self.target_path),
                details=f"Service exception: {type(e).__name__}",
            ) from e
        except Exception as e:
            ezlogger.error(f"Unexpected error in backup_path: {e}")
            raise UserPathInterfaceError(
                message=f"PATH backup failed: {e}",
                operation="backup_path",
                path=str(self.target_path),
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def restore_path(self) -> None:
        """
        Restore user PATH from backup with integrated UI.

        This method handles the complete UI flow for PATH restoration.

        Raises:
            UserPathError: If PATH restoration fails
            RegistryError: If registry operations fail
            FileSystemError: If file system operations fail
        """
        try:
            ezprinter.print_header("W.O.M.M PATH Restoration")

            # Check if any backup files exist (JSON only)
            try:
                backup_files = list(self.backup_dir.glob(".path_*.json"))
            except Exception as e:
                raise UserPathInterfaceError(
                    message=f"Failed to scan backup directory: {e}",
                    operation="restore_path",
                    path=str(self.backup_dir),
                    details=f"Cannot access backup directory: {self.backup_dir}",
                ) from e

            if not backup_files:
                raise UserPathInterfaceError(
                    message="No PATH backup found",
                    operation="restore_path",
                    path=str(self.backup_dir),
                    details=f"Target path: {self.target_path}, Backup location: {self.backup_dir}, No backup files matching pattern '.path_*.json' found",
                )

            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Create selection table
            table = ezprinter.create_table(
                title="Available PATH Backups",
                columns=[
                    ("Index", "cyan", True),
                    ("Backup File", "green", False),
                    ("Date", "yellow", False),
                    ("Size", "blue", False),
                    ("PATH Entries", "magenta", False),
                ],
            )

            backup_info_list = []

            for i, backup_file in enumerate(backup_files, 1):
                try:
                    stat = backup_file.stat()
                    modified_date = datetime.fromtimestamp(stat.st_mtime).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    # Read backup JSON content
                    try:
                        data = json.loads(backup_file.read_text(encoding="utf-8"))
                    except (PermissionError, OSError) as e:
                        ezlogger.warning(
                            f"Failed to read backup file {backup_file.name}: {e}"
                        )
                        continue
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        ezlogger.warning(
                            f"Failed to parse backup file {backup_file.name}: {e}"
                        )
                        continue

                    path_value = data.get("path_string", "")
                    entries = data.get("entries", [])
                    path_entries = len(entries)

                    table.add_row(
                        str(i),
                        backup_file.name,
                        modified_date,
                        f"{stat.st_size} bytes",
                        str(path_entries),
                    )

                    backup_info_list.append(
                        {
                            "file": backup_file,
                            "path_value": path_value,
                            "path_entries": path_entries,
                        }
                    )

                except Exception as e:
                    ezlogger.warning(f"Error reading backup {backup_file.name}: {e}")
                    continue

            if not backup_info_list:
                raise UserPathInterfaceError(
                    message="No valid backup files found",
                    operation="restore_path",
                    path=str(self.backup_dir),
                    details="All backup files failed to load or parse",
                )

            # Display backup selection table
            ezpl_bridge.console.print(table)
            ezpl_bridge.console.print("")

            # Interactive selection with checkbox menu
            try:
                menu = InteractiveMenu(
                    title="Select Backup to Restore", border_style="cyan"
                )
                selected_backup = menu.select_from_list(
                    backup_info_list, display_func=format_backup_item
                )
            except Exception as e:
                raise UserPathInterfaceError(
                    message=f"Failed to create interactive menu: {e}",
                    operation="restore_path",
                    path=str(self.backup_dir),
                    details="UI interaction failed during backup selection",
                ) from e

            if selected_backup is None:
                ezprinter.system("Restoration cancelled")
                return

            # Confirm selection
            selected_file = selected_backup["file"]
            path_value = selected_backup["path_value"]
            path_entries = selected_backup["path_entries"]

            ezprinter.info(f"Selected: {selected_file.name}")
            ezprinter.info(
                f"Date: {datetime.fromtimestamp(selected_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}"
            )
            ezprinter.info(f"PATH entries: {path_entries}")
            ezprinter.info(f"PATH length: {len(path_value)} characters")

            # Ask for confirmation with interactive menu
            try:
                confirm_menu = InteractiveMenu(
                    title="Confirm Restoration", border_style="yellow"
                )
                if not confirm_menu.confirm_action(
                    "Proceed with restoration?", default_yes=True
                ):
                    ezprinter.system("Restoration cancelled")
                    return
            except Exception as e:
                raise UserPathInterfaceError(
                    message=f"Failed to create confirmation menu: {e}",
                    operation="restore_path",
                    path=str(self.backup_dir),
                    details="UI interaction failed during restoration confirmation",
                ) from e

            # Restore PATH
            if self.platform == "Windows":
                try:
                    restore_result = self._command_runner.run_silent(
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
                    ezlogger.error(f"Command runner error in restore_path: {e}")
                    raise UserPathInterfaceError(
                        message=f"Failed to execute registry update: {e}",
                        operation="restore_path",
                        path="HKCU\\Environment",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                if not restore_result.returncode == 0:
                    raise UserPathInterfaceError(
                        message="Failed to restore Windows user PATH",
                        operation="restore_path",
                        path="HKCU\\Environment",
                        details=f"Return code: {restore_result.returncode}",
                    )
            else:
                # For Unix, we can only update current session
                os.environ["PATH"] = path_value

            # Display success results
            ezprinter.success("PATH restored successfully!")
            ezprinter.info(f"Restored from backup: {selected_file.name}")
            ezprinter.info(f"Restored {path_entries} PATH entries")
            ezprinter.info(
                "You may need to restart your terminal for changes to take effect"
            )

        except UserPathInterfaceError:
            raise
        except (
            UserPathServiceError,
            RegistryServiceError,
            FileSystemServiceError,
        ) as e:
            ezlogger.error(f"Service error in restore_path: {e}")
            raise UserPathInterfaceError(
                message=f"PATH restoration failed: {e}",
                operation="restore_path",
                path=str(self.backup_dir),
                details=f"Service exception: {type(e).__name__}",
            ) from e
        except Exception as e:
            ezlogger.error(f"Unexpected error in restore_path: {e}")
            raise UserPathInterfaceError(
                message=f"PATH restoration failed: {e}",
                operation="restore_path",
                path=str(self.backup_dir),
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def add_to_path(self) -> PathOperationResult:
        """
        Add WOMM to PATH environment variable.

        Returns:
            PathOperationResult: Result of the PATH addition operation

        Raises:
            UserPathError: If PATH addition fails
            RegistryError: If registry operations fail
            FileSystemError: If file system operations fail
        """
        try:
            womm_path = str(self.target_path)

            # Get current PATH first
            try:
                current_path_result = self._path_service.get_current_system_path()
            except (RegistryServiceError, ValidationServiceError) as e:
                ezlogger.error(f"Service error getting current PATH: {e}")
                raise UserPathInterfaceError(
                    message=f"Failed to get current PATH: {e}",
                    operation="add_to_path",
                    path=womm_path,
                    details=f"Service exception: {type(e).__name__}",
                ) from e

            if not current_path_result.success:
                ezprinter.error(
                    f"Failed to get current PATH: {current_path_result.message}"
                )
                raise UserPathInterfaceError(
                    message=current_path_result.message or "Failed to get current PATH",
                    operation="add_to_path",
                    path=womm_path,
                    details=current_path_result.error or "",
                )

            # Build original path string from entries
            sep = os.pathsep or (";" if self.platform == "Windows" else ":")
            original_path = sep.join(current_path_result.path_entries or [])

            if self.platform == "Windows":
                try:
                    result = self._path_service.setup_windows_path(
                        womm_path, original_path
                    )
                    # Process result and display via UI
                    if result.success:
                        if result.path_modified:
                            ezprinter.success(result.message)
                        else:
                            ezprinter.info(result.message)
                    else:
                        ezprinter.error(
                            result.message or "Failed to setup Windows PATH"
                        )
                    return result
                except (RegistryServiceError, ValidationServiceError) as e:
                    ezlogger.error(f"Service error in add_to_path (Windows): {e}")
                    raise UserPathInterfaceError(
                        message=f"Failed to setup Windows PATH: {e}",
                        operation="add_to_path",
                        path=womm_path,
                        details=f"Service exception: {type(e).__name__}",
                    ) from e
            else:
                try:
                    result = self._path_service.setup_unix_path(
                        womm_path, original_path
                    )
                    # Process result and display via UI
                    if result.success:
                        if result.path_modified:
                            ezprinter.success(result.message)
                        else:
                            ezprinter.info(result.message)
                    else:
                        ezprinter.error(result.message or "Failed to setup Unix PATH")
                    return result
                except (FileSystemServiceError, ValidationServiceError) as e:
                    ezlogger.error(f"Service error in add_to_path (Unix): {e}")
                    raise UserPathInterfaceError(
                        message=f"Failed to setup Unix PATH: {e}",
                        operation="add_to_path",
                        path=womm_path,
                        details=f"Service exception: {type(e).__name__}",
                    ) from e

        except UserPathInterfaceError:
            raise
        except Exception as e:
            ezlogger.error(f"Unexpected error in add_to_path: {e}")
            raise UserPathInterfaceError(
                message=f"PATH addition failed: {e}",
                operation="add_to_path",
                path=womm_path,
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def remove_from_path(self) -> PathOperationResult:
        """
        Remove WOMM from PATH environment variable.

        Returns:
            PathOperationResult: Result of the PATH removal operation

        Raises:
            PathManagerInterfaceError: If PATH removal fails
        """
        try:
            womm_path = str(self.target_path)

            if self.platform == "Windows":
                try:
                    result = self._path_service.remove_from_windows_path(womm_path)
                    # Process result and display via UI
                    if result.success:
                        if result.path_modified:
                            ezprinter.success(result.message)
                        else:
                            ezprinter.info(result.message)
                    else:
                        ezprinter.error(
                            result.message or "Failed to remove from Windows PATH"
                        )
                    return result
                except (RegistryServiceError, ValidationServiceError) as e:
                    ezlogger.error(f"Service error in remove_from_path (Windows): {e}")
                    raise UserPathInterfaceError(
                        message=f"Failed to remove from Windows PATH: {e}",
                        operation="remove_from_path",
                        path=womm_path,
                        details=f"Service exception: {type(e).__name__}",
                    ) from e
            else:
                try:
                    result = self._path_service.remove_from_unix_path(womm_path)
                    # Process result and display via UI
                    if result.success:
                        if result.path_modified:
                            ezprinter.success(result.message)
                        else:
                            ezprinter.info(result.message)
                    else:
                        ezprinter.error(
                            result.message or "Failed to remove from Unix PATH"
                        )
                    return result
                except (FileSystemServiceError, ValidationServiceError) as e:
                    ezlogger.error(f"Service error in remove_from_path (Unix): {e}")
                    raise UserPathInterfaceError(
                        message=f"Failed to remove from Unix PATH: {e}",
                        operation="remove_from_path",
                        path=womm_path,
                        details=f"Service exception: {type(e).__name__}",
                    ) from e

        except UserPathInterfaceError:
            raise
        except Exception as e:
            ezlogger.error(f"Unexpected error in remove_from_path: {e}")
            raise UserPathInterfaceError(
                message=f"PATH removal failed: {e}",
                operation="remove_from_path",
                path=womm_path,
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _backup_path(self) -> dict:
        """
        Backup the current user PATH.

        Returns:
            Dictionary containing backup results

        Raises:
            UserPathError: If backup creation fails
            RegistryError: If registry operations fail
            FileSystemError: If file system operations fail
        """
        try:
            result = {
                "success": False,
                "target_path": str(self.target_path),
                "backup_location": str(self.backup_dir),
                "backup_files": [],
                "errors": [],
            }

            # Create backup directory if it doesn't exist
            try:
                self.backup_dir.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                raise UserPathInterfaceError(
                    message=f"Failed to create backup directory: {e}",
                    operation="_backup_path",
                    path=str(self.backup_dir),
                    details=f"Cannot create directory: {self.backup_dir}",
                ) from e

            # Get current PATH
            try:
                path_result = self._path_service.get_current_system_path()
            except (
                UserPathServiceError,
                RegistryServiceError,
                ValidationServiceError,
            ) as e:
                ezlogger.warning(f"Service error in _backup_path: {e}")
                result["errors"].append(str(e))
                return result

            # Check result
            if not path_result.success:
                result["errors"].append(
                    path_result.message or "Failed to get current PATH"
                )
                return result

            # Create JSON backup file with timestamp
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
                "target": str(self.target_path),
                "separator": sep,
                "path_string": current_path,
                "entries": entries,
                "length": len(current_path),
            }

            try:
                with open(backup_json, "w", encoding="utf-8") as jf:
                    json.dump(payload, jf, indent=2, ensure_ascii=False)
            except (PermissionError, OSError) as e:
                raise UserPathInterfaceError(
                    message=f"Failed to write backup file: {e}",
                    operation="_backup_path",
                    path=str(backup_json),
                    details=f"Cannot write to backup file: {backup_json}",
                ) from e
            except (TypeError, ValueError) as e:
                raise UserPathInterfaceError(
                    message=f"Failed to serialize backup data: {e}",
                    operation="_backup_path",
                    path=str(backup_json),
                    details="JSON serialization failed for backup payload",
                ) from e

            # Update latest backup reference (copy instead of symlink for Windows compatibility)
            try:
                if self.latest_backup.exists():
                    self.latest_backup.unlink()
                shutil.copy2(backup_json, self.latest_backup)
            except (PermissionError, OSError) as e:
                ezlogger.warning(f"Failed to update latest backup reference: {e}")
                # Continue without updating latest backup reference

            # Get list of all backup files (JSON only)
            try:
                backup_files = sorted(
                    self.backup_dir.glob(".path_*.json"), reverse=True
                )
                result["backup_files"] = [str(f.name) for f in backup_files]
            except Exception as e:
                ezlogger.warning(f"Failed to list backup files: {e}")
                # Continue with empty backup files list

            result["success"] = True
            return result

        except UserPathInterfaceError:
            raise
        except (
            UserPathServiceError,
            RegistryServiceError,
            FileSystemServiceError,
        ) as e:
            ezlogger.error(f"Service error in _backup_path: {e}")
            raise UserPathInterfaceError(
                message=f"PATH backup creation failed: {e}",
                operation="_backup_path",
                path=str(self.target_path),
                details=f"Service exception: {type(e).__name__}",
            ) from e
        except Exception as e:
            ezlogger.error(f"Unexpected error in _backup_path: {e}")
            raise UserPathInterfaceError(
                message=f"PATH backup creation failed: {e}",
                operation="_backup_path",
                path=str(self.target_path),
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _list_backups(self) -> dict:
        """
        List available PATH backups.

        Returns:
            Dictionary containing backup information

        Raises:
            UserPathError: If backup listing fails
            FileSystemError: If file system operations fail
        """
        try:
            result = {
                "success": False,
                "target_path": str(self.target_path),
                "backup_location": str(self.backup_dir),
                "backups": [],
                "latest_backup": "",
                "errors": [],
            }

            if not self.backup_dir.exists():
                result["errors"].append("No backup directory found")
                return result

            # Get all backup files (JSON only)
            try:
                backup_files = list(self.backup_dir.glob(".path_*.json"))
            except Exception as e:
                raise UserPathInterfaceError(
                    message=f"Failed to scan backup directory: {e}",
                    operation="_list_backups",
                    path=str(self.backup_dir),
                    details=f"Cannot access backup directory: {self.backup_dir}",
                ) from e

            if not backup_files:
                result["errors"].append("No PATH backups found")
                return result

            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            for backup_file in backup_files:
                try:
                    stat = backup_file.stat()
                    try:
                        data = json.loads(backup_file.read_text(encoding="utf-8"))
                    except (PermissionError, OSError) as e:
                        ezlogger.warning(
                            f"Failed to read backup file {backup_file.name}: {e}"
                        )
                        continue
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        ezlogger.warning(
                            f"Failed to parse backup file {backup_file.name}: {e}"
                        )
                        continue

                    backup_info = {
                        "name": backup_file.name,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "description": f"JSON backup ({data.get('timestamp', '')})",
                    }
                    result["backups"].append(backup_info)

                    # Mark as latest if it's the most recent
                    if not result["latest_backup"]:
                        result["latest_backup"] = backup_file.name

                except Exception as e:
                    result["errors"].append(f"Error listing backups: {e}")
                    continue

            result["success"] = True
            return result

        except UserPathInterfaceError:
            raise
        except (UserPathServiceError, FileSystemServiceError) as e:
            ezlogger.error(f"Service error in _list_backups: {e}")
            raise UserPathInterfaceError(
                message=f"Backup listing failed: {e}",
                operation="_list_backups",
                path=str(self.backup_dir),
                details=f"Service exception: {type(e).__name__}",
            ) from e
        except Exception as e:
            ezlogger.error(f"Unexpected error in _list_backups: {e}")
            raise UserPathInterfaceError(
                message=f"Backup listing failed: {e}",
                operation="_list_backups",
                path=str(self.backup_dir),
                details=f"Exception type: {type(e).__name__}",
            ) from e
