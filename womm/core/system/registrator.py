#!/usr/bin/env python3
"""
Standalone registrator script for WOMM context menu management.

This script is called by 'womm context' commands to manage Windows context menus.
It uses the utility functions from registrator_utils but provides the CLI interface.
"""

import argparse
import sys
from pathlib import Path

# Add the WOMM module to the Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from womm.core.utils.system.registrator_utils import (
    ScriptType,
    add_context_menu_entry,
    backup_registry_entries,
    generate_registry_key_name,
    list_context_menu_entries,
    remove_context_menu_entry,
    restore_from_backup,
    save_backup,
    validate_icon_path,
    validate_script_path,
)


def main():
    """Main entry point for the standalone registrator script."""
    parser = argparse.ArgumentParser(
        description="Windows Context Menu Registrator for Works On My Machine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Add a script to context menu
    python registrator.py "C:\\tools\\my_script.py" "My Python Action"

    # Add with custom icon
    python registrator.py "C:\\tools\\script.ps1" "PowerShell Action" "powershell"

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
    import os

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
        print("❌ Error adding context menu entries")
        return 1


if __name__ == "__main__":
    sys.exit(main())
