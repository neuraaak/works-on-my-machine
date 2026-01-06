#!/usr/bin/env python3
"""
PATH Manager for Works On My Machine.

Handles PATH backup, restoration, and management operations.
Provides a unified interface for cross-platform PATH management.
"""

# =============================================================================
# IMPORTS
# =============================================================================

# Standard library imports
import json
import logging
import os
import platform
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Third-party imports
from rich.console import Console
from rich.table import Table

# Local imports
from ...exceptions.system import FileSystemError, RegistryError, UserPathError
from ...ui import (
    InteractiveMenu,
    create_backup_table,
    format_backup_item,
    print_error,
    print_header,
    print_info,
    print_success,
    print_system,
)
from ...utils.cli_utils import run_silent
from ...utils.system.user_path_utils import (
    get_current_system_path,
    remove_from_unix_path,
    remove_from_windows_path,
    setup_unix_path,
    setup_windows_path,
)

# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# MAIN CLASS
# =============================================================================


class PathManager:
    """Manages PATH operations for Works On My Machine.

    Provides cross-platform PATH management including backup, restoration,
    and modification operations with integrated UI feedback.
    """

    def __init__(self, target: Optional[str] = None):
        """
        Initialize the path manager.

        Args:
            target: Custom target directory (default: ~/.womm)

        Raises:
            UserPathError: If path manager initialization fails
        """
        try:
            # Input validation
            if target is not None and not isinstance(target, str):
                raise UserPathError(
                    message="Target parameter must be a string",
                    details=f"Received type: {type(target).__name__}",
                )

            if target:
                self.target_path = Path(target).expanduser().resolve()
            else:
                self.target_path = Path.home() / ".womm"

            self.backup_dir = self.target_path / ".backup"
            self.latest_backup = self.backup_dir / ".path.json"
            self.platform = platform.system()

        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Failed to initialize PathManager: {e}")
            raise UserPathError(
                message=f"Path manager initialization failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # =============================================================================
    # PUBLIC METHODS - UI INTEGRATED
    # =============================================================================

    def list_backup(self) -> None:
        """
        List available PATH backups with integrated UI.

        This method handles the complete UI flow for listing backup information.

        Raises:
            UserPathError: If backup listing fails
        """
        try:
            print_header("W.O.M.M PATH Backup List")

            # Get backup information
            result = self._list_backups()

            # Display results using console functions
            if result["success"]:
                print_system(f"Backup location: {result['backup_location']}")
                print_success("PATH backup information retrieved successfully!")

                if result["backups"]:
                    print("")
                    # Create and display backup table
                    backup_table = create_backup_table(result["backups"])
                    console = Console()
                    console.print(backup_table)
                else:
                    print("")
                    print_system("No backup files found")
            else:
                print_error("Failed to retrieve backup information")
                for error in result["errors"]:
                    print_error(error)

        except UserPathError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in list_backup: {e}")
            raise UserPathError(
                message=f"Backup listing failed: {e}",
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
            print_header("W.O.M.M PATH Backup Creation")

            # Create backup directory if it doesn't exist
            try:
                self.backup_dir.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                raise FileSystemError(
                    operation="directory_creation",
                    file_path=str(self.backup_dir),
                    reason=f"Failed to create backup directory: {e}",
                    details=f"Cannot create directory: {self.backup_dir}",
                ) from e

            # Get current PATH
            current_path = get_current_system_path()

            # Create JSON backup file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_json = self.backup_dir / f".path_{timestamp}.json"
            sep = os.pathsep or ";"
            entries = [p for p in current_path.split(sep) if p]
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
                raise FileSystemError(
                    operation="file_writing",
                    file_path=str(backup_json),
                    reason=f"Failed to write backup file: {e}",
                    details=f"Cannot write to backup file: {backup_json}",
                ) from e
            except (TypeError, ValueError) as e:
                raise UserPathError(
                    message=f"Failed to serialize backup data: {e}",
                    details="JSON serialization failed for backup payload",
                ) from e

            # Update latest backup reference (copy instead of symlink for Windows compatibility)
            try:
                if self.latest_backup.exists():
                    self.latest_backup.unlink()
                shutil.copy2(backup_json, self.latest_backup)
            except (PermissionError, OSError) as e:
                logger.warning(f"Failed to update latest backup reference: {e}")
                # Continue without updating latest backup reference

            # Display success results
            print_success("PATH backup (JSON) created successfully!")
            print_system(f"Backup location: {self.backup_dir}")
            print_system(f"Backup file: {backup_json.name}")
            print_info(f"PATH length: {len(current_path)} characters")

        except (UserPathError, RegistryError, FileSystemError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in backup_path: {e}")
            raise UserPathError(
                message=f"PATH backup failed: {e}",
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
            console = Console()
            print_header("W.O.M.M PATH Restoration")

            # Check if any backup files exist (JSON only)
            try:
                backup_files = list(self.backup_dir.glob(".path_*.json"))
            except Exception as e:
                raise FileSystemError(
                    operation="directory_scanning",
                    file_path=str(self.backup_dir),
                    reason=f"Failed to scan backup directory: {e}",
                    details=f"Cannot access backup directory: {self.backup_dir}",
                ) from e

            if not backup_files:
                raise UserPathError(
                    message="No PATH backup found",
                    details=f"Target path: {self.target_path}, Backup location: {self.backup_dir}, No backup files matching pattern '.path_*.json' found",
                )

            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Create selection table
            table = Table(title="Available PATH Backups")
            table.add_column("Index", style="cyan", no_wrap=True)
            table.add_column("Backup File", style="green")
            table.add_column("Date", style="yellow")
            table.add_column("Size", style="blue")
            table.add_column("PATH Entries", style="magenta")

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
                        logger.warning(
                            f"Failed to read backup file {backup_file.name}: {e}"
                        )
                        continue
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        logger.warning(
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
                    logger.warning(f"Error reading backup {backup_file.name}: {e}")
                    continue

            if not backup_info_list:
                raise UserPathError(
                    message="No valid backup files found",
                    details="All backup files failed to load or parse",
                )

            # Display backup selection table
            console.print(table)
            print("")

            # Interactive selection with checkbox menu
            try:
                menu = InteractiveMenu(
                    title="Select Backup to Restore", border_style="cyan"
                )
                selected_backup = menu.select_from_list(
                    backup_info_list, display_func=format_backup_item
                )
            except Exception as e:
                raise UserPathError(
                    message=f"Failed to create interactive menu: {e}",
                    details="UI interaction failed during backup selection",
                ) from e

            if selected_backup is None:
                print_system("Restoration cancelled")
                return

            # Confirm selection
            selected_file = selected_backup["file"]
            path_value = selected_backup["path_value"]
            path_entries = selected_backup["path_entries"]

            print_info(f"Selected: {selected_file.name}")
            print_info(
                f"Date: {datetime.fromtimestamp(selected_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}"
            )
            print_info(f"PATH entries: {path_entries}")
            print_info(f"PATH length: {len(path_value)} characters")

            # Ask for confirmation with interactive menu
            try:
                confirm_menu = InteractiveMenu(
                    title="Confirm Restoration", border_style="yellow"
                )
                if not confirm_menu.confirm_action(
                    "Proceed with restoration?", default_yes=True
                ):
                    print_system("Restoration cancelled")
                    return
            except Exception as e:
                raise UserPathError(
                    message=f"Failed to create confirmation menu: {e}",
                    details="UI interaction failed during restoration confirmation",
                ) from e

            # Restore PATH
            if self.platform == "Windows":
                try:
                    restore_result = run_silent(
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
                    raise RegistryError(
                        registry_key="HKCU\\Environment",
                        operation="update",
                        reason=f"Failed to execute registry update: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                if not restore_result.success:
                    raise RegistryError(
                        registry_key="HKCU\\Environment",
                        operation="update",
                        reason="Failed to restore Windows user PATH",
                        details=f"Return code: {restore_result.returncode}",
                    )
            else:
                # For Unix, we can only update current session
                os.environ["PATH"] = path_value

            # Display success results
            print_success("PATH restored successfully!")
            print_info(f"Restored from backup: {selected_file.name}")
            print_info(f"Restored {path_entries} PATH entries")
            print_info(
                "You may need to restart your terminal for changes to take effect"
            )

        except (UserPathError, RegistryError, FileSystemError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in restore_path: {e}")
            raise UserPathError(
                message=f"PATH restoration failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # =============================================================================
    # PUBLIC METHODS - UTILITY OPERATIONS
    # =============================================================================

    def add_to_path(self) -> Dict:
        """
        Add WOMM to PATH environment variable.

        Returns:
            Dictionary with operation results

        Raises:
            UserPathError: If PATH addition fails
            RegistryError: If registry operations fail
            FileSystemError: If file system operations fail
        """
        try:
            womm_path = str(self.target_path)

            if self.platform == "Windows":
                try:
                    return setup_windows_path(womm_path, get_current_system_path())
                except (RegistryError, FileSystemError, UserPathError):
                    # Re-raise our custom exceptions
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise UserPathError(
                        message=f"Failed to setup Windows PATH: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e
            else:
                try:
                    return setup_unix_path(womm_path, get_current_system_path())
                except (FileSystemError, UserPathError):
                    # Re-raise our custom exceptions
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise UserPathError(
                        message=f"Failed to setup Unix PATH: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

        except (UserPathError, RegistryError, FileSystemError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in add_to_path: {e}")
            raise UserPathError(
                message=f"PATH addition failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def remove_from_path(self) -> Dict:
        """
        Remove WOMM from PATH environment variable.

        Returns:
            Dictionary with operation results

        Raises:
            UserPathError: If PATH removal fails
            RegistryError: If registry operations fail
            FileSystemError: If file system operations fail
        """
        try:
            womm_path = str(self.target_path)

            if self.platform == "Windows":
                try:
                    return remove_from_windows_path(womm_path)
                except (RegistryError, FileSystemError, UserPathError):
                    # Re-raise our custom exceptions
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise UserPathError(
                        message=f"Failed to remove from Windows PATH: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e
            else:
                try:
                    return remove_from_unix_path(womm_path)
                except (FileSystemError, UserPathError):
                    # Re-raise our custom exceptions
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise UserPathError(
                        message=f"Failed to remove from Unix PATH: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

        except (UserPathError, RegistryError, FileSystemError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in remove_from_path: {e}")
            raise UserPathError(
                message=f"PATH removal failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # =============================================================================
    # PRIVATE METHODS - INTERNAL OPERATIONS
    # =============================================================================

    def _backup_path(self) -> Dict:
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
                raise FileSystemError(
                    operation="directory_creation",
                    file_path=str(self.backup_dir),
                    reason=f"Failed to create backup directory: {e}",
                    details=f"Cannot create directory: {self.backup_dir}",
                ) from e

            # Get current PATH
            try:
                current_path = get_current_system_path()
            except (UserPathError, RegistryError) as e:
                result["errors"].append(str(e))
                return result

            # Create JSON backup file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_json = self.backup_dir / f".path_{timestamp}.json"
            sep = os.pathsep or ";"
            entries = [p for p in current_path.split(sep) if p]
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
                raise FileSystemError(
                    operation="file_writing",
                    file_path=str(backup_json),
                    reason=f"Failed to write backup file: {e}",
                    details=f"Cannot write to backup file: {backup_json}",
                ) from e
            except (TypeError, ValueError) as e:
                raise UserPathError(
                    message=f"Failed to serialize backup data: {e}",
                    details="JSON serialization failed for backup payload",
                ) from e

            # Update latest backup reference (copy instead of symlink for Windows compatibility)
            try:
                if self.latest_backup.exists():
                    self.latest_backup.unlink()
                shutil.copy2(backup_json, self.latest_backup)
            except (PermissionError, OSError) as e:
                logger.warning(f"Failed to update latest backup reference: {e}")
                # Continue without updating latest backup reference

            # Get list of all backup files (JSON only)
            try:
                backup_files = sorted(
                    self.backup_dir.glob(".path_*.json"), reverse=True
                )
                result["backup_files"] = [str(f.name) for f in backup_files]
            except Exception as e:
                logger.warning(f"Failed to list backup files: {e}")
                # Continue with empty backup files list

            result["success"] = True
            return result

        except (UserPathError, RegistryError, FileSystemError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _backup_path: {e}")
            raise UserPathError(
                message=f"PATH backup creation failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _list_backups(self) -> Dict:
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
                raise FileSystemError(
                    operation="directory_scanning",
                    file_path=str(self.backup_dir),
                    reason=f"Failed to scan backup directory: {e}",
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
                        logger.warning(
                            f"Failed to read backup file {backup_file.name}: {e}"
                        )
                        continue
                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        logger.warning(
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

        except (UserPathError, FileSystemError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _list_backups: {e}")
            raise UserPathError(
                message=f"Backup listing failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e
