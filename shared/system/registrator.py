#!/usr/bin/env python3
"""
Enhanced Windows Context Menu Registrator for Works On My Machine.

This script provides advanced context menu management for Windows, with support for:
- Multiple script types (Python, PowerShell, Batch, Executable)
- Auto-detection of script type and appropriate execution
- Backup and restore functionality
- Integration with Works On My Machine system
- Robust validation and error handling

Usage:
    python registrator.py script_path "Action Title" [icon_path]
    python registrator.py --list
    python registrator.py --remove key_name
    python registrator.py --backup backup_file
    python registrator.py --restore backup_file
    python registrator.py --help
"""

import argparse
import json
import logging
import os
import shutil
import sys
import winreg
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple


class ScriptType:
    """Script type detection and configuration."""

    PYTHON = "python"
    POWERSHELL = "powershell"
    BATCH = "batch"
    EXECUTABLE = "executable"

    EXTENSIONS = {
        ".py": PYTHON,
        ".ps1": POWERSHELL,
        ".bat": BATCH,
        ".cmd": BATCH,
        ".exe": EXECUTABLE,
    }

    ICONS = {
        PYTHON: "C:\\Windows\\py.exe",
        POWERSHELL: "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
        BATCH: "C:\\Windows\\System32\\cmd.exe",
        EXECUTABLE: None,  # Use file's own icon
    }

    @classmethod
    def detect_type(cls, file_path: str) -> str:
        """Detect script type from file extension."""
        ext = Path(file_path).suffix.lower()
        return cls.EXTENSIONS.get(ext, cls.EXECUTABLE)

    @classmethod
    def get_default_icon(cls, script_type: str) -> Optional[str]:
        """Get default icon for script type."""
        return cls.ICONS.get(script_type)

    @classmethod
    def build_command(cls, script_type: str, script_path: str) -> str:
        """Build appropriate command for script type."""
        if script_type == cls.PYTHON:
            # Try to find Python executable
            python_exe = (
                shutil.which("python") or shutil.which("python3") or shutil.which("py")
            )
            if python_exe:
                return f'"{python_exe}" "{script_path}" "%V"'
            else:
                return f'py "{script_path}" "%V"'
        elif script_type == cls.POWERSHELL:
            return f'powershell.exe -ExecutionPolicy Bypass -File "{script_path}" "%V"'
        elif script_type == cls.BATCH:
            return f'cmd.exe /c "{script_path}" "%V"'
        elif script_type == cls.EXECUTABLE:
            return f'"{script_path}" "%V"'
        else:
            return f'"{script_path}" "%V"'


def generate_registry_key_name(file_path: str) -> str:
    """
    Generate registry key name from file path.

    Args:
        file_path: Path to script file

    Returns:
        Formatted registry key name
    """
    # Get filename without extension
    filename = Path(file_path).stem

    # Replace underscores with spaces and split
    filename = filename.replace("_", " ").replace("-", " ")
    parts = [p for p in filename.split(" ") if p]  # Remove empty parts

    # Convert to camelCase
    if parts:
        registry_key = parts[0].lower()
        for part in parts[1:]:
            if part:
                registry_key += part.capitalize()
    else:
        registry_key = "worksOnMyMachine"

    # Clean up
    registry_key = registry_key.strip().replace(" ", "")

    # Add prefix for Works On My Machine
    if not registry_key.startswith(("works", "dev")):
        registry_key = "wom" + registry_key.capitalize()

    return registry_key


def validate_script_path(script_path: str) -> Tuple[bool, str]:
    """
    Validate script path and provide feedback.

    Args:
        script_path: Path to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    path = Path(script_path)

    if not path.exists():
        return False, f"Script file does not exist: {script_path}"

    if not path.is_file():
        return False, f"Path is not a file: {script_path}"

    if not os.access(path, os.R_OK):
        return False, f"Script file is not readable: {script_path}"

    # Check if it's a supported type
    script_type = ScriptType.detect_type(script_path)
    if script_type == ScriptType.EXECUTABLE and not os.access(path, os.X_OK):
        return False, f"Executable file is not executable: {script_path}"

    return True, ""


def validate_icon_path(icon_path: str) -> str:
    """
    Validate and normalize icon path.

    Args:
        icon_path: Icon path or special value

    Returns:
        Normalized icon path
    """
    if icon_path.lower() in ["powershell", "ps"]:
        return "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe"
    elif icon_path.lower() in ["python", "py"]:
        return "C:\\Windows\\py.exe"
    elif icon_path.lower() in ["cmd", "batch"]:
        return "C:\\Windows\\System32\\cmd.exe"
    elif icon_path.lower() == "auto":
        return None  # Will be auto-detected
    else:
        return icon_path


def backup_registry_entries() -> Dict:
    """
    Backup current context menu entries.

    Returns:
        Dictionary containing backup data
    """
    backup_data = {
        "timestamp": datetime.now().isoformat(),
        "version": "1.0",
        "entries": [],
    }

    paths_to_backup = [
        "Software\\Classes\\Directory\\shell",
        "Software\\Classes\\Directory\\background\\shell",
    ]

    for base_path in paths_to_backup:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, base_path) as key:
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        entry_data = {
                            "base_path": base_path,
                            "key_name": subkey_name,
                            "properties": {},
                        }

                        # Read entry properties
                        try:
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                # Read MUIVerb
                                try:
                                    mui_verb, _ = winreg.QueryValueEx(subkey, "MUIVerb")
                                    entry_data["properties"]["MUIVerb"] = mui_verb
                                except FileNotFoundError:
                                    pass

                                # Read Icon
                                try:
                                    icon, _ = winreg.QueryValueEx(subkey, "Icon")
                                    entry_data["properties"]["Icon"] = icon
                                except FileNotFoundError:
                                    pass

                                # Read command
                                try:
                                    with winreg.OpenKey(subkey, "command") as cmd_key:
                                        command, _ = winreg.QueryValueEx(cmd_key, "")
                                        entry_data["properties"]["Command"] = command
                                except FileNotFoundError:
                                    pass
                        except Exception as e:
                            logging.debug(f"Failed to process registry entry: {e}")

                        backup_data["entries"].append(entry_data)
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            pass

    return backup_data


def save_backup(backup_data: Dict, backup_file: str) -> bool:
    """
    Save backup data to file.

    Args:
        backup_data: Backup data dictionary
        backup_file: Path to backup file

    Returns:
        True if successful
    """
    try:
        backup_path = Path(backup_file)
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Backup saved to: {backup_path}")
        print(f"📊 Entries backed up: {len(backup_data['entries'])}")
        return True
    except Exception as e:
        print(f"❌ Error saving backup: {e}")
        return False


def restore_from_backup(backup_file: str) -> bool:
    """
    Restore context menu entries from backup.

    Args:
        backup_file: Path to backup file

    Returns:
        True if successful
    """
    try:
        with open(backup_file, encoding="utf-8") as f:
            backup_data = json.load(f)

        print(f"🔄 Restoring from backup: {backup_file}")
        print(f"📅 Backup date: {backup_data.get('timestamp', 'Unknown')}")
        print(f"📊 Entries to restore: {len(backup_data['entries'])}")

        restored = 0
        for entry in backup_data["entries"]:
            try:
                base_path = entry["base_path"]
                key_name = entry["key_name"]
                properties = entry["properties"]

                reg_path = f"{base_path}\\{key_name}"

                # Create main key
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                    # Set properties
                    if "MUIVerb" in properties:
                        winreg.SetValueEx(
                            key, "MUIVerb", 0, winreg.REG_SZ, properties["MUIVerb"]
                        )
                    if "Icon" in properties:
                        winreg.SetValueEx(
                            key, "Icon", 0, winreg.REG_SZ, properties["Icon"]
                        )

                # Create command subkey
                if "Command" in properties:
                    command_path = f"{reg_path}\\command"
                    with winreg.CreateKey(
                        winreg.HKEY_CURRENT_USER, command_path
                    ) as cmd_key:
                        winreg.SetValueEx(
                            cmd_key, "", 0, winreg.REG_SZ, properties["Command"]
                        )

                restored += 1
                print(f"   ✓ Restored: {key_name}")

            except Exception as e:
                print(
                    f"   ❌ Failed to restore {entry.get('key_name', 'unknown')}: {e}"
                )

        print(f"✅ Restored {restored} entries successfully")
        return True

    except Exception as e:
        print(f"❌ Error restoring backup: {e}")
        return False


def add_context_menu_entry(
    reg_path: str, command: str, mui_verb: str, icon_path: str
) -> bool:
    """
    Add context menu entry to registry with enhanced error handling.

    Args:
        reg_path: Registry path
        command: Command to execute
        mui_verb: Text displayed in menu
        icon_path: Path to icon

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create main key
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
            # Set icon (only if provided)
            if icon_path:
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, icon_path)
            # Set display text
            winreg.SetValueEx(key, "MUIVerb", 0, winreg.REG_SZ, mui_verb)

        # Create command subkey
        command_path = f"{reg_path}\\command"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, command_path) as cmd_key:
            winreg.SetValueEx(cmd_key, "", 0, winreg.REG_SZ, command)

        return True

    except PermissionError:
        print(f"❌ Permission denied accessing registry: {reg_path}")
        print("💡 Try running as administrator")
        return False
    except Exception as e:
        print(f"❌ Error adding registry entry: {e}")
        return False


def remove_context_menu_entry(registry_key_name: str) -> bool:
    """
    Remove a context menu entry.

    Args:
        registry_key_name: Registry key name

    Returns:
        True if successful, False otherwise
    """
    try:
        paths_to_remove = [
            f"Software\\Classes\\Directory\\shell\\{registry_key_name}",
            f"Software\\Classes\\Directory\\background\\shell\\{registry_key_name}",
        ]

        for path in paths_to_remove:
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, f"{path}\\command")
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, path)
                print(f"✅ Removed: {path}")
            except FileNotFoundError:
                pass  # Key doesn't exist, that's normal
            except Exception as e:
                print(f"⚠️  Error removing {path}: {e}")

        return True

    except Exception as e:
        print(f"❌ Error during removal: {e}")
        return False


def list_context_menu_entries() -> None:
    """List and display existing context menu entries."""
    try:
        paths_to_check = [
            "Software\\Classes\\Directory\\shell",
            "Software\\Classes\\Directory\\background\\shell",
        ]

        print("📋 Existing context menu entries:")

        for base_path in paths_to_check:
            print(f"\n📁 {base_path}:")
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, base_path) as key:
                    i = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, i)

                            # Try to read details
                            try:
                                with winreg.OpenKey(key, subkey_name) as subkey:
                                    try:
                                        mui_verb, _ = winreg.QueryValueEx(
                                            subkey, "MUIVerb"
                                        )
                                        print(f"   ✓ {subkey_name} - {mui_verb}")
                                    except FileNotFoundError:
                                        print(f"   • {subkey_name}")
                            except Exception:
                                print(f"   • {subkey_name}")

                            i += 1
                        except OSError:
                            break

            except FileNotFoundError:
                print("   (no entries)")

    except Exception as e:
        print(f"❌ Error listing entries: {e}")


def main():
    """Enhanced main function with new features."""
    parser = argparse.ArgumentParser(
        description="Enhanced Windows Context Menu Registrator for Works On My Machine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a script to context menu (auto-detection)
  python registrator.py "C:\\tools\\my_script.py" "My Python Action"

  # Add with custom icon
  python registrator.py "C:\\tools\\script.ps1" "PowerShell Action" "powershell"

  # Add batch file with auto icon
  python registrator.py "C:\\tools\\deploy.bat" "Deploy Project" "auto"

  # List existing entries
  python registrator.py --list

  # Remove an entry
  python registrator.py --remove womMyScript

  # Backup context menu entries
  python registrator.py --backup "backup.json"

  # Restore from backup
  python registrator.py --restore "backup.json"
        """,
    )

    # Positional arguments for adding entries
    parser.add_argument(
        "script_path", nargs="?", help="Full path to script or executable"
    )
    parser.add_argument("mui_verb", nargs="?", help="Action title for context menu")
    parser.add_argument(
        "icon_input",
        nargs="?",
        default="auto",
        help="Icon path, or 'auto', 'powershell', 'python', 'cmd' (default: auto)",
    )

    # Action arguments
    parser.add_argument(
        "--list", action="store_true", help="List existing context menu entries"
    )
    parser.add_argument(
        "--remove", metavar="KEY_NAME", help="Remove context menu entry by key name"
    )
    parser.add_argument(
        "--backup", metavar="BACKUP_FILE", help="Backup context menu entries to file"
    )
    parser.add_argument(
        "--restore",
        metavar="BACKUP_FILE",
        help="Restore context menu entries from backup file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    # Check Windows OS
    if os.name != "nt":
        print("❌ This script only works on Windows")
        return 1

    # Backup mode
    if args.backup:
        print("📦 Creating backup of context menu entries...")
        backup_data = backup_registry_entries()
        return 0 if save_backup(backup_data, args.backup) else 1

    # Restore mode
    if args.restore:
        if not Path(args.restore).exists():
            print(f"❌ Backup file not found: {args.restore}")
            return 1
        return 0 if restore_from_backup(args.restore) else 1

    # List mode
    if args.list:
        list_context_menu_entries()
        return 0

    # Remove mode
    if args.remove:
        if args.dry_run:
            print(f"🔍 Would remove context menu entry: {args.remove}")
            return 0
        success = remove_context_menu_entry(args.remove)
        return 0 if success else 1

    # Add mode - validate arguments
    if not args.script_path or not args.mui_verb:
        print("❌ Missing arguments for adding entry")
        print("Usage: python registrator.py <script_path> <action_title> [icon_path]")
        print("Use --help for more information")
        return 1

    # Validate script path
    is_valid, error_msg = validate_script_path(args.script_path)
    if not is_valid:
        print(f"❌ {error_msg}")
        return 1

    # Auto-detect script type
    script_type = ScriptType.detect_type(args.script_path)

    # Determine icon path
    icon_path = validate_icon_path(args.icon_input)
    if icon_path is None:  # Auto-detection
        icon_path = ScriptType.get_default_icon(script_type)

    # Validate icon if provided
    if icon_path and not Path(icon_path).exists():
        print(f"⚠️  Icon not found: {icon_path}")
        icon_path = ScriptType.get_default_icon(script_type)
        if icon_path:
            print(f"💡 Using default icon for {script_type}: {icon_path}")

    # Generate registry key name
    registry_key_name = generate_registry_key_name(args.script_path)

    # Create registry paths
    reg_path_file = f"Software\\Classes\\Directory\\shell\\{registry_key_name}"
    reg_path_directory = (
        f"Software\\Classes\\Directory\\background\\shell\\{registry_key_name}"
    )

    # Build appropriate command for script type
    command = ScriptType.build_command(script_type, args.script_path)

    print("🔧 Adding to Windows Context Menu")
    print(f"📜 Script: {args.script_path}")
    print(f"🎯 Type: {script_type}")
    print(f"🏷️  Title: {args.mui_verb}")
    print(f"🎨 Icon: {icon_path or 'Default file icon'}")
    print(f"🔑 Registry Key: {registry_key_name}")
    print(f"⚡ Command: {command}")

    if args.dry_run:
        print("\n🔍 Dry run mode - no changes made")
        print("✅ Configuration validated successfully")
        return 0

    # Add entries
    print("\n📝 Adding registry entries...")
    success_file = add_context_menu_entry(
        reg_path_file, command, args.mui_verb, icon_path
    )
    success_dir = add_context_menu_entry(
        reg_path_directory, command, args.mui_verb, icon_path
    )

    if success_file and success_dir:
        print(f"\n✅ Context menu added successfully as '{registry_key_name}'!")
        print("💡 Entries will appear in folder and background context menus")
        print(f"📋 To remove later: python registrator.py --remove {registry_key_name}")
        return 0
    else:
        print("\n❌ Error adding context menu entries")
        return 1


if __name__ == "__main__":
    sys.exit(main())
