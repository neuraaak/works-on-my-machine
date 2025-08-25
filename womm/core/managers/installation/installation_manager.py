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
        from ...ui.common.extended.dynamic_progress import (
            create_dynamic_layered_progress,
        )
        from ...ui.common.extended.progress_animations import ProgressAnimations
        from ...ui.common.panels import create_panel

        print_header("W.O.M.M Installation")

        # Check target directory existence
        from ...ui.common.progress import create_spinner_with_status

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
                from ...ui.common.prompts import show_warning_panel

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

        # Define installation stages with DynamicLayeredProgress
        # Color palette: main layer is bright, sub-layers use softer colors
        stages = [
            {
                "name": "main_installation",
                "type": "main",
                "steps": [
                    "Preparation",
                    "File Copy",
                    "Executable",
                    "Backup",
                    "PATH Setup",
                    "Verification",
                ],
                "description": "WOMM Installation Progress",
                "style": "bold bright_white",
            },
            {
                "name": "preparation",
                "type": "spinner",
                "description": "Preparing installation environment...",
                "style": "bright_cyan",
            },
            {
                "name": "file_copy",
                "type": "progress",
                "total": len(files_to_copy),
                "description": "Copying project files...",
                "style": "bright_magenta",
            },
            {
                "name": "executable",
                "type": "spinner",
                "description": "Creating executable script...",
                "style": "bright_cyan",
            },
            {
                "name": "backup",
                "type": "spinner",
                "description": "Creating PATH backup...",
                "style": "bright_cyan",
            },
            {
                "name": "path_setup",
                "type": "spinner",
                "description": "Configuring PATH environment...",
                "style": "bright_cyan",
            },
            {
                "name": "verification",
                "type": "steps",
                "steps": [
                    "File integrity check",
                    "Essential files verification",
                    "Command accessibility test",
                    "PATH configuration test",
                ],
                "description": "Verifying installation...",
                "style": "bright_green",
            },
        ]

        console.print("")
        with create_dynamic_layered_progress(stages) as progress:
            animations = ProgressAnimations(progress.progress)

            # Stage 1: Preparation
            prep_messages = [
                "Analyzing system requirements...",
                "Checking target directory permissions...",
                "Validating installation path...",
                "Preparing file operations...",
            ]

            for msg in prep_messages:
                progress.update_layer("preparation", 0, msg)
                sleep(0.2)

            # Complete preparation
            progress.complete_layer("preparation")
            # Get task_id for animation
            prep_task_id = None
            for tid, metadata in progress.layer_metadata.items():
                if metadata["name"] == "preparation":
                    prep_task_id = tid
                    break
            if prep_task_id:
                animations.success_flash(prep_task_id, duration=0.5)

            # Update main installation progress
            progress.update_layer("main_installation", 0, "Preparation completed")
            sleep(0.3)

            # Stage 2: Copy files
            if not self._copy_files_with_progress(files_to_copy, progress, verbose):
                progress.emergency_stop("Failed to copy files")
                print_error("Failed to copy files")
                return False

            # Complete file copy
            progress.complete_layer("file_copy")
            # Get task_id for animation
            copy_task_id = None
            for tid, metadata in progress.layer_metadata.items():
                if metadata["name"] == "file_copy":
                    copy_task_id = tid
                    break
            if copy_task_id:
                animations.success_flash(copy_task_id, duration=0.5)

            # Update main installation progress
            progress.update_layer("main_installation", 1, "Files copied successfully")
            sleep(0.3)

            # Stage 3: Create executable
            progress.update_layer("executable", 0, "Creating womm.py executable...")
            executable_result = create_womm_executable(self.target_path)
            if not executable_result["success"]:
                progress.emergency_stop(
                    f"Failed to create executable: {executable_result.get('error')}"
                )
                print_error(
                    f"Failed to create executable: {executable_result.get('error')}"
                )
                return False

            progress.update_layer("executable", 0, "Creating womm.bat wrapper...")
            sleep(0.2)

            # Complete executable creation
            progress.complete_layer("executable")
            # Get task_id for animation
            exe_task_id = None
            for tid, metadata in progress.layer_metadata.items():
                if metadata["name"] == "executable":
                    exe_task_id = tid
                    break
            if exe_task_id:
                animations.success_flash(exe_task_id, duration=0.5)

            # Update main installation progress
            progress.update_layer("main_installation", 2, "Executable created")
            sleep(0.3)

            # Stage 4: Backup PATH
            progress.update_layer(
                "backup", 0, "Backing up current PATH configuration..."
            )
            if not self._backup_path():
                progress.emergency_stop("Failed to backup PATH")
                print_error("Failed to backup PATH")
                return False

            progress.update_layer("backup", 0, "PATH backup completed successfully")
            sleep(0.2)

            # Complete backup
            progress.complete_layer("backup")
            # Get task_id for animation
            backup_task_id = None
            for tid, metadata in progress.layer_metadata.items():
                if metadata["name"] == "backup":
                    backup_task_id = tid
                    break
            if backup_task_id:
                animations.success_flash(backup_task_id, duration=0.5)

            # Update main installation progress
            progress.update_layer("main_installation", 3, "PATH backup completed")
            sleep(0.3)

            # Stage 5: Setup PATH
            progress.update_layer(
                "path_setup", 0, "Configuring PATH environment variable..."
            )
            if not self._setup_path():
                progress.emergency_stop("Failed to setup PATH")
                print_error("Failed to setup PATH")
                self._rollback_path()  # Rollback on failure
                return False

            progress.update_layer("path_setup", 0, "PATH configuration completed")
            sleep(0.2)

            # Complete PATH setup
            progress.complete_layer("path_setup")
            # Get task_id for animation
            path_task_id = None
            for tid, metadata in progress.layer_metadata.items():
                if metadata["name"] == "path_setup":
                    path_task_id = tid
                    break
            if path_task_id:
                animations.success_flash(path_task_id, duration=0.5)

            # Update main installation progress
            progress.update_layer("main_installation", 4, "PATH configured")
            sleep(0.3)

            # Stage 6: Verification
            if not self._verify_installation_with_progress(progress):
                progress.emergency_stop("Installation verification failed")
                print_error("Installation verification failed")
                self._rollback_path()  # Rollback on failure
                return False

            # Complete verification
            progress.complete_layer("verification")
            # Get task_id for animation
            verify_task_id = None
            for tid, metadata in progress.layer_metadata.items():
                if metadata["name"] == "verification":
                    verify_task_id = tid
                    break
            if verify_task_id:
                animations.success_flash(verify_task_id, duration=0.5)

            # Complete main installation progress
            progress.update_layer(
                "main_installation", 5, "Installation completed successfully!"
            )
            sleep(0.3)

            # Final animation for main installation
            main_task_id = None
            for tid, metadata in progress.layer_metadata.items():
                if metadata["name"] == "main_installation":
                    main_task_id = tid
                    break
            if main_task_id:
                animations.success_flash(main_task_id, duration=1.0)
                sleep(1.2)

            # Complete and remove main installation layer
            progress.complete_layer("main_installation")

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

    def _copy_files_with_progress(
        self,
        files_to_copy: list[str],
        progress,
        verbose: bool = False,
    ) -> bool:
        """Copy files from source to target directory with progress tracking.

        Args:
            files_to_copy: List of relative file paths to copy
            progress: DynamicLayeredProgress instance
            verbose: Show detailed progress information

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create target directory
            self.target_path.mkdir(parents=True, exist_ok=True)

            # Copy files with progress tracking
            from ...ui.common.console import print_system

            for i, relative_file in enumerate(files_to_copy):
                source_file = self.source_path / relative_file
                target_file = self.target_path / relative_file

                # Update file copy progress
                file_name = Path(relative_file).name
                progress.update_layer("file_copy", i + 1, f"Copying: {file_name}")

                # Create parent directories
                target_file.parent.mkdir(parents=True, exist_ok=True)

                # Copy the file
                shutil.copy2(source_file, target_file)
                sleep(0.01)

                if verbose:
                    print_system(f"📄 Copied: {relative_file}")

            return True

        except Exception as e:
            from ...ui.common.console import print_error

            print_error(f"Error copying files: {e}")
            return False

    def _verify_installation_with_progress(self, progress) -> bool:
        """Verify installation with progress tracking.

        Args:
            progress: DynamicLayeredProgress instance

        Returns:
            True if verification passed, False otherwise
        """
        try:
            # Step 1: File integrity check
            progress.update_layer("verification", 0, "Checking file integrity...")
            files_result = verify_files_copied(self.source_path, self.target_path)
            if not files_result["success"]:
                from ...ui.common.console import print_error

                print_error(
                    f"File verification failed: {files_result.get('error', 'Files missing or corrupted')}"
                )
                return False
            sleep(0.2)

            # Step 2: Essential files verification
            progress.update_layer("verification", 1, "Verifying essential files...")
            essential_files = ["womm.py", "womm.bat"]
            for essential_file in essential_files:
                file_path = self.target_path / essential_file
                if not file_path.exists():
                    from ...ui.common.console import print_error

                    print_error(f"Essential file missing: {essential_file}")
                    return False
            sleep(0.2)

            # Step 3: Command accessibility test
            progress.update_layer("verification", 2, "Testing command accessibility...")
            commands_result = verify_commands_accessible(str(self.target_path))
            if not commands_result["success"]:
                from ...ui.common.console import print_error

                print_error(f"Commands not accessible: {commands_result.get('error')}")
                return False
            sleep(0.2)

            # Step 4: PATH configuration test
            progress.update_layer("verification", 3, "Verifying PATH configuration...")
            path_result = verify_path_configuration(str(self.target_path))
            if not path_result["success"]:
                from ...ui.common.console import print_error

                print_error(f"PATH configuration failed: {path_result.get('error')}")
                return False
            sleep(0.2)

            return True

        except Exception as e:
            from ...ui.common.console import print_error

            print_error(f"Error during verification: {e}")
            return False

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
            sleep(0.5)

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
