#!/usr/bin/env python3
"""
Installation Manager for Works On My Machine.

This module handles the complete installation process of WOMM to the user's
home directory, using utility functions for core operations.

Author: WOMM Team
Version: 2.2.0
"""

# IMPORTS
########################################################
# Standard library imports
import platform
import shutil
from pathlib import Path
from time import sleep
from typing import Optional

# Local imports
from ...utils.installation import (
    create_womm_executable,
    get_current_womm_path,
    get_files_to_copy,
    get_target_womm_path,
    verify_files_copied,
)
from ...utils.installation.path_management_utils import (
    verify_commands_accessible,
    verify_path_configuration,
)

# MAIN CLASS
########################################################
# Core installation manager class


class InstallationManager:
    """Manages the installation process for Works On My Machine.

    This class handles all aspects of installing Works On My Machine to the user's
    system, including:
        - File copying and directory structure setup
        - PATH environment variable configuration
        - Registry modifications (Windows)
        - Backup creation for safe rollback
        - Interactive UI with progress tracking
        - Security validation throughout the process

    The installer supports both development (git clone) and PyPI installations,
    with automatic detection and appropriate handling for each scenario.
    """

    def __init__(self):
        """Initialize the installation manager."""
        self.source_path = get_current_womm_path()
        self.target_path = get_target_womm_path()
        self.actions = []
        self.platform = platform.system()
        # Track backup file for potential rollback after failures
        self._path_backup_file: Optional[str] = None

    def install(
        self,
        target: Optional[str] = None,
        force: bool = False,
        backup: bool = True,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Install Works On My Machine to the user's system.

        Args:
            target: Custom target directory (default: ~/.womm)
            force: Force installation even if already installed
            backup: Create backup before installation
            dry_run: Show what would be done without making changes
            verbose: Show detailed progress information

        Returns:
            True if installation successful, False otherwise
        """
        # Override target path if specified
        if target:
            self.target_path = Path(target).expanduser().resolve()

        # Import UI modules
        from ...ui.common.console import (
            console,
            print_error,
            print_header,
            print_install,
            print_success,
            print_system,
        )
        from ...ui.common.panels import create_panel
        from ...ui.common.progress import (
            create_layered_progressbar,
            create_spinner_with_status,
        )
        from ...ui.common.prompts import show_warning_panel

        print_header("W.O.M.M Installation")

        # Check target directory existence
        with create_spinner_with_status("Checking target directory...") as (
            progress,
            task,
        ):
            progress.update(task, status="Analyzing installation requirements...")

            # Check if WOMM is already installed
            if (
                self.target_path.exists()
                and any(self.target_path.iterdir())
                and not force
            ):
                show_warning_panel(
                    "Installation directory already exists",
                    f"Target directory: {self.target_path}\n"
                    "Use --force to overwrite existing installation",
                )
                return False

        if dry_run:
            print_system("DRY RUN MODE - No changes will be made")

        # Get list of files to copy
        console.print("")
        with create_spinner_with_status("Analyzing source files...") as (
            progress,
            task,
        ):
            progress.update(task, status="Scanning source directory...")
            files_to_copy = get_files_to_copy(self.source_path)
            progress.update(task, status=f"Found {len(files_to_copy)} files to copy")

        if dry_run:
            if backup:
                print_install("Would backup current PATH configuration")
            print_install(
                f"Would copy {len(files_to_copy)} files to {self.target_path}"
            )
            print_install("Would setup PATH configuration")
            print_install("Would create executable script")
            print_install("Would verify installation")
            if verbose:
                print_system("🔍 Dry run mode - detailed logging enabled")
                for file_path in files_to_copy[:5]:  # Show first 5 files as sample
                    print_system(f"  📄 Would copy: {file_path}")
                if len(files_to_copy) > 5:
                    print_system(f"  ... and {len(files_to_copy) - 5} more files")
            return True

        # Actual installation steps
        installation_steps = ["Files", "Executable", "PATH", "Verification"]
        if backup:
            installation_steps.insert(0, "Backup")

        # Define layers for layered progress bar
        layers = [
            {
                "name": "main_steps",
                "total": len(installation_steps),
                "description": "Installing W.O.M.M...",
                "style": "bold blue",
            },
            {
                "name": "file_copy",
                "total": len(files_to_copy),
                "description": "Copying files...",
                "style": "dim white",
            },
        ]

        console.print("")
        with create_layered_progressbar(layers) as (progress, task_ids):
            # Step 1: Backup PATH (if enabled)
            if backup:
                progress.update(task_ids["main_steps"], details="Backup")
                if not self._backup_path():
                    print_error("Failed to backup PATH")
                    return False
                progress.advance(task_ids["main_steps"])
                if verbose:
                    print_system(f"✅ PATH backup saved: {self._path_backup_file}")

            # Step 2: Copy files
            progress.update(task_ids["main_steps"], details="Files")
            if not self._copy_files(
                files_to_copy, verbose, progress, task_ids["file_copy"]
            ):
                progress.stop()
                print_error("Failed to copy files")
                if backup:
                    self._rollback_path()  # Rollback on failure
                return False
            progress.advance(task_ids["main_steps"])
            if verbose:
                print_system(
                    f"✅ Copied {len(files_to_copy)} files to {self.target_path}"
                )

            # Step 3: Create executable
            progress.update(task_ids["main_steps"], details="Executable")
            executable_result = create_womm_executable(self.target_path)
            if not executable_result["success"]:
                progress.stop()
                print_error(
                    f"Failed to create executable: {executable_result.get('error')}"
                )
                if backup:
                    self._rollback_path()  # Rollback on failure
                return False
            progress.advance(task_ids["main_steps"])
            if verbose:
                print_system("✅ Executable script created")

            # Step 4: Setup PATH
            progress.update(task_ids["main_steps"], details="PATH")
            if not self._setup_path():
                progress.stop()
                print_error("Failed to setup PATH")
                if backup:
                    self._rollback_path()  # Rollback on failure
                return False
            progress.advance(task_ids["main_steps"])
            if verbose:
                print_system("✅ PATH environment variable configured")

            # Step 5: Verification
            progress.update(task_ids["main_steps"], details="Verification")
            if not self._verify_installation():
                progress.stop()
                print_error("Installation verification failed")
                if backup:
                    self._rollback_path()  # Rollback on failure
                return False
            progress.advance(task_ids["main_steps"])
            if verbose:
                print_system("✅ Installation verification completed")

        console.print("")
        print_success("✅ W.O.M.M installation completed successfully!")
        print_system(f"📁 Installed to: {self.target_path}")

        # Show completion panel
        completion_content = (
            "WOMM has been successfully installed on your system.\n\n"
            "Getting started:\n"
            "• Run 'womm --help' to see all available commands\n"
            "• Try 'womm init' to set up a new project\n"
            "• Use 'womm deploy' to manage your development tools\n\n"
            "• Restart your terminal for PATH changes to take effect\n\n"
            "Welcome to Works On My Machine!"
        )

        completion_panel = create_panel(
            completion_content,
            title="✅ Installation Complete",
            style="bright_green",
            border_style="bright_green",
            padding=(1, 1),
        )
        console.print("")
        console.print(completion_panel)

        return True

    def _copy_files(
        self,
        files_to_copy: list[str],
        verbose: bool = False,
        progress=None,
        file_task_id=None,
    ) -> bool:
        """Copy files from source to target directory.

        Args:
            files_to_copy: List of relative file paths to copy
            verbose: Show detailed progress information

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create target directory
            self.target_path.mkdir(parents=True, exist_ok=True)

            # Copy files with layered progress bar
            from ...ui.common.console import print_system

            for _i, relative_file in enumerate(files_to_copy):
                source_file = self.source_path / relative_file
                target_file = self.target_path / relative_file

                # Update file copy progress bar
                if progress and file_task_id is not None:
                    file_name = Path(relative_file).name
                    progress.update(file_task_id, details=f"Copying: {file_name}")

                # Create parent directories
                target_file.parent.mkdir(parents=True, exist_ok=True)

                # Copy the file
                shutil.copy2(source_file, target_file)
                sleep(0.01)

                # Advance file copy progress
                if progress and file_task_id is not None:
                    progress.advance(file_task_id)

                if verbose:
                    print_system(f"📄 Copied: {relative_file}")

            return True

        except Exception as e:
            from ...ui.common.console import print_error

            print_error(f"Error copying files: {e}")
            return False

    def _setup_path(self) -> bool:
        """Setup PATH environment variable using PathManager.

        Returns:
            True if successful, False otherwise
        """
        try:
            from ...managers.system.user_path_manager import PathManager

            path_manager = PathManager(target=str(self.target_path))
            result = path_manager.add_to_path()

            if not result["success"]:
                from ...ui.common.console import print_error

                print_error(
                    f"PATH setup failed: {result.get('error', 'Unknown error')}"
                )
                if "stderr" in result:
                    print_error(f"stderr: {result['stderr']}")
                return False

            return True

        except Exception as e:
            from ...ui.common.console import print_error

            print_error(f"Error setting up PATH: {e}")
            return False

    def _verify_installation(self) -> bool:
        """Verify that the installation completed successfully.

        Returns:
            True if verification passed, False otherwise
        """
        try:
            # Use utils for verification

            # 0. Verify all files were copied correctly
            files_result = verify_files_copied(self.source_path, self.target_path)
            if not files_result["success"]:
                from ...ui.common.console import print_error

                print_error(
                    f"File verification failed: {files_result.get('error', 'Files missing or corrupted')}"
                )
                return False

            # 1. Verify essential files exist (basic check during installation)
            essential_files = ["womm.py", "womm.bat"]
            for essential_file in essential_files:
                file_path = self.target_path / essential_file
                if not file_path.exists():
                    from ...ui.common.console import print_error

                    print_error(f"Essential file missing: {essential_file}")
                    return False

            # 2. Verify commands are accessible in PATH
            commands_result = verify_commands_accessible(str(self.target_path))
            if not commands_result["success"]:
                from ...ui.common.console import print_error

                print_error(f"Commands not accessible: {commands_result.get('error')}")
                return False

            # 3. Verify PATH configuration
            path_result = verify_path_configuration(str(self.target_path))
            if not path_result["success"]:
                from ...ui.common.console import print_error

                print_error(f"PATH configuration failed: {path_result.get('error')}")
                return False

            return True

        except Exception as e:
            from ...ui.common.console import print_error

            print_error(f"Error during verification: {e}")
            return False

    def _backup_path(self) -> bool:
        """Backup current PATH configuration using PathManager.

        Returns:
            True if backup successful, False otherwise
        """
        try:
            from ...managers.system.user_path_manager import PathManager

            path_manager = PathManager(target=str(self.target_path))
            backup_result = path_manager._backup_path()

            if backup_result["success"]:
                # Keep backup reference for potential rollback
                backup_files = backup_result.get("backup_files", [])
                if backup_files:
                    latest_name = backup_files[0]
                    self._path_backup_file = str(
                        (path_manager.backup_dir / latest_name).resolve()
                    )
                return True
            else:
                from ...ui.common.console import print_error

                print_error(f"PATH backup failed: {backup_result.get('error')}")
                return False

        except Exception as e:
            from ...ui.common.console import print_error

            print_error(f"Error during PATH backup: {e}")
            return False

    def _rollback_path(self) -> bool:
        """Rollback PATH to previous state using PathManager backup.

        Returns:
            True if rollback successful, False otherwise
        """
        try:
            if not self._path_backup_file:
                from ...ui.common.console import print_error

                print_error("No backup file available for rollback")
                return False

            # Use PathManager to restore from specific backup file
            import json
            from pathlib import Path

            backup_file = Path(self._path_backup_file)
            if not backup_file.exists():
                from ...ui.common.console import print_error

                print_error(f"Backup file not found: {backup_file}")
                return False

            # Read backup data to get the PATH string
            with open(backup_file, encoding="utf-8") as f:
                backup_data = json.load(f)

            restored_path = backup_data.get("path_string", "")
            if not restored_path:
                from ...ui.common.console import print_error

                print_error("Invalid backup file: no PATH string found")
                return False

            # Use PathManager's platform-specific restore logic
            from ...managers.system.user_path_manager import PathManager

            path_manager = PathManager(target=str(self.target_path))

            if path_manager.platform == "Windows":
                from ...utils.cli_utils import run_silent

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
                        restored_path,
                        "/f",
                    ]
                )

                if result.success:
                    from ...ui.common.console import print_success

                    print_success("PATH successfully rolled back to previous state")
                    return True
                else:
                    from ...ui.common.console import print_error

                    print_error(f"PATH rollback failed: {result.stderr}")
                    return False
            else:
                # Unix rollback - update environment
                import os

                os.environ["PATH"] = restored_path
                from ...ui.common.console import print_success

                print_success("PATH successfully rolled back to previous state")
                return True

        except Exception as e:
            from ...ui.common.console import print_error

            print_error(f"Error during PATH rollback: {e}")
            return False
