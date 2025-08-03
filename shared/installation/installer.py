#!/usr/bin/env python3
"""
Install Works On My Machine in user directory.

This script handles the installation of WOMM to the user's home directory,
including PATH setup, prerequisites installation, and Windows context menu integration.
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Import CLI manager
try:
    from shared.core.cli_manager import run_command, run_interactive, run_silent

    # Import security modules if available
    try:
        from shared.security.security_validator import security_validator

        SECURITY_AVAILABLE = True
    except ImportError:
        SECURITY_AVAILABLE = False
except ImportError:
    # Fallback if module not available during first installation
    subprocess_run = subprocess.run

    def run_command(cmd, desc, **kwargs):
        """Run a command with logging.

        Args:
            cmd: Command to run as list of strings.
            desc: Description of the command for logging.
            **kwargs: Additional arguments passed to subprocess.run.

        Returns:
            Object with success attribute indicating if command succeeded.
        """
        print(f"\n🔍 {desc}...")
        print(f"Command: {' '.join(cmd)}")
        result = subprocess_run(cmd, **kwargs)
        return type("obj", (object,), {"success": result.returncode == 0})()

    def run_silent(cmd, **kwargs):
        """Run a command silently.

        Args:
            cmd: Command to run as list of strings.
            **kwargs: Additional arguments passed to subprocess.run.

        Returns:
            CompletedProcess object from subprocess.run.
        """
        return subprocess_run(cmd, capture_output=True, **kwargs)

    def run_interactive(cmd, **kwargs):
        """Run a command interactively.

        Args:
            cmd: Command to run as list of strings.
            **kwargs: Additional arguments passed to subprocess.run.

        Returns:
            CompletedProcess object from subprocess.run.
        """
        return subprocess_run(cmd, **kwargs)


def get_target_womm_path():
    """Get the standard target path for Works On My Machine.

    Returns:
        Path object pointing to the .womm directory in user's home.
    """
    return Path.home() / ".womm"


def get_current_womm_path():
    """Get the current script path.

    Returns:
        Path object pointing to the directory containing this script.
    """
    # Go up from shared/installation/installer.py to the project root
    return Path(__file__).parent.parent.parent.absolute()


def should_exclude_file(file_path: Path, source_path: Path) -> bool:
    """Check if a file should be excluded from installation.

    Args:
        file_path: Path to the file relative to source
        source_path: Source directory path

    Returns:
        True if file should be excluded, False otherwise
    """
    # Convert to relative path for easier checking
    rel_path = file_path.relative_to(source_path)
    rel_str = str(rel_path).replace("\\", "/")  # Normalize separators

    # Exclusions based on .gitignore patterns
    gitignore_patterns = [
        # Python
        "__pycache__/",
        "*.py[cod]",
        "*.so",
        ".Python",
        "build/",
        "develop-eggs/",
        "dist/",
        "downloads/",
        "eggs/",
        ".eggs/",
        "lib/",
        "lib64/",
        "parts/",
        "sdist/",
        "var/",
        "wheels/",
        "share/python-wheels/",
        "*.egg-info/",
        ".installed.cfg",
        "*.egg",
        "MANIFEST",
        # Virtual environments
        ".venv/",
        "env/",
        "venv/",
        "ENV/",
        "env.bak/",
        "venv.bak/",
        ".conda/",
        # Testing
        ".pytest_cache/",
        ".coverage",
        "coverage.xml",
        "htmlcov/",
        ".tox/",
        ".cache",
        "nosetests.xml",
        "*.cover",
        "*.py,cover",
        ".hypothesis/",
        ".nox/",
        # Development Tools
        ".mypy_cache/",
        ".ruff_cache/",
        ".bandit/",
        ".pre-commit-cache/",
        ".benchmarks/",
        # Editors and IDEs
        ".cursor/",
        ".idea/",
        "*.swp",
        "*.swo",
        "*~",
        # OS
        "Thumbs.db",
        "ehthumbs.db",
        "Desktop.ini",
        "$RECYCLE.BIN/",
        ".DS_Store",
        ".DS_Store?",
        "._*",
        ".AppleDouble",
        ".LSOverride",
        ".directory",
        ".Trash-*",
        # Logs and temporary data
        "*.log",
        "*.pid",
        "*.tmp",
        "*.temp",
        "_temp/",
        # Sensitive files
        ".env",
        ".env.*",
        ".env.local",
        ".env.*.local",
        ".secret*",
        "*password*",
        "*secret*",
        "*.key",
        "*.pem",
        "*.crt",
        "credentials/",
        "keys/",
        # Backup et archives
        "*.bak",
        "*.backup",
        "*.orig",
        "*.rej",
        # Specific to works-on-my-machine project
        "/.womm",
        "test_output/",
        "temp_projects/",
        "works-on-my-machine-temp/",
        "*.backup/",
        "local_config/",
        "user_settings/",
        ".pip-cache/",
        "node_modules/",
        ".npm/",
        ".yarn/",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".Python",
    ]

    # Check gitignore patterns
    for pattern in gitignore_patterns:
        if pattern.endswith("/"):
            # Directory pattern
            if rel_str.startswith(pattern) or f"/{pattern}" in f"/{rel_str}":
                return True
        elif pattern.startswith("*"):
            # Wildcard pattern
            if rel_str.endswith(pattern[1:]) or pattern[1:] in rel_str:
                return True
        else:
            # Exact match
            if rel_str == pattern or rel_str.endswith(f"/{pattern}"):
                return True

    # Additional exclusions for active development files
    active_dev_files = [
        ".git/",
        ".gitignore",
        "cspell.json",  # Active configuration
        "pyproject.toml",  # Active configuration
        "setup.py",  # Active configuration
        "Makefile",  # Active configuration
        "lint.py",  # Active development script
        "run_tests.py",  # Active development script
        "init.py",  # Active development script
        "init.bat",  # Active development script
        "init.ps1",  # Active development script
        "DOCUMENTATION_RULES.md",  # Development documentation
        "coverage.xml",  # Test results
        # Note: womm.py is NOT excluded - it's needed for the CLI to work
    ]

    for pattern in active_dev_files:
        if pattern.endswith("/"):
            if rel_str.startswith(pattern):
                return True
        else:
            if rel_str == pattern:
                return True

    return False


def copy_womm_to_user_directory():
    """Copy Works On My Machine to %USER%/.womm.

    Returns:
        Path object pointing to the new location of Works On My Machine.
    """
    source = get_current_womm_path()
    target = get_target_womm_path()

    # Security validation for target path
    if SECURITY_AVAILABLE:
        is_valid, error = security_validator.validate_path(target)
        if not is_valid:
            print(f"❌ Invalid target path: {error}")
            return None

    print(f"[COPY] Copying from: {source}")
    print(f"[COPY] To: {target}")

    # Save old version if exists
    if target.exists():
        backup = target.with_suffix(".backup")
        if backup.exists():
            try:
                shutil.rmtree(backup)
            except Exception as e:
                print(f"[WARN] Could not remove existing backup: {e}")

        print(f"[BACKUP] Backing up old version to: {backup}")
        try:
            target.rename(backup)
        except PermissionError:
            print(
                "[WARN] Could not rename existing directory (in use), removing directly..."
            )
            try:
                shutil.rmtree(target)
            except Exception as e:
                print(f"[ERROR] Could not remove existing directory: {e}")
                print(
                    "[INFO] Please close any applications using the directory and try again"
                )
                return None

    # Copy with exclusions
    def ignore_files(dir_path, files):
        """Filter function for shutil.copytree."""
        ignored = []
        for file in files:
            file_path = Path(dir_path) / file
            if should_exclude_file(file_path, source):
                ignored.append(file)
                print(f"[EXCLUDE] {file_path.relative_to(source)}")
        return ignored

    # Copy
    shutil.copytree(source, target, ignore=ignore_files)
    print("[SUCCESS] Copy completed")

    return target


def backup_user_path(target_path: Path) -> bool:
    """Backup the current USER PATH to a .backup directory (never system PATH).

    Args:
        target_path: The target WOMM directory where to create the backup

    Returns:
        True if backup was successful, False otherwise
    """
    print("[BACKUP] Creating USER PATH backup (safe mode)...")

    try:
        # Create .backup directory
        backup_dir = target_path / ".backup"
        backup_dir.mkdir(exist_ok=True)

        # Get current USER PATH based on platform (never system PATH)
        current_path = ""
        if platform.system() == "Windows":
            try:
                # IMPORTANT: Only read USER PATH (HKCU), never system PATH
                result = run_silent(["reg", "query", "HKCU\\Environment", "/v", "PATH"])
                if result.returncode == 0:
                    # Handle both bytes and string output
                    if isinstance(result.stdout, bytes):
                        output = result.stdout.decode("utf-8", errors="ignore")
                    else:
                        output = result.stdout

                    for line in output.split("\n"):
                        if "PATH" in line and "REG_EXPAND_SZ" in line:
                            current_path = line.split("REG_EXPAND_SZ")[1].strip()
                            break
            except Exception as e:
                print(f"[WARN] Could not read Windows USER PATH: {e}")
                # Fallback to environment variable (user context only)
                current_path = os.environ.get("PATH", "")
        else:
            # Unix-like systems - user PATH only
            current_path = os.environ.get("PATH", "")

        # Create backup file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f".path_{timestamp}"

        # Write USER PATH to backup file
        with open(backup_file, "w", encoding="utf-8") as f:
            f.write(f"# USER PATH backup created on {datetime.now().isoformat()}\n")
            f.write(f"# Platform: {platform.system()}\n")
            f.write("# Security: USER PATH only (system PATH never touched)\n")
            f.write("# Original USER PATH:\n")
            f.write(current_path)

        print(f"[SUCCESS] USER PATH backup created: {backup_file}")
        print("[SECURITY] Only user PATH backed up (system PATH untouched)")

        # Also create a symlink to the latest backup
        latest_backup = backup_dir / ".path"
        if latest_backup.exists():
            latest_backup.unlink()
        latest_backup.symlink_to(backup_file.name)

        return True

    except Exception as e:
        print(f"[ERROR] Failed to create USER PATH backup: {e}")
        return False


def restore_user_path(target_path: Path) -> bool:
    """Restore the user PATH from backup.

    Args:
        target_path: The WOMM directory containing the backup

    Returns:
        True if restore was successful, False otherwise
    """
    print("[RESTORE] Restoring PATH from backup...")

    try:
        backup_dir = target_path / ".backup"
        latest_backup = backup_dir / ".path"

        if not latest_backup.exists():
            print("[ERROR] No PATH backup found")
            return False

        # Read the backup file
        with open(latest_backup, encoding="utf-8") as f:
            lines = f.readlines()

        # Extract the original PATH (skip comment lines)
        original_path = ""
        for line in lines:
            if not line.startswith("#") and line.strip():
                original_path = line.strip()
                break

        if not original_path:
            print("[ERROR] No valid PATH found in backup")
            return False

        # Resolve environment variables in the PATH
        try:
            import os

            resolved_path = os.path.expandvars(original_path)
            print(f"[INFO] Resolved PATH: {resolved_path}")
        except Exception as e:
            print(f"[WARN] Could not resolve environment variables: {e}")
            resolved_path = original_path

        # Restore PATH based on platform
        if platform.system() == "Windows":
            try:
                # IMPORTANT: Only restore USER PATH (HKCU), never system PATH
                result = run_command(
                    [
                        "reg",
                        "add",
                        "HKCU\\Environment",
                        "/v",
                        "PATH",
                        "/t",
                        "REG_EXPAND_SZ",
                        "/d",
                        resolved_path,
                        "/f",
                    ],
                    "Restoring Windows USER PATH (safe mode)",
                    capture_output=True,
                    text=True,
                )

                if result.success:
                    print("[SUCCESS] Windows USER PATH restored successfully")
                    print("[SECURITY] Only user PATH restored (system PATH untouched)")
                    print("[INFO] Restart your terminal to apply changes")
                    return True
                else:
                    print("[ERROR] Failed to restore Windows USER PATH")
                    return False

            except Exception as e:
                print(f"[ERROR] Error restoring Windows USER PATH: {e}")
                return False
        else:
            # For Unix-like systems, we can't easily restore to system PATH
            # but we can provide instructions
            print("[INFO] For Unix-like systems, manual PATH restoration required")
            print(f"[INFO] Original PATH was: {original_path}")
            print("[INFO] Please manually update your shell profile file")
            return False

    except Exception as e:
        print(f"[ERROR] Failed to restore PATH: {e}")
        return False


def setup_path():
    """Set up PATH environment variable."""
    womm_path = get_target_womm_path()

    if platform.system() == "Windows":
        setup_windows_path(womm_path)
    else:
        setup_unix_path(womm_path)


def setup_windows_path(womm_path):
    """Set up PATH for Windows (USER PATH ONLY - never system PATH)."""
    print("[PATH] Setting up Windows USER PATH (safe mode)...")

    # Get current USER PATH from registry (HKCU = Current User only)
    try:
        result = run_silent(["reg", "query", "HKCU\\Environment", "/v", "PATH"])
        if result.returncode == 0:
            # Parse current PATH
            if isinstance(result.stdout, bytes):
                output = result.stdout.decode("utf-8", errors="ignore")
            else:
                output = result.stdout
            for line in output.split("\n"):
                if "PATH" in line and "REG_EXPAND_SZ" in line:
                    current_path = line.split("REG_EXPAND_SZ")[1].strip()
                    break
            else:
                current_path = ""
        else:
            current_path = ""
    except Exception:
        current_path = ""

    # Check if our path is already in PATH
    if str(womm_path) not in current_path:
        try:
            # IMPORTANT: Add WOMM path to the END of current PATH
            # Format: current_path;%USERPROFILE%\.womm
            new_path = f"{current_path};{womm_path}" if current_path else str(womm_path)

            # IMPORTANT: Use setx without /M flag to modify USER PATH only
            # /M flag would modify SYSTEM PATH which we want to avoid for security
            result = run_command(
                [
                    "setx",
                    "PATH",
                    new_path,
                ],
                "Setting Windows USER PATH (safe mode)",
                capture_output=True,
                text=True,
            )

            if result.success:
                print("[SUCCESS] Windows USER PATH updated successfully")
                print("[SECURITY] Only user PATH modified (system PATH untouched)")
                print(f"[INFO] Added {womm_path} to USER PATH")
                print(
                    "[INFO] Restart your terminal or run 'refreshenv' to apply changes"
                )
            else:
                print("[WARN] Failed to update Windows USER PATH automatically")
                print("[INFO] You can add it manually (USER PATH only):")
                print(f'   setx PATH "%PATH%;{womm_path}"')
        except Exception as e:
            print(f"[ERROR] Error updating Windows USER PATH: {e}")
            print("[INFO] You can add it manually (USER PATH only):")
            print(f'   setx PATH "%PATH%;{womm_path}"')
    else:
        print("[SUCCESS] USER PATH already configured")


def setup_unix_path(womm_path):
    """Set up PATH for Unix-like systems."""
    print("[PATH] Setting up Unix PATH...")

    # Determine shell profile file
    shell = os.environ.get("SHELL", "")
    home = Path.home()

    if "zsh" in shell:
        profile_file = home / ".zshrc"
    elif "bash" in shell:
        profile_file = home / ".bashrc"
    else:
        profile_file = home / ".profile"

    # Check if our path is already in profile
    if profile_file.exists():
        with open(profile_file, encoding="utf-8") as f:
            content = f.read()
    else:
        content = ""

    path_line = f'export PATH="$PATH:{womm_path}"'
    if path_line not in content:
        # Add to profile
        with open(profile_file, "a", encoding="utf-8") as f:
            f.write(f'\n# Works On My Machine\nexport PATH="$PATH:{womm_path}"\n')

        print(f"✅ Added to {profile_file}")
        print("🔄 Restart your terminal or run 'source ~/.bashrc' to apply changes")
    else:
        print("✅ PATH already configured")


def create_womm_executable():
    """Create the main womm executable for Windows."""
    if platform.system() == "Windows":
        womm_path = get_target_womm_path()
        womm_bat = womm_path / "womm.bat"

        womm_bat_content = """@echo off
REM Works On My Machine - Main CLI Entry Point
REM This file allows running 'womm' from anywhere once ~/.womm is in PATH

python "%~dp0womm.py" %*
"""
        womm_bat.write_text(womm_bat_content, encoding="utf-8")
        print(f"[BAT] Created main womm.bat: {womm_bat}")
    else:
        # Create Unix executable for womm command
        womm_path = get_target_womm_path()
        womm_exec = womm_path / "womm"

        womm_exec_content = """#!/usr/bin/env python3
# Works On My Machine - Main CLI Entry Point
# This file allows running 'womm' from anywhere once ~/.womm is in PATH

import sys
from pathlib import Path

# Add the womm package to the path
womm_path = Path(__file__).parent
sys.path.insert(0, str(womm_path))

# Import and run the CLI
from womm.cli import womm

if __name__ == "__main__":
    womm()
"""
        womm_exec.write_text(womm_exec_content, encoding="utf-8")
        womm_exec.chmod(0o755)  # Make executable
        print(f"[EXEC] Created Unix womm executable: {womm_exec}")


def check_and_install_prerequisites() -> bool:
    """Check and install prerequisites if needed."""
    try:
        from shared.installation.prerequisite_installer import PrerequisiteInstaller

        installer = PrerequisiteInstaller()
        should_install, missing, custom_path = installer.prompt_installation()

        if should_install and missing:
            return installer.install_missing_prerequisites(missing, custom_path)
        elif not missing:
            print("[SUCCESS] All prerequisites are already installed!")
            return True
        else:
            print("⏭️  Installation cancelled by user")
            return False

    except ImportError:
        print("[WARN] Prerequisites installer not available")
        return True

    except Exception as e:
        print(f"[ERROR] Error checking prerequisites: {e}")
        return True


def main():
    """Run the installation process.

    Installs WOMM to user directory, sets up PATH, and configures the environment.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Install Works On My Machine")
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force installation even if .womm directory exists",
    )
    parser.add_argument(
        "--no-prerequisites",
        action="store_true",
        help="Skip prerequisites installation",
    )
    parser.add_argument(
        "--no-context-menu",
        action="store_true",
        help="Skip Windows context menu integration",
    )
    parser.add_argument(
        "--target", type=str, help="Custom target directory (default: ~/.womm)"
    )

    args = parser.parse_args()

    print("[INSTALL] Installing Works On My Machine")
    print("=" * 50)

    # Use custom target if specified
    if args.target:
        global get_target_womm_path
        custom_target = Path(args.target).expanduser().resolve()

        def get_target_womm_path():
            return custom_target

    current_path = get_current_womm_path()
    target_path = get_target_womm_path()

    print(f"[INFO] Current location: {current_path}")
    print(f"[INFO] Target location: {target_path}")

    # Check if target directory already exists
    if target_path.exists() and not args.force:
        print(f"[WARN] Directory {target_path} already exists")
        response = input("Do you want to continue and overwrite it? (y/N): ").lower()
        if response not in ["y", "yes", "o", "oui"]:
            print("[INFO] Installation cancelled")
            return

    # Copy WOMM to target directory
    if current_path != target_path:
        print("[COPY] Copying WOMM to target directory...")
        copy_womm_to_user_directory()

    # Backup current user PATH before modification
    if not backup_user_path(target_path):
        print("[WARN] PATH backup failed, but continuing with installation...")

    # Prerequisites check removed - dependencies will be checked when needed
    # This allows for faster installation and just-in-time dependency management

    # Normal configuration
    create_womm_executable()
    setup_path()

    print("\n[SUCCESS] Installation complete!")
    print("[INFO] Commands available after terminal restart:")
    print("  - womm")
    print("  - womm install")
    print("  - womm uninstall")
    print("  - womm new python")
    print("  - womm new javascript")
    print("  - womm lint")
    print("  - womm spell")
    print("  - womm system")

    # Offer to add to Windows context menu
    if platform.system() == "Windows" and not args.no_context_menu:
        print("\n[WINDOWS] Windows System Integration")
        try:
            response = input(
                "Do you want to add Works On My Machine to the context menu? (y/N): "
            ).lower()
        except (EOFError, KeyboardInterrupt):
            print("[INFO] Using default: No context menu integration")
            response = "n"
        if response in ["o", "oui", "y", "yes"]:
            try:
                register_script = (
                    target_path / "shared" / "system" / "register_wom_tools.py"
                )
                if register_script.exists():
                    print("[REGISTER] Adding to Windows context menu...")
                    result = run_command(
                        [
                            sys.executable,
                            str(register_script),
                            "--register",
                            "--no-backup",
                        ],
                        "Registering context menu",
                    )

                    if result.success:
                        print("[SUCCESS] Works On My Machine added to context menu!")
                        print("[INFO] Right-click on a folder to see WOMM options")
                    else:
                        print("[WARN] Error adding to context menu")
                        print("[INFO] You can do it manually later with:")
                        print("   womm context register")
                else:
                    print("[WARN] Registry script not found")
            except Exception as e:
                print(f"[ERROR] Error adding to context menu: {e}")
        else:
            print("[INFO] You can add WOMM to the context menu later with:")
            print("   womm context register")

    # OS-specific instructions
    if platform.system() == "Windows":
        print("\n[INFO] To use immediately (without restart):")
        print(f"    set PATH=%PATH%;{target_path}")
        print("    womm --help")
    else:
        print("\n💡 To use immediately (without restart):")
        print(f'    export PATH="$PATH:{target_path}"')
        print("    womm --help")


if __name__ == "__main__":
    main()
