#!/usr/bin/env python3
"""
Context menu commands for WOMM CLI.
Handles Windows context menu management.
"""

# IMPORTS
########################################################
# External modules and dependencies

import platform
import sys
from datetime import datetime
from pathlib import Path

import click

# IMPORTS
########################################################
# Internal modules and dependencies
from rich import print

from ..core.installation.installer import get_target_womm_path
from ..core.ui.console import (
    LogLevel,
    print_error,
    print_info,
    print_pattern,
    print_success,
    print_system,
)
from ..core.ui.interactive import InteractiveMenu
from ..core.ui.panels import create_panel
from ..core.ui.progress import create_spinner_with_status
from ..core.ui.prompts import confirm, prompt_choice
from ..core.utils.cli_manager import run_command
from ..utils.path_resolver import resolve_script_path

# UTILITY FUNCTIONS
########################################################
# Helper functions and utilities


def _check_windows_only() -> bool:
    """Check if running on Windows and display appropriate message."""
    if platform.system().lower() != "windows":
        print_info("Context menu management is Windows-specific")
        print_info("Consider using symbolic links or aliases on Unix systems")
        return False
    return True


def _execute_registrator_command(
    cmd: list,
    description: str,
    dry_run: bool = False,
    verbose: bool = False,
    show_output: bool = False,
) -> bool:
    """Execute registrator command with consistent UI feedback and error handling."""
    if dry_run:
        print_info(f"Dry run: {' '.join(map(str, cmd))}")
        return True

    if verbose:
        print_system(f"Executing: {' '.join(map(str, cmd))}")

    if show_output:
        # For commands like list/status that need to show output, use subprocess directly
        import subprocess

        try:
            result = subprocess.run(cmd, cwd=None, check=False)  # noqa: S603
            success = result.returncode == 0
        except Exception as e:
            print_error(f"Failed to execute command: {e}")
            return False
    else:
        # For commands like register/unregister, use spinner
        with create_spinner_with_status(f"Running {description}...") as (
            progress,
            task,
        ):
            progress.update(task, status=f"Executing {description}...")
            result = run_command(cmd, description)
            success = result.success

    if success:
        if not show_output:  # Only show success message if output wasn't already shown
            print_success(f"{description} completed successfully")
        return True
    else:
        if not show_output:
            print_error(f"{description} failed")
        return False


def _get_python_executable() -> str:
    """Get the appropriate Python executable for WOMM operations.

    Uses the global Python installation (from PATH) that the user has
    on their system, whether installed manually or via WOMM.
    """
    import shutil

    # Try different Python executables in order of preference
    python_candidates = ["python", "python3", "py"]

    for candidate in python_candidates:
        python_exe = shutil.which(candidate)
        if python_exe:
            return python_exe

    # Last resort fallback to the current Python executable
    return sys.executable


def _get_registrator_script_path():
    """Get the path to the registrator script."""
    # Try to find it in the installed WOMM directory first
    try:
        womm_path = get_target_womm_path()
        if womm_path.exists():
            installed_registrator = (
                womm_path / "womm" / "core" / "system" / "registrator.py"
            )
            if installed_registrator.exists():
                return str(installed_registrator)
    except Exception as e:
        print_pattern(
            LogLevel.DEBUG,
            "SYSTEM",
            f"Could not access installed WOMM registrator: {e}",
        )

    # Fallback to development path
    return resolve_script_path("womm/core/system/registrator.py")


def _get_backup_directory() -> str:
    """Get the appropriate directory for backups."""
    try:
        womm_path = get_target_womm_path()
        if womm_path.exists():
            backup_dir = womm_path / ".backup" / "context_menu"
            backup_dir.mkdir(parents=True, exist_ok=True)
            return str(backup_dir)
    except Exception as e:
        print_pattern(
            LogLevel.DEBUG, "SYSTEM", f"Could not access WOMM backup directory: {e}"
        )

    # Fallback to current directory
    return "."


def _generate_backup_filenames(backup_dir: str) -> tuple[str, str]:
    """Generate timestamped and latest backup filenames."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    platform_name = platform.system()

    # Timestamped backup file
    timestamped_file = (
        f"{backup_dir}/context_menu_backup_{platform_name}_{timestamp}.json"
    )

    # Latest backup file (without timestamp)
    latest_file = f"{backup_dir}/context_menu_backup_{platform_name}.json"

    return timestamped_file, latest_file


def _execute_backup_with_timestamp(
    python_exe: str, script_path: str, backup_dir: str, dry_run: bool, verbose: bool
) -> tuple[bool, str]:
    """Execute backup with timestamped filename and create latest copy."""
    import shutil

    # Generate filenames
    timestamped_file, latest_file = _generate_backup_filenames(backup_dir)

    # Execute backup to timestamped file
    backup_cmd = [python_exe, str(script_path), "--backup", timestamped_file]
    success = _execute_registrator_command(
        backup_cmd, "Context menu backup", dry_run, verbose
    )

    if success and not dry_run:
        # Copy timestamped backup to latest backup file
        try:
            shutil.copy2(timestamped_file, latest_file)
            print_pattern(
                LogLevel.DEBUG,
                "SYSTEM",
                f"Created latest backup reference: {latest_file}",
            )
        except Exception as e:
            print_pattern(
                LogLevel.DEBUG, "SYSTEM", f"Could not create latest backup copy: {e}"
            )

    return success, timestamped_file


def _get_default_target() -> str:
    """Get the default target path for context menu registration."""
    import os

    try:
        # Try to find womm in PATH, but prefer installed version over dev version
        womm_candidates = []
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)

        for path_dir in path_dirs:
            womm_bat = Path(path_dir) / "womm.bat"
            if womm_bat.exists():
                womm_candidates.append(str(womm_bat))

        # Prefer the one in user directory over development directory
        womm_exe = None
        for candidate in womm_candidates:
            if ".womm" in candidate and "Users" in candidate:
                womm_exe = candidate
                break

        # If no user installation found, use first candidate
        if not womm_exe and womm_candidates:
            womm_exe = womm_candidates[0]

        if womm_exe:
            print_pattern(LogLevel.DEBUG, "SYSTEM", f"Found WOMM in PATH: {womm_exe}")
            # Get the WOMM installation directory from the executable path
            womm_install_path = Path(womm_exe).parent
            # Create backup directory within the installation
            backup_dir = womm_install_path / ".backup" / "context_menu"
            backup_dir.mkdir(parents=True, exist_ok=True)
            return str(backup_dir)

        # Fallback to get_target_womm_path if womm not in PATH
        womm_path = get_target_womm_path()
        backup_dir = womm_path / ".backup" / "context_menu"
        backup_dir.mkdir(parents=True, exist_ok=True)
        return str(backup_dir)

    except Exception as e:
        print_pattern(LogLevel.DEBUG, "SYSTEM", f"Could not create default target: {e}")
        # Final fallback to current directory
        return "."


def _show_tip_panel(content: str, title: str = "Tip"):
    """Show a tip panel with consistent formatting."""
    tip_panel = create_panel(
        content,
        title=title,
        border_style="yellow",
        style="bright_yellow",
        padding=(1, 1),
        width=80,
    )
    print("")
    print(tip_panel)
    print("")


# MAIN FUNCTIONS
########################################################
# Core CLI functionality and command groups


@click.group()
def context_group():
    """Windows context menu management."""


# COMMAND FUNCTIONS
########################################################
# Command implementations


@context_group.command("register")
@click.option(
    "--target",
    "target_path",
    type=click.Path(),
    default=None,
    help="Script or executable to register in context menu (default: backup directory)",
)
@click.option("--label", required=True, help="Label to display in context menu")
@click.option(
    "--registrator-args",
    multiple=True,
    help="Extra args passed to registrator (e.g., shell type, icon)",
)
@click.option("--dry-run", is_flag=True, help="Show command without executing")
@click.option("--verbose", is_flag=True, help="Verbose mode")
def context_register(target_path, label, registrator_args, dry_run, verbose):
    """📝 Register WOMM tools in Windows context menu."""
    if not _check_windows_only():
        return

    # Use default target if none provided
    if target_path is None:
        target_path = _get_default_target()
        print_info(f"Using default target: {target_path}")

    python_exe = _get_python_executable()
    script_path = _get_registrator_script_path()

    # Always create backup before registration
    backup_dir = _get_backup_directory()

    with create_spinner_with_status("Creating backup before registration...") as (
        progress,
        task,
    ):
        progress.update(task, status="Creating backup...")
        success, backup_file = _execute_backup_with_timestamp(
            python_exe, script_path, backup_dir, dry_run, verbose
        )
    if not success:
        print_error("Backup failed, aborting registration")
        return

    # Build registrator command: python registrator.py <target> <label> [extra]
    cmd = [python_exe, str(script_path), str(target_path), str(label)]
    for extra in registrator_args:
        cmd.extend(extra.split())

    # Execute registration
    success = _execute_registrator_command(
        cmd, "Context menu registration", dry_run, verbose
    )

    if success and not dry_run:
        print_success(f"Tool '{label}' registered successfully in context menu")

        # Show helpful tip panel
        tip_content = """Right-click in any folder to see your new context menu entry.

• The entry will appear in both folder and background context menus
• Use 'womm context list' to see all registered entries
• Use 'womm context unregister --remove <key>' to remove entries later"""

        _show_tip_panel(tip_content, "Context Menu Usage")

    elif not success:
        print_error("Registration failed - check the error details above")


@context_group.command("unregister")
@click.option(
    "--remove",
    "remove_key",
    required=True,
    help="Key name to remove (as stored in registry)",
)
@click.option("--dry-run", is_flag=True, help="Show command without executing")
@click.option("--verbose", is_flag=True, help="Verbose mode")
def context_unregister(remove_key, dry_run, verbose):
    """🗑️ Unregister WOMM tools from Windows context menu."""
    if not _check_windows_only():
        return

    python_exe = _get_python_executable()
    script_path = _get_registrator_script_path()
    cmd = [python_exe, str(script_path), "--remove", str(remove_key)]

    # Execute unregistration
    success = _execute_registrator_command(
        cmd, "Context menu unregistration", dry_run, verbose
    )

    if success and not dry_run:
        print_success(f"Entry '{remove_key}' removed successfully from context menu")

        # Show helpful tip panel
        tip_content = """Context menu entry has been removed successfully.

• Changes will be visible after refreshing File Explorer
• Use 'womm context list' to verify the removal
• Use 'womm context register' to add new entries"""

        _show_tip_panel(tip_content, "Unregistration Complete")

    elif not success:
        print_error("Unregistration failed - check the error details above")


@context_group.command("list")
@click.option("--dry-run", is_flag=True, help="Show command without executing")
@click.option("--verbose", is_flag=True, help="Verbose mode")
def context_list(dry_run, verbose):
    """📋 List registered context menu entries."""
    if not _check_windows_only():
        return

    python_exe = _get_python_executable()
    script_path = _get_registrator_script_path()
    cmd = [python_exe, str(script_path), "--list"]

    # Execute list command - show output since this is an informational command
    success = _execute_registrator_command(
        cmd, "Context menu listing", dry_run, verbose, show_output=True
    )

    if success and not dry_run:
        # Show helpful tip panel
        tip_content = """Context menu management commands:

• womm context register --target <file> --label "<name>" - Add new entry
• womm context unregister --remove <key> - Remove existing entry
• womm context quick-setup - Setup common WOMM tools
• womm context status - Check current registration status"""

        _show_tip_panel(tip_content, "Context Menu Commands")

    elif not success:
        print_error("Failed to retrieve context menu entries")


@context_group.command("quick-setup")
@click.option("--dry-run", is_flag=True, help="Show commands without executing")
@click.option("--verbose", is_flag=True, help="Verbose mode")
def context_quick_setup(dry_run, verbose):
    """⚡ Quick setup common WOMM tools in context menu."""
    if not _check_windows_only():
        return

    # Common WOMM tools to register
    tools = [
        {
            "target": "womm.py",
            "label": "WOMM CLI",
            "description": "Main WOMM command-line interface",
        },
        # Add more tools as needed
    ]

    script_path = _get_registrator_script_path()
    success_count = 0
    total_tools = len(tools)

    with create_spinner_with_status("Setting up common WOMM tools...") as (
        progress,
        task,
    ):
        for i, tool in enumerate(tools, 1):
            progress.update(
                task, status=f"Registering {tool['description']} ({i}/{total_tools})..."
            )
            if verbose:
                print_info(f"Registering: {tool['description']}")
            cmd = [sys.executable, str(script_path), tool["target"], tool["label"]]

            success = _execute_registrator_command(
                cmd, f"Register {tool['label']}", dry_run, verbose
            )

            if success:
                success_count += 1

    if not dry_run:
        if success_count == total_tools:
            print_success(f"All {total_tools} WOMM tools registered successfully!")
            print_info("Right-click in any folder to access WOMM tools")
        else:
            print_info(f"Registered {success_count}/{total_tools} tools successfully")


@context_group.command("status")
def context_status():
    """📊 Show context menu registration status (Windows only)."""
    if not _check_windows_only():
        return

    python_exe = _get_python_executable()
    script_path = _get_registrator_script_path()
    cmd = [python_exe, str(script_path), "--list"]

    # Execute status check - show output since this displays current status
    with create_spinner_with_status("Checking context menu registration status...") as (
        progress,
        task,
    ):
        progress.update(task, status="Retrieving context menu entries...")
        success = _execute_registrator_command(
            cmd, "Context menu status check", show_output=True
        )

    if success:
        # Show helpful information panel
        info_content = """Context menu status information:

• Entries with descriptions are managed by external tools
• Entries without descriptions are system defaults or unmanaged
• All entries are shown for both folder and background context menus
• Backup files are stored in your WOMM installation directory"""

        _show_tip_panel(info_content, "Status Information")

    else:
        print_error("Failed to retrieve context menu status")

        # Show troubleshooting panel
        troubleshoot_content = """Troubleshooting context menu issues:

• Ensure you have administrator privileges
• Check if Windows Registry access is blocked
• Try running from an elevated command prompt
• Verify WOMM installation is complete"""

        _show_tip_panel(troubleshoot_content, "Troubleshooting")


@context_group.command("backup")
@click.option(
    "--output", "-o", help="Custom backup file path (default: auto-generated)"
)
@click.option("--dry-run", is_flag=True, help="Show command without executing")
@click.option("--verbose", is_flag=True, help="Verbose mode")
def context_backup(output, dry_run, verbose):
    """💾 Create backup of current context menu entries."""
    if not _check_windows_only():
        return

    python_exe = _get_python_executable()
    script_path = _get_registrator_script_path()

    # Determine backup file path
    if output:
        # Custom output path - use as is without timestamp
        backup_file = output
        print_info(f"Backup location: {backup_file}")

        # Build backup command
        cmd = [python_exe, str(script_path), "--backup", backup_file]

        # Execute backup with spinner
        with create_spinner_with_status("Creating context menu backup...") as (
            progress,
            task,
        ):
            progress.update(task, status="Creating backup...")
            success = _execute_registrator_command(
                cmd, "Context menu backup", dry_run, verbose
            )

        if success and not dry_run:
            print_success("Context menu backup created successfully!")
            print_info(f"📄 Backup saved to: {backup_file}")
    else:
        # Auto-generated path with timestamp
        backup_dir = _get_backup_directory()
        print_info("Creating backup of context menu entries...")

        success, backup_file = _execute_backup_with_timestamp(
            python_exe, script_path, backup_dir, dry_run, verbose
        )

        if success and not dry_run:
            print_success("Context menu backup created successfully!")
            print_info(f"Timestamped backup: {backup_file}")

            # Show latest backup info
            _, latest_file = _generate_backup_filenames(backup_dir)
            print_info(f"Latest backup: {latest_file}")

    if success and not dry_run:
        # Show helpful tip panel
        tip_content = f"""Context menu backup completed successfully.

• Backup file: {backup_file}
• Use this backup to restore context menu entries if needed
• The backup includes all current registry entries for context menus
• You can specify a custom backup location with --output"""

        _show_tip_panel(tip_content, "Backup Information")

    elif not success:
        print_error("Backup failed - check the error details above")


@context_group.command("restore")
@click.option(
    "--backup-file",
    "-f",
    help="Specific backup file to restore (default: interactive selection)",
)
@click.option("--dry-run", is_flag=True, help="Show command without executing")
@click.option("--verbose", is_flag=True, help="Verbose mode")
def context_restore(backup_file, dry_run, verbose):
    """🔄 Restore context menu entries from backup."""
    if not _check_windows_only():
        return

    import json
    from datetime import datetime

    python_exe = _get_python_executable()
    script_path = _get_registrator_script_path()
    backup_dir = _get_backup_directory()

    # If specific backup file provided, use it
    if backup_file:
        backup_path = Path(backup_file)
        if not backup_path.exists():
            print_error(f"Backup file not found: {backup_file}")
            return
        selected_file = backup_path
    else:
        # Interactive selection from available backups
        backup_files = list(Path(backup_dir).glob("context_menu_backup_*.json"))
        if not backup_files:
            print_error("No context menu backups found")
            print_info(f"Checked directory: {backup_dir}")
            return

        # Sort by modification time (newest first)
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        print_info("Available context menu backups:")
        print("")

        # Display backup options
        for i, file in enumerate(backup_files, 1):
            try:
                stat = file.stat()
                modified_date = datetime.fromtimestamp(stat.st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                size_kb = stat.st_size / 1024

                # Try to read backup info
                try:
                    with open(file, encoding="utf-8") as f:
                        data = json.load(f)
                    entry_count = len(data.get("entries", []))
                    info = f" ({entry_count} entries)"
                except Exception:
                    info = ""

                print_info(f"  {i}. {file.name}")
                print_info(f"     📅 {modified_date} | 📦 {size_kb:.1f} KB{info}")

            except Exception as e:
                print_pattern(
                    LogLevel.DEBUG, "SYSTEM", f"Error reading backup {file.name}: {e}"
                )
                continue

        print("")

        # Create backup file choices
        backup_choices = []
        for file in backup_files:
            try:
                size_kb = file.stat().st_size / 1024
                modified_date = datetime.fromtimestamp(file.stat().st_mtime).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                # Try to read entry count from backup
                info = ""
                try:
                    with open(file, encoding="utf-8") as f:
                        data = json.load(f)
                    entry_count = len(data.get("entries", []))
                    info = f" ({entry_count} entries)"
                except Exception:
                    info = ""

                choice_text = (
                    f"{file.name} - 📅 {modified_date} | 📦 {size_kb:.1f} KB{info}"
                )
                backup_choices.append(choice_text)

            except Exception as e:
                print_pattern(
                    LogLevel.DEBUG, "SYSTEM", f"Error reading backup {file.name}: {e}"
                )
                continue

        # Show selection menu
        try:
            selected_choice = prompt_choice(
                "Choose a backup to restore:", backup_choices
            )

            # Find the corresponding file
            selected_index = backup_choices.index(selected_choice)
            selected_file = backup_files[selected_index]

        except (KeyboardInterrupt, ValueError):
            print_info("📤 Restore cancelled")
            return

    # Confirm restore operation
    print_info(f"Selected backup: {selected_file.name}")

    # Ask for confirmation
    if not confirm(
        "This will overwrite current context menu entries. Proceed?", default=False
    ):
        print_info("Restore cancelled")
        return

    # Execute restore with spinner
    cmd = [python_exe, str(script_path), "--restore", str(selected_file)]

    with create_spinner_with_status("Restoring context menu from backup...") as (
        progress,
        task,
    ):
        progress.update(task, status="Restoring from backup...")
        success = _execute_registrator_command(
            cmd, "Context menu restore", dry_run, verbose
        )

    if success and not dry_run:
        print_success("Context menu restored successfully!")
        print_info(f"Restored from: {selected_file.name}")

        # Show helpful tip panel
        tip_content = f"""Context menu restore completed successfully.

• Restored from: {selected_file.name}
• All context menu entries have been restored from the backup
• Changes should be visible immediately in File Explorer
• Use 'womm context list' to verify the restored entries"""

        _show_tip_panel(tip_content, "Restore Complete")

    elif not success:
        print_error("Restore failed - check the error details above")


@context_group.command("cherry-pick")
@click.option("--dry-run", is_flag=True, help="Show changes without executing")
@click.option("--verbose", is_flag=True, help="Verbose mode")
def context_cherry_pick(dry_run, verbose):
    """🍒 Cherry-pick specific context menu entries from backups."""
    if not _check_windows_only():
        return

    try:
        # Get backup directory and scan for backups
        backup_dir = Path(_get_backup_directory())
        if not backup_dir.exists():
            print_error("No backup directory found")
            print_info("Create a backup first using 'womm context register'")
            return

        # Collect all entries from all backups
        with create_spinner_with_status("Scanning backup files...") as (progress, task):
            progress.update(task, status="Collecting context menu entries...")
            all_entries = _collect_all_entries_from_backups(backup_dir, verbose)
        if not all_entries:
            print_error("No context menu entries found in backups")
            return

        # Get currently installed entries for comparison
        current_entries = _get_current_context_entries(verbose)

        # Filter out already installed entries
        available_entries = _filter_available_entries(all_entries, current_entries)
        if not available_entries:
            print_info("All context menu entries from backups are already installed")
            return

        # Show selection menu
        selected_entries = _show_cherry_pick_menu(available_entries)
        if not selected_entries:
            print_info("Cherry-pick cancelled")
            return

        # Apply selected entries
        _apply_cherry_picked_entries(selected_entries, dry_run, verbose)

    except Exception as e:
        print_error(f"Cherry-pick failed: {e}")
        if verbose:
            import traceback

            traceback.print_exc()


def _collect_all_entries_from_backups(backup_dir: Path, verbose: bool) -> list:
    """Collect and deduplicate all context menu entries from backup files."""
    import json

    all_entries = {}  # Using dict to automatically deduplicate by key_name
    backup_files = sorted(backup_dir.glob("context_menu_backup_*.json"))

    if verbose:
        print_info(f"Scanning {len(backup_files)} backup files...")

    for backup_file in backup_files:
        try:
            with open(backup_file, encoding="utf-8") as f:
                data = json.load(f)

            entries = data.get("entries", [])
            for entry in entries:
                key_name = entry.get("key_name")
                if key_name and key_name not in all_entries:
                    # Add metadata about source backup
                    entry["_source_backup"] = backup_file.name
                    entry["_display_name"] = _format_entry_display_name(entry)
                    all_entries[key_name] = entry

        except Exception as e:
            if verbose:
                print_pattern(
                    LogLevel.DEBUG, "SYSTEM", f"Error reading {backup_file.name}: {e}"
                )

    if verbose:
        print_info(f"Found {len(all_entries)} unique context menu entries")

    return list(all_entries.values())


def _format_entry_display_name(entry: dict) -> str:
    """Format entry for display in selection menu."""
    key_name = entry.get("key_name", "Unknown")
    properties = entry.get("properties", {})

    # Try to get a user-friendly name
    display_text = properties.get("MUIVerb") or properties.get("@", key_name)

    # Get command info for context
    command = properties.get("Command", "")
    if command:
        # Extract executable name from command
        import re

        exe_match = re.search(r'"([^"]*\.exe)"', command)
        if exe_match:
            exe_name = Path(exe_match.group(1)).name
            display_text = f"{display_text} ({exe_name})"

    return f"{display_text} [key: {key_name}]"


def _get_current_context_entries(verbose: bool) -> set:
    """Get currently installed context menu entries."""
    python_exe = _get_python_executable()
    script_path = _get_registrator_script_path()

    cmd = [python_exe, str(script_path), "--list"]

    if verbose:
        print_info("Checking currently installed context menu entries...")

    try:
        import subprocess

        result = subprocess.run(  # noqa: S603
            cmd,
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="ignore",
        )  # noqa: S603

        # Parse the output to extract key names
        current_keys = set()
        for line in result.stdout.splitlines():
            if "Key:" in line:
                key_match = line.split("Key:")[-1].strip()
                if key_match:
                    current_keys.add(key_match)

        if verbose:
            print_info(f"Found {len(current_keys)} currently installed entries")

        return current_keys

    except Exception as e:
        if verbose:
            print_pattern(
                LogLevel.DEBUG, "SYSTEM", f"Error checking current entries: {e}"
            )
        return set()


def _filter_available_entries(all_entries: list, current_entries: set) -> list:
    """Filter out entries that are already installed."""
    available = []
    for entry in all_entries:
        key_name = entry.get("key_name")
        if key_name and key_name not in current_entries:
            available.append(entry)
    return available


def _show_cherry_pick_menu(available_entries: list) -> list:
    """Show interactive menu for selecting entries to install."""
    print_info("Select context menu entries to install:")

    # Create interactive menu
    menu = InteractiveMenu(
        title="Cherry-pick Context Menu Entries",
        instruction="Use space to select/deselect, enter to confirm, q to quit",
    )

    # Format entries for display
    def format_entry(entry):
        return entry["_display_name"]

    # Show multi-selection menu
    selected = menu.select_multiple_from_list(
        available_entries, display_func=format_entry
    )

    return selected if selected else []


def _apply_cherry_picked_entries(selected_entries: list, dry_run: bool, verbose: bool):
    """Apply the selected context menu entries."""
    python_exe = _get_python_executable()
    script_path = _get_registrator_script_path()

    with create_spinner_with_status(
        f"Applying {len(selected_entries)} selected entries..."
    ) as (progress, task):
        for i, entry in enumerate(selected_entries, 1):
            key_name = entry.get("key_name")
            properties = entry.get("properties", {})
            source_backup = entry.get("_source_backup", "unknown")

            # Extract command and other properties
            command = properties.get("Command", "")
            muiverb = properties.get("MUIVerb")
            icon = properties.get("Icon")

            if not command:
                print_pattern(
                    LogLevel.WARNING, "SYSTEM", f"Skipping {key_name}: no command found"
                )
                continue

            progress.update(
                task, status=f"Installing {key_name} ({i}/{len(selected_entries)})..."
            )
            if verbose:
                print_info(f"[{i}/{len(selected_entries)}] Installing: {key_name}")
                print_info(f"   Source: {source_backup}")
                print_info(f"   Command: {command}")

            # Build registrator command
            cmd = [python_exe, str(script_path)]

            # Extract script path from command (simplified approach)
            if '"' in command:
                script_match = command.split('"')[1]
                if script_match:
                    cmd.extend([script_match, muiverb or key_name])

                    # Add icon if present
                    if icon:
                        cmd.append(icon)

            # Execute command
            if dry_run:
                print_info(f"Dry run: {' '.join(cmd)}")
            else:
                success = _execute_registrator_command(
                    cmd, f"Installing {key_name}", dry_run=False, verbose=verbose
                )

                if success:
                    print_success(f"Installed: {key_name}")
                else:
                    print_error(f"Failed to install: {key_name}")

    if not dry_run:
        print_success(
            f"Cherry-pick completed! {len(selected_entries)} entries installed"
        )

        # Show tip panel
        tip_content = f"""Cherry-pick installation completed successfully.

• {len(selected_entries)} context menu entries installed
• Changes should be visible immediately in File Explorer
• Use 'womm context list' to verify the new entries
• If an entry doesn't work, check the original script path"""

        _show_tip_panel(tip_content, "Cherry-pick Complete")
