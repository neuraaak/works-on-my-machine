#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Works On My Machine - Auto-registration of tools to Windows context menu.

This script automatically registers commonly used Works On My Machine tools
to the Windows context menu for easy access from any folder.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from system.registrator import (
        ScriptType,
        add_context_menu_entry,
        backup_registry_entries,
        generate_registry_key_name,
        list_context_menu_entries,
        save_backup,
        validate_script_path,
    )
except ImportError:
    # Fallback si l'import échoue
    ScriptType = None
    add_context_menu_entry = None
    backup_registry_entries = None
    generate_registry_key_name = None
    list_context_menu_entries = None
    save_backup = None
    validate_script_path = None


class WOMRegistrator:
    """Works On My Machine tools registrator."""

    def __init__(self):
        """Initialize the WOM registrator.

        Args:
            wom_root (Path): Path to Works On My Machine root folder.
            backup_dir (Path): Path to backup folder.
            tools_config (List[Dict]): Configuration of tools to register.

        Returns:
            None
        """
        self.wom_root = Path(__file__).parent.parent.parent
        self.backup_dir = self.wom_root / ".backups"
        self.tools_config = self._get_tools_config()

    def _get_tools_config(self) -> List[Dict]:
        """Get configuration for WOM tools to register.

        Returns:
            List[Dict]: Configuration of tools to register.
        """
        tools = [
            {
                "script": self.wom_root / "womm.py",
                "title": "🛠️ Install Works On My Machine",
                "icon": "python",
                "description": "Install WOMM in current directory",
            },
            {
                "script": self.wom_root / "shared" / "project_detector.py",
                "title": "🔍 Detect Project Type",
                "icon": "python",
                "description": "Auto-detect and setup project",
            },
            {
                "script": self.wom_root / "shared" / "environment_manager.py",
                "title": "⚙️ Setup Dev Environment",
                "icon": "python",
                "description": "Configure development environment",
            },
            {
                "script": self.wom_root / "shared" / "prerequisite_installer.py",
                "title": "📦 Install Prerequisites",
                "icon": "python",
                "description": "Install required development tools",
            },
            {
                "script": self.wom_root / "shared" / "vscode_config.py",
                "title": "🔧 Configure VSCode",
                "icon": "python",
                "description": "Setup VSCode for development",
            },
            {
                "script": self.wom_root / "shared" / "cspell_manager.py",
                "title": "📝 Spell Check Project",
                "icon": "python",
                "description": "Check spelling in project files",
            },
        ]

        # Filter to only existing scripts
        return [tool for tool in tools if tool["script"].exists()]

    def create_backup(self) -> bool:
        """Create backup before registration."""
        try:
            from datetime import datetime

            self.backup_dir.mkdir(exist_ok=True)
            backup_file = (
                self.backup_dir
                / f"context_menu_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

            print("📦 Creating backup before registration...")
            backup_data = backup_registry_entries()
            return save_backup(backup_data, str(backup_file))
        except Exception as e:
            print(f"⚠️  Could not create backup: {e}")
            return False

    def register_tools(self, create_backup: bool = True) -> bool:
        """Register all WOM tools to context menu."""
        if create_backup:
            self.create_backup()

        print("🔧 Registering Works On My Machine tools to context menu...")
        print(f"📁 WOM Root: {self.wom_root}")
        print(f"📊 Tools to register: {len(self.tools_config)}")

        success_count = 0

        for tool in self.tools_config:
            script_path = str(tool["script"])
            title = tool["title"]
            icon = tool["icon"]

            print(f"\n📜 Registering: {title}")
            print(f"   Script: {script_path}")

            # Validate script
            is_valid, error_msg = validate_script_path(script_path)
            if not is_valid:
                print(f"   ❌ {error_msg}")
                continue

            # Generate registry key
            registry_key = generate_registry_key_name(script_path)

            # Get icon path
            script_type = ScriptType.detect_type(script_path)
            if icon == "auto":
                icon_path = ScriptType.get_default_icon(script_type)
            else:
                icon_path = (
                    ScriptType.get_default_icon(icon)
                    if icon in ScriptType.ICONS
                    else icon
                )

            # Build command
            command = ScriptType.build_command(script_type, script_path)

            # Create registry paths
            reg_path_file = f"Software\\Classes\\Directory\\shell\\{registry_key}"
            reg_path_directory = (
                f"Software\\Classes\\Directory\\background\\shell\\{registry_key}"
            )

            # Add entries
            success_file = add_context_menu_entry(
                reg_path_file, command, title, icon_path
            )
            success_dir = add_context_menu_entry(
                reg_path_directory, command, title, icon_path
            )

            if success_file and success_dir:
                print(f"   ✅ Registered as: {registry_key}")
                success_count += 1
            else:
                print("   ❌ Failed to register")

        print(
            f"\n✅ Successfully registered {success_count}/{len(self.tools_config)} tools"
        )

        if success_count > 0:
            print("\n💡 Tools are now available in folder context menus!")
            print("📋 Right-click on any folder to see Works On My Machine options")

        return success_count > 0

    def unregister_tools(self) -> bool:
        """Remove all WOM tools from context menu."""
        print("🗑️  Removing Works On My Machine tools from context menu...")

        from system.registrator import remove_context_menu_entry

        success_count = 0

        for tool in self.tools_config:
            script_path = str(tool["script"])
            registry_key = generate_registry_key_name(script_path)

            print(f"🗑️  Removing: {registry_key}")
            if remove_context_menu_entry(registry_key):
                success_count += 1

        print(f"✅ Removed {success_count}/{len(self.tools_config)} tools")
        return success_count > 0

    def show_registered_tools(self):
        """Show currently registered WOM tools."""
        print("📋 Works On My Machine tools in context menu:")

        registered_keys = set()
        for tool in self.tools_config:
            registry_key = generate_registry_key_name(str(tool["script"]))
            registered_keys.add(registry_key)

        # List all entries and highlight WOM ones
        list_context_menu_entries()

        print(f"\n🎯 Expected WOM tools: {', '.join(registered_keys)}")


def main():
    """Execute the main entry point of the script.

    Returns:
        int: Exit code.
    """
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(
        description="Register Works On My Machine tools to Windows context menu",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Register all WOM tools
  python register_wom_tools.py --register

  # Remove all WOM tools
  python register_wom_tools.py --unregister

  # Show registered tools
  python register_wom_tools.py --list

  # Register without backup
  python register_wom_tools.py --register --no-backup
        """,
    )

    parser.add_argument(
        "--register", action="store_true", help="Register WOM tools to context menu"
    )
    parser.add_argument(
        "--unregister", action="store_true", help="Remove WOM tools from context menu"
    )
    parser.add_argument("--list", action="store_true", help="Show registered WOM tools")
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup creation (not recommended)",
    )

    args = parser.parse_args()

    # Check Windows OS
    if os.name != "nt":
        print("❌ This script only works on Windows")
        return 1

    registrator = WOMRegistrator()

    if args.register:
        success = registrator.register_tools(create_backup=not args.no_backup)
        return 0 if success else 1
    elif args.unregister:
        success = registrator.unregister_tools()
        return 0 if success else 1
    elif args.list:
        registrator.show_registered_tools()
        return 0
    else:
        print("❌ No action specified. Use --register, --unregister, or --list")
        print("Use --help for more information")
        return 1


if __name__ == "__main__":
    sys.exit(main())
