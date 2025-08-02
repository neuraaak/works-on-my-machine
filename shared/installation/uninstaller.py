#!/usr/bin/env python3
"""
Uninstaller for Works On My Machine.
Removes WOMM from the system and cleans up PATH entries.
"""

import argparse
import platform
import shutil
import sys
import winreg
from pathlib import Path

# Import CLI manager
try:
    from shared.core.cli_manager import run_command, run_silent
except ImportError:
    # Fallback if module not available
    import subprocess

    def run_command(cmd, desc, **kwargs):
        """Run a command with logging."""
        print(f"\n🔍 {desc}...")
        print(f"Command: {' '.join(cmd)}")

        # Security validation
        if SECURITY_AVAILABLE:
            validator = SecurityValidator()
            is_valid, error_msg = validator.validate_command(cmd)
            if not is_valid:
                print(f"   ⚠️  Security validation failed: {error_msg}")
                return type("obj", (object,), {"success": False})()

        result = subprocess.run(cmd, **kwargs)  # noqa: S603
        return type("obj", (object,), {"success": result.returncode == 0})()

    def run_silent(cmd, **kwargs):
        """Run a command silently."""
        # Security validation
        if SECURITY_AVAILABLE:
            validator = SecurityValidator()
            is_valid, error_msg = validator.validate_command(cmd)
            if not is_valid:
                print(f"   ⚠️  Security validation failed: {error_msg}")
                return type("obj", (object,), {"success": False})()

        return subprocess.run(cmd, capture_output=True, **kwargs)  # noqa: S603


# Import security validator if available
try:
    from shared.security.security_validator import SecurityValidator

    SECURITY_AVAILABLE = True
except ImportError:
    SECURITY_AVAILABLE = False


def get_target_womm_path() -> Path:
    """Get the standard target path for Works On My Machine."""
    return Path.home() / ".womm"


def remove_from_windows_path(bin_path: Path) -> bool:
    """Remove WOMM bin directory from Windows PATH."""
    try:
        print("🔧 Removing from Windows PATH...")

        # Get current PATH from registry
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_READ | winreg.KEY_WRITE,
        )

        try:
            path_value, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            print("   ⚠️  PATH not found in registry")
            return True

        # Remove WOMM bin path
        bin_path_str = str(bin_path)
        path_parts = path_value.split(";")

        if bin_path_str in path_parts:
            path_parts.remove(bin_path_str)
            new_path = ";".join(path_parts)

            # Update registry
            winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
            print(f"   ✓ Removed {bin_path_str} from PATH")
        else:
            print(f"   ℹ️  {bin_path_str} not found in PATH")

        winreg.CloseKey(key)
        return True

    except Exception as e:
        print(f"   ❌ Error updating Windows PATH: {e}")
        return False


def remove_from_unix_path(bin_path: Path) -> bool:
    """Remove WOMM bin directory from Unix PATH."""
    try:
        print("🔧 Removing from Unix PATH...")

        # Common shell config files
        shell_files = [
            Path.home() / ".bashrc",
            Path.home() / ".bash_profile",
            Path.home() / ".zshrc",
            Path.home() / ".profile",
        ]

        bin_path_str = str(bin_path)
        removed = False

        for shell_file in shell_files:
            if shell_file.exists():
                content = shell_file.read_text()

                # Look for PATH export lines containing WOMM
                lines = content.split("\n")
                new_lines = []

                for line in lines:
                    path_patterns = [
                        f'export PATH="{bin_path_str}:$PATH"',
                        f'export PATH=$PATH:"{bin_path_str}"',
                        "export PATH=" + bin_path_str + ":$PATH",
                        "export PATH=$PATH:" + bin_path_str,
                    ]
                    if any(pattern in line for pattern in path_patterns):
                        print(f"   ✓ Removed PATH entry from {shell_file.name}")
                        removed = True
                    else:
                        new_lines.append(line)

                if removed:
                    shell_file.write_text("\n".join(new_lines))

        if not removed:
            print(f"   ℹ️  {bin_path_str} not found in shell config files")

        return True

    except Exception as e:
        print(f"   ❌ Error updating Unix PATH: {e}")
        return False


def remove_context_menu() -> bool:
    """Remove WOMM tools from Windows context menu."""
    if platform.system() != "Windows":
        return True

    try:
        print("🔧 Removing Windows context menu entries...")

        # Use the existing unregister script
        unregister_script = Path(__file__).parent / "system" / "register_wom_tools.py"

        if unregister_script.exists():
            result = run_silent(
                [sys.executable, str(unregister_script), "--unregister"]
            )

            if result.returncode == 0:
                print("   ✓ Context menu entries removed")
                return True
            else:
                print("   ⚠️  Error removing context menu entries")
                return False
        else:
            print("   ℹ️  Context menu unregister script not found")
            return True

    except Exception as e:
        print(f"   ❌ Error removing context menu: {e}")
        return False


def remove_womm_directory(target_path: Path) -> bool:
    """Remove the WOMM directory."""
    try:
        print(f"🗑️  Removing WOMM directory: {target_path}")

        if target_path.exists():
            shutil.rmtree(target_path)
            print("   ✓ WOMM directory removed")
            return True
        else:
            print("   ℹ️  WOMM directory not found")
            return True

    except Exception as e:
        print(f"   ❌ Error removing WOMM directory: {e}")
        return False


def main():
    """Run the uninstallation process."""
    parser = argparse.ArgumentParser(description="Uninstall Works On My Machine")
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force uninstallation without confirmation",
    )
    parser.add_argument(
        "--target", type=str, help="Custom target directory (default: ~/.womm)"
    )

    args = parser.parse_args()

    print("🗑️  WOMM Uninstaller")
    print("=" * 50)

    # Determine target path
    if args.target:
        target_path = Path(args.target).expanduser().resolve()
    else:
        target_path = get_target_womm_path()

    print(f"🎯 Target: {target_path}")

    # Check if WOMM is installed
    if not target_path.exists():
        print("❌ Works On My Machine is not installed at the specified location")
        return 1

    # Confirmation
    if not args.force:
        print("\n⚠️  This will completely remove Works On My Machine from:")
        print(f"   - Directory: {target_path}")
        print("   - System PATH")
        print("   - Windows context menu (if applicable)")

        response = input("\n🤔 Are you sure you want to continue? (y/N): ").lower()
        if response not in ["y", "yes", "o", "oui"]:
            print("⏭️  Uninstallation cancelled")
            return 0

    # Start uninstallation
    print("\n🚀 Starting uninstallation...")

    success = True

    # 1. Remove from PATH
    bin_path = target_path / "bin"
    if platform.system() == "Windows":
        if not remove_from_windows_path(bin_path):
            success = False
    else:
        if not remove_from_unix_path(bin_path):
            success = False

    # 2. Remove context menu entries
    if not remove_context_menu():
        success = False

    # 3. Remove WOMM directory
    if not remove_womm_directory(target_path):
        success = False

    # Final status
    if success:
        print("\n✅ Uninstallation completed successfully!")
        print(
            "💡 You may need to restart your terminal for PATH changes to take effect"
        )
    else:
        print("\n❌ Uninstallation completed with errors")
        print("💡 Some components may need manual removal")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
