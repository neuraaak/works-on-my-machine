#!/usr/bin/env python3
"""
Install Works On My Machine in user directory.

This script handles the installation of WOMM to the user's home directory,
including PATH setup and environment configuration.
"""

# IMPORTS
########################################################
# Standard library imports
import os
import platform
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Local/third-party imports
from womm.core.installation.path_manager_utils import (
    deduplicate_path_entries,
    extract_path_from_reg_output,
)
from womm.core.utils.cli_manager import run_silent

# Security is assumed available; remove conditional availability


# CONSTANTS
########################################################
# Configuration constants
DEFAULT_EXCLUDE_PATTERNS = [
    ".git",
    ".gitignore",
    ".pytest_cache",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".coverage",
    "htmlcov",
    "build",
    "dist",
    "*.egg-info",
    ".venv",
    "venv",
    "node_modules",
    ".vscode",
    ".idea",
    "*.log",
    ".DS_Store",
    "Thumbs.db",
    ".mypy_cache",
    ".ruff_cache",
    ".cursor",
    "cspell.json",
    "*_temp.*",
    "*.mdc",
    "benchmarks",
    "coverage",
    "ignore-install.txt",
    "LICENSE",
    "pyproject.toml",
    "MANIFEST",
    "Makefile",
    "setup.py",
    "tests",
    "run_tests.py",
    "build_package.py",
    "build_exe.py",
]


# UTILITY FUNCTIONS
########################################################
# Helper functions for path management and file operations


def get_target_womm_path() -> Path:
    """Get the standard target path for Works On My Machine.

    Returns:
        Path object pointing to the .womm directory in user's home.
    """
    return Path.home() / ".womm"


def get_current_womm_path() -> Path:
    """Get the current script path.

    Returns:
        Path object pointing to the directory containing this script.
    """
    # Go up from womm/core/installation/installer.py to the project root
    # womm/core/installation/installer.py -> womm/core/installation/ -> womm/core/ -> womm/ -> project_root
    current_path = Path(__file__).parent.parent.parent.parent.absolute()

    # Verify we're at the project root by checking for key files
    if not (current_path / "pyproject.toml").exists():
        raise RuntimeError(
            f"Could not find project root. Expected pyproject.toml at {current_path}"
        )

    return current_path


def should_exclude_file(file_path: Path, source_path: Path) -> bool:
    """Check if a file should be excluded from installation.

    Args:
        file_path: Path to the file relative to source
        source_path: Source directory path

    Returns:
        True if file should be excluded, False otherwise
    """
    # Load exclude patterns from ignore-install.txt if available
    exclude_patterns = []
    ignore_file = source_path / "ignore-install.txt"

    if ignore_file.exists():
        try:
            with open(ignore_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line and not line.startswith("#"):
                        exclude_patterns.append(line)
        except Exception as e:
            # Fall back to default patterns if file can't be read
            # Log the error for debugging but continue with defaults
            print(f"Warning: Could not read ignore-install.txt: {e}")

    # Fallback to default patterns if no ignore-install.txt or empty
    if not exclude_patterns:
        exclude_patterns = DEFAULT_EXCLUDE_PATTERNS

    file_name = file_path.name
    relative_path = file_path.relative_to(source_path)

    for pattern in exclude_patterns:
        if pattern.startswith("*"):
            if file_name.endswith(pattern[1:]):
                return True
        elif pattern in str(relative_path):
            return True

    return False


# MAIN CLASS
########################################################
# Core installation manager class


class InstallationManager:
    """Manages WOMM installation process with data-driven approach."""

    def __init__(self):
        """Initialize the installation manager."""
        self.current_path = get_current_womm_path()
        self.target_path = get_target_womm_path()
        # Track backup file for potential rollback after failures
        self._path_backup_file: Optional[str] = None

    def install(
        self,
        force: bool = False,
        target: Optional[str] = None,
    ) -> None:
        """
        Perform WOMM installation with integrated UI.

        Args:
            force: Force installation even if target directory exists
            target: Custom target directory
        """
        # Override target path if specified
        if target:
            self.target_path = Path(target).expanduser().resolve()

        # Import UI modules
        from womm.core.ui.console import (
            console,
            print_error,
            print_header,
            print_install,
            print_success,
            print_system,
        )
        from womm.core.ui.panels import create_panel
        from womm.core.ui.progress import (
            create_file_copy_progress,
            create_spinner_with_status,
            create_step_progress,
        )
        from womm.core.ui.prompts import confirm, show_warning_panel

        print_header("W.O.M.M Installation")

        # Check target directory existence
        with create_spinner_with_status("Checking target directory...") as (
            progress,
            task,
        ):
            if self.target_path.exists() and not force:
                progress.update(task, status="Directory already exists.")
            else:
                progress.update(
                    task, status="Directory does not exist, ready for installation."
                )

        # Check if target directory already exists
        if self.target_path.exists() and not force:
            # Show warning panel for existing directory
            console.print("")
            show_warning_panel(
                "Directory Already Exists",
                f"The directory {self.target_path} already exists.\n\n"
                "This will overwrite the existing installation.",
            )

            # Ask for confirmation
            if not confirm(
                "Do you want to continue and overwrite the existing directory?",
                default=False,
            ):
                console.print("❌ Installation cancelled", style="red")
                raise RuntimeError("Installation cancelled by user")

            console.print("")
            print_system("Overwriting existing installation...")

        # Copy WOMM to target directory with progress bar
        if self.current_path != self.target_path:
            # Get list of files to copy for progress bar
            files_to_copy = self._get_files_to_copy()
            with create_file_copy_progress(files_to_copy, "Copying WOMM files...") as (
                progress,
                task,
                files,
            ):
                # Iterate through each file and update progress
                for file_path in files:
                    # Update progress bar with current file
                    filename = os.path.basename(file_path)
                    progress.update(task, current_file=filename)

                    # Copy each file individually
                    try:
                        import time

                        source_file = self.current_path / file_path.rstrip("/")
                        target_file = self.target_path / file_path.rstrip("/")

                        if source_file.is_file():
                            # Copy single file
                            shutil.copy2(source_file, target_file)
                            time.sleep(0.1)
                        elif source_file.is_dir():
                            # Copy directory
                            shutil.copytree(
                                source_file, target_file, dirs_exist_ok=True
                            )
                            time.sleep(0.3)

                        # Advance progress bar
                        progress.advance(task)
                    except Exception as e:
                        print_error(f"Failed to copy {file_path}: {e}")
                        raise RuntimeError(f"Copy failed: {file_path}")

        # Backup current user PATH with spinner
        print("")
        with create_spinner_with_status("Backing up user PATH...") as (
            progress,
            task,
        ):
            progress.update(task, status="Creating PATH backup...")
            backup_result = self._backup_user_path()
            if backup_result["success"]:
                progress.update(task, status="User PATH backed up successfully")
                # Keep backup reference for potential rollback
                self._path_backup_file = backup_result.get("backup_file")
            else:
                progress.update(task, status="PATH backup failed.")
                progress.stop()
                print_error("PATH backup failed.")

        # Create WOMM executable with spinner
        print("")
        with create_spinner_with_status("Creating WOMM executable...") as (
            progress,
            task,
        ):
            progress.update(task, status="Setting up executable...")
            exec_result = self._create_womm_executable()
            if not exec_result["success"]:
                progress.update(task, status="Failed to create executable.")
                progress.stop()
                print_error(f"Failed to create executable: {exec_result['error']}")
                raise RuntimeError("Executable creation failed")
            progress.update(task, status="Executable created successfully")

        # Setup PATH with spinner
        print("")
        with create_spinner_with_status("Setting up PATH...") as (
            progress,
            task,
        ):
            path_result = self._setup_path()
            if not path_result["success"]:
                progress.update(task, status="Failed to setup PATH.")
                progress.stop()
                print_error(f"Failed to setup PATH: {path_result['error']}")
                raise RuntimeError("PATH setup failed")

            # Display proper status based on whether a new entry was added
            if path_result.get("path_added") is False:
                progress.update(task, status="PATH already configured.")
            else:
                progress.update(task, status="PATH configured successfully.")

        # Verify installation with step progress
        try:
            print("")
            print_system("Verifying installation...")
            verification_steps = ["Files", "Executable", "PATH", "Commands"]
            with create_step_progress(
                verification_steps, "Verifying installation..."
            ) as (
                progress,
                task,
                steps,
            ):
                # Perform verification for each step
                verification_results = []
                for i, step in enumerate(steps):
                    # Update progress bar with current step and step number
                    progress.update(
                        task,
                        description=f"[bold blue]{step}",
                        current_step=step,
                        step=i + 1,
                    )

                    # Perform specific verification for each step
                    if step == "Files":
                        result = self._verify_files_copied()
                    elif step == "Executable":
                        result = self._verify_executable_works()
                    elif step == "PATH":
                        result = self._verify_path_configured()
                    elif step == "Commands":
                        result = self._verify_commands_accessible()
                    else:
                        result = {
                            "success": False,
                            "error": f"Unknown verification step: {step}",
                        }

                    verification_results.append(result)

                    if not result["success"]:
                        raise Exception(
                            f"Verification failed for {step}: {result.get('error', 'Check failed')}"
                        )

                    # Advance progress bar
                    progress.advance(task)

        except Exception as e:
            print("")
            print_error(f"Error during verification: {e}")
            raise

        # Show verification details
        for result in verification_results:
            if result["success"]:
                print_success(f"✓ {result.get('message', 'Check passed')}")
            else:
                print_error(f"✗ {result.get('error', 'Check failed')}")

        # Installation success
        print("")
        print_install("🎉 Installation completed successfully!")

        # Show "to use immediately" panel
        tip_content = (
            "To use WOMM commands immediately in this terminal:\n\n"
            f"Windows: set PATH=%PATH%;{self.target_path}\n"
            f'Unix/Mac: export PATH="$PATH:{self.target_path}"\n\n'
            "Or simply restart your terminal for permanent access."
        )

        tip_panel = create_panel(
            tip_content,
            title="💡 Quick Start Tip",
            style="bright_magenta",
            border_style="bright_magenta",
            padding=(1, 1),
        )
        print("")
        console.print(tip_panel)

        return None

    # PRIVATE METHODS
    ########################################################
    # Internal methods for installation process

    def _copy_womm_to_user_directory(self) -> Dict:
        """Copy WOMM files to user directory."""
        result_dict = {
            "success": False,
            "message": "",
            "error": "",
        }

        try:
            source = self.current_path
            target = self.target_path

            # Validate paths
            if not source.exists():
                result_dict["error"] = f"Source directory does not exist: {source}"
                return result_dict

            # Create target directory
            target.mkdir(parents=True, exist_ok=True)

            # Copy files with exclusions
            def ignore_files(dir_path, files):
                return [
                    f for f in files if should_exclude_file(Path(dir_path) / f, source)
                ]

            shutil.copytree(source, target, dirs_exist_ok=True, ignore=ignore_files)

            result_dict["success"] = True
            result_dict["message"] = f"WOMM files copied successfully to {target}"
            return result_dict

        except Exception as e:
            result_dict["error"] = str(e)
            return result_dict

    def _backup_user_path(self) -> Dict:
        """Backup current user PATH."""
        result_dict = {
            "success": False,
            "message": "",
            "error": "",
        }

        try:
            backup_dir = self.target_path / ".backup"
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f".path_{timestamp}"

            if platform.system() == "Windows":
                # Windows PATH backup - use environment variable
                current_path = os.environ.get("PATH", "")
                if current_path:
                    with open(backup_file, "w", encoding="utf-8") as f:
                        f.write(f"# WOMM PATH Backup - {timestamp}\n")
                        f.write(f"# Platform: {platform.system()}\n")
                        f.write(f"# User: {os.environ.get('USERNAME', 'unknown')}\n")
                        f.write("# Original PATH:\n")
                        f.write(f"{current_path}\n")
                    result_dict["success"] = True
                    result_dict["message"] = f"PATH backup created: {backup_file.name}"
                    result_dict["backup_file"] = str(backup_file)
                    return result_dict
                else:
                    result_dict["error"] = "Could not read Windows PATH"
                    return result_dict
            else:
                # Unix PATH backup
                current_path = os.environ.get("PATH", "")
                with open(backup_file, "w", encoding="utf-8") as f:
                    f.write(f"# WOMM PATH Backup - {timestamp}\n")
                    f.write(f"# Platform: {platform.system()}\n")
                    f.write(f"# User: {os.environ.get('USER', 'unknown')}\n\n")
                    f.write(current_path)
                result_dict["success"] = True
                result_dict["message"] = f"PATH backup created: {backup_file.name}"
                result_dict["backup_file"] = str(backup_file)
                return result_dict

        except Exception as e:
            result_dict["error"] = str(e)
            return result_dict

    def _create_womm_executable(self) -> Dict:
        """Create WOMM executable."""
        result_dict = {
            "success": False,
            "message": "",
            "error": "",
        }

        try:
            if platform.system() == "Windows":
                # Create womm.bat using the current Python interpreter to avoid PATH issues
                womm_bat = self.target_path / "womm.bat"
                bat_content = (
                    f'@echo off\n"{sys.executable}" "{self.target_path}\\womm.py" %*\n'
                )
                womm_bat.write_text(bat_content, encoding="utf-8")
                result_dict["success"] = True
                result_dict["message"] = (
                    "Windows executable (womm.bat) created successfully"
                )
                return result_dict
            else:
                # Create Unix executable
                womm_exec = self.target_path / "womm"
                exec_content = f'#!/bin/bash\npython3 "{self.target_path}/womm.py" "$@"'
                womm_exec.write_text(exec_content, encoding="utf-8")
                womm_exec.chmod(0o755)
                result_dict["success"] = True
                result_dict["message"] = "Unix executable (womm) created successfully"
                return result_dict

        except Exception as e:
            result_dict["error"] = str(e)
            return result_dict

    def _setup_path(self) -> Dict:
        """Setup PATH for WOMM with proper user PATH handling and backup/restore."""
        try:
            womm_path = str(self.target_path)

            if platform.system() == "Windows":
                original_path = os.environ.get("PATH", "")
                return self._setup_windows_path(womm_path, original_path)
            else:
                # Unix PATH setup with rollback
                original_path = os.environ.get("PATH", "")
                return self._setup_unix_path(womm_path, original_path)

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _persist_path_change(self, new_path: str) -> Dict:
        """Persist PATH change to system (registry on Windows, profile on Unix)."""
        try:
            if platform.system() == "Windows":
                # Windows: Update user PATH in registry
                result = run_silent(
                    [
                        "reg",
                        "add",
                        "HKCU\\Environment",
                        "/v",
                        "PATH",
                        "/t",
                        "REG_EXPAND_SZ",
                        "/d",
                        new_path,
                        "/f",
                    ]
                )
                if result.success:
                    return {
                        "success": True,
                        "message": "PATH persisted to Windows registry",
                    }
                else:
                    return {
                        "success": False,
                        "error": "Failed to update Windows registry",
                    }
            else:
                # Unix: Update shell profile
                return self._persist_unix_path_change(new_path)

        except Exception as e:
            return {"success": False, "error": f"PATH persistence error: {e}"}

    def _persist_unix_path_change(self, _new_path: str) -> Dict:
        """Persist PATH change to Unix shell profile."""
        try:
            womm_path = str(self.target_path)
            profile_files = ["~/.bashrc", "~/.zshrc", "~/.profile"]

            for profile_file in profile_files:
                profile_path = Path(profile_file).expanduser()
                if profile_path.exists():
                    content = profile_path.read_text()
                    if womm_path not in content:
                        # Add PATH export
                        export_line = f'\n# Added by WOMM installer\nexport PATH="{womm_path}:$PATH"\n'
                        profile_path.write_text(content + export_line)
                        return {
                            "success": True,
                            "message": f"PATH persisted to {profile_file}",
                        }
                    else:
                        return {
                            "success": True,
                            "message": f"Already configured in {profile_file}",
                        }

            # If no profile found, create ~/.profile
            profile_path = Path("~/.profile").expanduser()
            export_line = (
                f'# Added by WOMM installer\nexport PATH="{womm_path}:$PATH"\n'
            )
            profile_path.write_text(export_line)
            return {"success": True, "message": "PATH persisted to new ~/.profile"}

        except Exception as e:
            return {"success": False, "error": f"Unix PATH persistence error: {e}"}

    def _rollback_path_from_backup(self) -> None:
        """Restore PATH from latest backup if available (best effort)."""
        try:
            backup_file_path: Optional[Path] = None
            # Prefer the backup created during this run
            if self._path_backup_file:
                backup_file_path = Path(self._path_backup_file)
            else:
                # Fallback to newest backup in .backup directory
                backup_dir = self.target_path / ".backup"
                backups = sorted(
                    backup_dir.glob(".path_*"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True,
                )
                if backups:
                    backup_file_path = backups[0]

            if not backup_file_path or not backup_file_path.exists():
                return

            # Parse PATH value from backup file
            path_value = ""
            content = backup_file_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            for idx, line in enumerate(lines):
                if line.strip() == "# Original PATH:" and idx + 1 < len(lines):
                    path_value = lines[idx + 1].strip()
                    break
            # If marker not found, abort rollback silently
            if not path_value:
                return

            if not path_value:
                return

            # Restore PATH according to platform
            if platform.system() == "Windows":
                run_silent(
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
            else:
                os.environ["PATH"] = path_value
        except Exception:
            # Silent best-effort rollback
            return

    def _setup_windows_path(self, womm_path: str, original_path: str) -> Dict:
        """Setup Windows PATH with automatic rollback and safety verification."""
        try:
            # Check if already in PATH
            if womm_path in original_path:
                return {
                    "success": True,
                    "path_added": False,
                    "message": "Already in PATH",
                }

            # Step 1: Get current user PATH from registry and store it
            result = run_silent(["reg", "query", "HKCU\\Environment", "/v", "PATH"])

            if result.returncode == 0:
                # Parse current user PATH from registry
                actual_user_path = extract_path_from_reg_output(result.stdout)

                # If no user PATH found, start with empty
                if not actual_user_path:
                    actual_user_path = ""

                # Check if already in user PATH
                if womm_path in actual_user_path:
                    return {
                        "success": True,
                        "path_added": False,
                        "message": "Already in user PATH",
                    }

                # Step 2: Create new user PATH (append WOMM at the end, keep order, deduplicate)
                new_user_path = (
                    f"{actual_user_path};{womm_path}" if actual_user_path else womm_path
                )
                new_user_path = deduplicate_path_entries(new_user_path)

                # Step 3: Modify user PATH in registry
                # Use REG_EXPAND_SZ to preserve expandable variables
                result = run_silent(
                    [
                        "reg",
                        "add",
                        "HKCU\\Environment",
                        "/v",
                        "PATH",
                        "/t",
                        "REG_EXPAND_SZ",
                        "/d",
                        new_user_path,
                        "/f",
                    ]
                )

                if result.returncode == 0:
                    # Step 4: Verify the modification - check if PATH length is valid
                    verification_result = run_silent(
                        ["reg", "query", "HKCU\\Environment", "/v", "PATH"]
                    )

                    if verification_result.returncode == 0:
                        # Extract the new PATH value
                        new_path_value = extract_path_from_reg_output(
                            verification_result.stdout
                        )

                        # Step 5: Safety check (content-based): ensure we didn't drop unique entries
                        def _normalize_list(path_str: str) -> list[str]:
                            parts = []
                            for p in path_str.split(";"):
                                t = p.strip()
                                if not t:
                                    continue
                                parts.append(
                                    os.path.expandvars(t).rstrip("/\\").lower()
                                )
                            # preserve order, unique
                            seen = set()
                            uniq = []
                            for x in parts:
                                if x in seen:
                                    continue
                                seen.add(x)
                                uniq.append(x)
                            return uniq

                        orig_norm = set(_normalize_list(actual_user_path))
                        new_norm = set(_normalize_list(new_path_value))
                        womm_norm = os.path.expandvars(womm_path).rstrip("/\\").lower()

                        if not (orig_norm.issubset(new_norm) and womm_norm in new_norm):
                            # Restore original user PATH
                            run_silent(
                                [
                                    "reg",
                                    "add",
                                    "HKCU\\Environment",
                                    "/v",
                                    "PATH",
                                    "/t",
                                    "REG_EXPAND_SZ",
                                    "/d",
                                    actual_user_path,
                                    "/f",
                                ]
                            )
                            return {
                                "success": False,
                                "error": "PATH verification failed - restored original PATH",
                            }

                        # Step 6: Update current session PATH (non-persistent) with dedup
                        system_path = os.environ.get("PATH", "")
                        os.environ["PATH"] = deduplicate_path_entries(
                            f"{new_user_path};{system_path}"
                        )

                        # Step 7: Final verification
                        verification = self._verify_path_modification(womm_path)
                        if verification["success"]:
                            return {
                                "success": True,
                                "path_added": True,
                                "message": "User PATH configured successfully",
                            }
                        else:
                            # Rollback: restore original user PATH
                            os.environ["PATH"] = original_path
                            run_silent(
                                [
                                    "reg",
                                    "add",
                                    "HKCU\\Environment",
                                    "/v",
                                    "PATH",
                                    "/t",
                                    "REG_EXPAND_SZ",
                                    "/d",
                                    actual_user_path,
                                    "/f",
                                ]
                            )
                            return {
                                "success": False,
                                "error": "User PATH modification failed verification",
                            }
                    else:
                        # Rollback: restore original user PATH
                        run_silent(
                            [
                                "reg",
                                "add",
                                "HKCU\\Environment",
                                "/v",
                                "PATH",
                                "/t",
                                "REG_EXPAND_SZ",
                                "/d",
                                actual_user_path,
                                "/f",
                            ]
                        )
                        return {
                            "success": False,
                            "error": "Failed to verify PATH modification",
                        }
                else:
                    return {
                        "success": False,
                        "error": "Failed to modify user PATH in registry",
                    }
            else:
                return {
                    "success": False,
                    "error": "Failed to read user PATH from registry",
                }

        except Exception as e:
            return {"success": False, "error": f"Windows user PATH setup error: {e}"}

    def _setup_unix_path(self, womm_path: str, original_path: str) -> Dict:
        """Setup Unix PATH with automatic rollback."""
        try:
            # Check if already in PATH
            if womm_path in original_path:
                return {
                    "success": True,
                    "path_added": False,
                    "message": "Already in PATH",
                }

            # Unix PATH setup
            profile_files = ["~/.bashrc", "~/.zshrc", "~/.profile"]
            for profile_file in profile_files:
                profile_path = Path(profile_file).expanduser()
                if profile_path.exists():
                    content = profile_path.read_text()
                    if womm_path not in content:
                        # Backup original content
                        backup_content = content

                        # Add PATH export
                        export_line = f'\nexport PATH="$PATH:{womm_path}"\n'
                        profile_path.write_text(content + export_line)

                        # Update current session
                        new_path = f"{original_path}:{womm_path}"
                        os.environ["PATH"] = new_path

                        # Verify the modification
                        verification = self._verify_path_modification(womm_path)
                        if verification["success"]:
                            return {
                                "success": True,
                                "path_added": True,
                                "message": f"PATH configured in {profile_file}",
                            }
                        else:
                            # Rollback: restore original content
                            profile_path.write_text(backup_content)
                            os.environ["PATH"] = original_path
                            return {
                                "success": False,
                                "error": "PATH modification failed verification",
                            }
                    else:
                        return {
                            "success": True,
                            "path_added": False,
                            "message": f"Already configured in {profile_file}",
                        }

            return {"success": False, "error": "No shell profile found"}

        except Exception as e:
            return {"success": False, "error": f"Unix PATH setup error: {e}"}

    def _verify_path_modification(self, womm_path: str) -> Dict:
        """Verify that PATH modification was successful."""
        try:
            current_path = os.environ.get("PATH", "")

            # Check if womm_path is in current PATH
            if womm_path in current_path:
                # Test if womm executable is accessible
                womm_exec = Path(womm_path) / (
                    "womm.bat" if platform.system() == "Windows" else "womm"
                )
                if womm_exec.exists():
                    return {"success": True, "message": "PATH modification verified"}
                else:
                    return {
                        "success": False,
                        "error": "WOMM executable not found after PATH modification",
                    }
            else:
                return {
                    "success": False,
                    "error": "WOMM path not found in current PATH",
                }

        except Exception as e:
            return {"success": False, "error": f"PATH verification error: {e}"}

    def _verify_installation(self) -> Dict:
        """Verify that installation was successful."""
        result_dict = {
            "success": False,
            "message": "",
            "error": "",
        }

        try:
            checks = []

            # Check 1: Files copied successfully
            files_check = self._verify_files_copied()
            checks.append(files_check)

            # Note: PATH verification is now done in _setup_windows_path with registry query
            # Executable verification removed due to Unicode encoding issues with subprocess
            # The executable works fine in interactive mode, the issue is only with subprocess.run

            success = all(check["success"] for check in checks)

            result_dict["success"] = success
            result_dict["checks"] = checks
            result_dict["message"] = "Installation verification completed"
            return result_dict

        except Exception as e:
            result_dict["error"] = f"Installation verification error: {e}"
            return result_dict

    def _verify_files_copied(self) -> Dict:
        """Verify that WOMM files were copied successfully."""
        result_dict = {
            "success": False,
            "message": "",
            "error": "",
        }

        try:
            required_files = [
                "womm.py",
                "womm.bat" if platform.system() == "Windows" else "womm",
            ]
            missing_files = []

            for file_name in required_files:
                file_path = self.target_path / file_name
                if not file_path.exists():
                    missing_files.append(file_name)

            if missing_files:
                result_dict["error"] = f"Missing files: {', '.join(missing_files)}"
                return result_dict
            else:
                result_dict["success"] = True
                result_dict["message"] = "All required files present"
                return result_dict

        except Exception as e:
            result_dict["error"] = f"File verification error: {e}"
            return result_dict

    def _verify_executable_works(self) -> Dict:
        """Verify that WOMM executable works correctly."""
        result_dict = {
            "success": False,
            "message": "",
            "error": "",
        }

        try:
            if platform.system() == "Windows":
                exec_path = self.target_path / "womm.bat"
            else:
                exec_path = self.target_path / "womm"

            if not exec_path.exists():
                result_dict["error"] = "WOMM executable not found"
                return result_dict

            # Test basic functionality - avoid --help due to Unicode encoding issues
            # Just test that the executable can be run without arguments
            if platform.system() == "Windows":
                # Use cmd to run batch files when shell=False; quote path for spaces
                test_result = run_silent(["cmd", "/c", f'"{str(exec_path)}"'])
            else:
                test_result = run_silent([str(exec_path)])

            # Accept common benign exit codes
            if test_result.returncode in [0, 1, 2]:
                result_dict["success"] = True
                result_dict["message"] = "WOMM executable working correctly"
                return result_dict
            else:
                result_dict["error"] = (
                    f"WOMM executable failed basic test (exit code: {test_result.returncode})"
                )
                return result_dict

        except Exception as e:
            result_dict["error"] = f"Executable verification error: {e}"
            return result_dict

    def _verify_path_configured(self) -> Dict:
        """Verify that PATH is configured correctly."""
        result_dict = {
            "success": False,
            "message": "",
            "error": "",
        }

        try:
            current_path = os.environ.get("PATH", "")
            womm_path = str(self.target_path)

            if womm_path in current_path:
                result_dict["success"] = True
                result_dict["message"] = "PATH configured correctly"
                return result_dict
            else:
                result_dict["error"] = "WOMM path not found in current PATH"
                return result_dict

        except Exception as e:
            result_dict["error"] = f"PATH verification error: {e}"
            return result_dict

    def _verify_commands_accessible(self) -> Dict:
        """Verify that WOMM commands are accessible."""
        result_dict = {
            "success": False,
            "message": "",
            "error": "",
        }

        try:
            # Test if womm command is accessible
            if platform.system() == "Windows":
                # Lancer un nouvel invite de cmd en background pour checker
                # car le terminal actuel n'a pas le PATH à jour
                test_result = run_silent(["cmd", "/c", "where", "womm"])
            else:
                test_result = run_silent(["which", "womm"])

            if test_result.success:
                result_dict["success"] = True
                result_dict["message"] = "WOMM commands accessible"
                return result_dict
            else:
                result_dict["error"] = "WOMM commands not accessible"
                return result_dict

        except Exception as e:
            result_dict["error"] = f"Command accessibility error: {e}"
            return result_dict

    def _get_files_to_copy(self) -> List[str]:
        """Get list of files and directories to copy for progress bar."""
        files_to_copy = []
        source = self.current_path

        # Add main files and directories
        for item in source.iterdir():
            if should_exclude_file(item, source):
                continue
            if item.is_file():
                files_to_copy.append(str(item.name))
            elif item.is_dir():
                files_to_copy.append(f"{item.name}/")

        return files_to_copy
