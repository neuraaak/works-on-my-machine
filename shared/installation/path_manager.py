#!/usr/bin/env python3
"""
PATH Manager for Works On My Machine.
Handles PATH backup, restoration, and management operations.
"""

# IMPORTS
########################################################
# Standard library imports
import os
import platform
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Third-party imports
# (None for this file)

# Local imports
try:
    from shared.core.cli_manager import run_silent
except ImportError:
    # Fallback if module not available
    import subprocess

    def run_silent(cmd, **kwargs):
        """Run a command silently."""
        return subprocess.run(cmd, capture_output=True, **kwargs)  # noqa: S603


# MAIN CLASS
########################################################
# Core PATH management functionality


class PathManager:
    """Manages PATH operations for Works On My Machine."""

    def __init__(self, target: Optional[str] = None):
        """Initialize the path manager.

        Args:
            target: Custom target directory (default: ~/.womm)
        """
        if target:
            self.target_path = Path(target).expanduser().resolve()
        else:
            self.target_path = Path.home() / ".womm"

        self.backup_dir = self.target_path / ".backup"
        self.latest_backup = self.backup_dir / ".path"
        self.platform = platform.system()

    # PUBLIC METHODS
    ########################################################
    # Main interface methods for PATH operations

    def list_backup(self) -> None:
        """List available PATH backups with integrated UI.

        This method handles the complete UI flow for listing backup information.
        """
        try:
            from shared.ui.console import (
                print_error,
                print_header,
                print_success,
                print_system,
            )
            from shared.ui.tables import create_backup_table

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
                    from rich.console import Console

                    console = Console()
                    console.print(backup_table)
                else:
                    print("")
                    print_system("No backup files found")
            else:
                print_error("Failed to retrieve backup information")
                for error in result["errors"]:
                    print_error(error)

        except ImportError as e:
            print(f"[FAIL] Error importing UI components: {e}")
        except Exception as e:
            print(f"[FAIL] Error displaying backup information: {e}")

    def backup_path(self) -> None:
        """Create a new PATH backup with integrated UI.

        This method handles the complete UI flow for creating a new backup.
        """
        try:
            from shared.ui.console import (
                print_error,
                print_header,
                print_info,
                print_success,
                print_system,
            )

            print_header("W.O.M.M PATH Backup Creation")

            # Create backup directory if it doesn't exist
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # Get current PATH
            if self.platform == "Windows":
                # Use environment variable for Windows
                current_path = os.environ.get("PATH", "")
                if not current_path:
                    print_error("Failed to read Windows PATH from environment")
                    return
            else:
                current_path = os.environ.get("PATH", "")

            # Create backup file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f".path_{timestamp}"

            with open(backup_file, "w", encoding="utf-8") as f:
                f.write(f"# WOMM PATH Backup - {timestamp}\n")
                f.write(f"# Platform: {self.platform}\n")
                f.write(f"# Target: {self.target_path}\n")
                f.write("# Original PATH:\n")
                f.write(f"{current_path}\n")

            # Update latest backup reference (copy instead of symlink for Windows compatibility)
            if self.latest_backup.exists():
                self.latest_backup.unlink()
            # Copy the backup file to .path (latest reference)
            shutil.copy2(backup_file, self.latest_backup)

            # Display success results
            print_success("PATH backup created successfully!")
            print_system(f"Backup location: {self.backup_dir}")
            print_system(f"Backup file: {backup_file.name}")
            print_info(f"PATH length: {len(current_path)} characters")

        except ImportError as e:
            print(f"[FAIL] Error importing UI components: {e}")
        except Exception as e:
            print(f"[FAIL] Error creating PATH backup: {e}")

    def restore_path(self) -> None:
        """Restore user PATH from backup with integrated UI.

        This method handles the complete UI flow for PATH restoration.
        """
        try:
            from rich.console import Console
            from rich.table import Table

            from shared.ui.console import (
                print_error,
                print_header,
                print_info,
                print_success,
                print_system,
            )

            console = Console()
            print_header("W.O.M.M PATH Restoration")

            # Check if any backup files exist
            backup_files = list(self.backup_dir.glob(".path_*"))
            if not backup_files:
                print_error("No PATH backup found")
                return

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

                    # Read backup content to count PATH entries
                    with open(backup_file, encoding="utf-8") as f:
                        content = f.read()

                    # Parse PATH entries
                    path_value = ""
                    lines = content.split("\n")

                    # Find the line after "# Original PATH:"
                    for j, line in enumerate(lines):
                        if line.strip() == "# Original PATH:" and j + 1 < len(lines):
                            path_value = lines[j + 1].strip()
                            break

                    # Fallback: if we didn't find the marker, look for the last non-comment line
                    if not path_value:
                        for line in reversed(lines):
                            if not line.startswith("#") and line.strip():
                                path_value = line.strip()
                                break

                    # Count PATH entries (split by separator)
                    path_entries = (
                        len(path_value.split(os.pathsep)) if path_value else 0
                    )

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
                    print_error(f"Error reading backup {backup_file.name}: {e}")
                    continue

            if not backup_info_list:
                print_error("No valid backup files found")
                return

            # Display backup selection table
            console.print(table)
            print("")

            # Interactive selection with checkbox menu
            from shared.ui.interactive import InteractiveMenu, format_backup_item

            menu = InteractiveMenu(
                title="Select Backup to Restore", border_style="cyan"
            )
            selected_backup = menu.select_from_list(
                backup_info_list, display_func=format_backup_item
            )

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
            confirm_menu = InteractiveMenu(
                title="Confirm Restoration", border_style="yellow"
            )
            if not confirm_menu.confirm_action(
                "Proceed with restoration?", default_yes=True
            ):
                print_system("Restoration cancelled")
                return

            # Restore PATH
            if self.platform == "Windows":
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
                if not restore_result.success:
                    print_error("Failed to restore Windows user PATH")
                    return
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

        except ImportError as e:
            print(f"[FAIL] Error importing UI components: {e}")
        except Exception as e:
            print(f"[FAIL] Error during PATH restoration: {e}")

    # PRIVATE METHODS
    ########################################################
    # Internal methods for PATH operations

    def _backup_path(self) -> Dict:
        """Backup the current user PATH.

        Returns:
            Dictionary containing backup results
        """
        result = {
            "success": False,
            "target_path": str(self.target_path),
            "backup_location": str(self.backup_dir),
            "backup_files": [],
            "errors": [],
        }

        try:
            # Create backup directory if it doesn't exist
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # Get current PATH
            if self.platform == "Windows":
                # Use environment variable for Windows
                current_path = os.environ.get("PATH", "")
                if not current_path:
                    result["errors"].append(
                        "Failed to read Windows PATH from environment"
                    )
                    return result
            else:
                current_path = os.environ.get("PATH", "")

            # Create backup file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f".path_{timestamp}"

            with open(backup_file, "w", encoding="utf-8") as f:
                f.write(f"# WOMM PATH Backup - {timestamp}\n")
                f.write(f"# Platform: {self.platform}\n")
                f.write(f"# Target: {self.target_path}\n")
                f.write("# Original PATH:\n")
                f.write(f"{current_path}\n")

            # Update latest backup reference (copy instead of symlink for Windows compatibility)
            if self.latest_backup.exists():
                self.latest_backup.unlink()
            # Copy the backup file to .path (latest reference)
            shutil.copy2(backup_file, self.latest_backup)

            # Get list of all backup files
            backup_files = list(self.backup_dir.glob(".path_*"))
            result["backup_files"] = [
                str(f.name) for f in sorted(backup_files, reverse=True)
            ]
            result["success"] = True

            return result

        except Exception as e:
            result["errors"].append(f"Error creating PATH backup: {e}")
            return result

    def _list_backups(self) -> Dict:
        """List available PATH backups.

        Returns:
            Dictionary containing backup information
        """
        result = {
            "success": False,
            "target_path": str(self.target_path),
            "backup_location": str(self.backup_dir),
            "backups": [],
            "latest_backup": "",
            "errors": [],
        }

        try:
            if not self.backup_dir.exists():
                result["errors"].append("No backup directory found")
                return result

            # Get all backup files
            backup_files = list(self.backup_dir.glob(".path_*"))
            if not backup_files:
                result["errors"].append("No PATH backups found")
                return result

            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            for backup_file in backup_files:
                try:
                    stat = backup_file.stat()
                    with open(backup_file, encoding="utf-8") as f:
                        first_line = f.readline().strip()

                    backup_info = {
                        "name": backup_file.name,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                        "description": (
                            first_line
                            if first_line.startswith("#")
                            else "No description"
                        ),
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

        except Exception as e:
            result["errors"].append(f"Error listing backups: {e}")
            return result
