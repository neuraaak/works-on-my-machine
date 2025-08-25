#!/usr/bin/env python3
"""
Uninstaller for Works On My Machine.
Removes WOMM from the system and cleans up PATH entries.
"""

# IMPORTS
########################################################
# Standard library imports
import platform
from pathlib import Path
from typing import Optional

# Local imports
from ...utils.installation import (
    get_files_to_remove,
    get_target_womm_path,
    verify_uninstallation_complete,
)
from ...utils.installation.path_management_utils import remove_from_path

# MAIN CLASS
########################################################
# Core uninstallation manager class


class UninstallationManager:
    """Manages the uninstallation process for Works On My Machine."""

    def __init__(self, target: Optional[str] = None):
        """Initialize the uninstallation manager.

        Args:
            target: Custom target directory (default: ~/.womm)
        """
        if target:
            self.target_path = Path(target).expanduser().resolve()
        else:
            self.target_path = get_target_womm_path()

        self.platform = platform.system()

    def uninstall(
        self,
        force: bool = False,
        dry_run: bool = False,
        verbose: bool = False,
    ) -> bool:
        """Uninstall Works On My Machine from the user's system.

        Args:
            force: Force uninstallation without confirmation
            dry_run: Show what would be done without making changes
            verbose: Show detailed progress information

        Returns:
            True if uninstallation successful, False otherwise
        """
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
        from ...ui.common.progress import create_spinner_with_status
        from ...ui.common.prompts import confirm, show_warning_panel

        print_header("W.O.M.M Uninstallation")

        # Check target directory existence
        with create_spinner_with_status("Checking target directory...") as (
            progress,
            task,
        ):
            progress.update(task, status="Analyzing uninstallation requirements...")

            # Check if WOMM is installed
            if not self.target_path.exists():
                progress.stop()
                show_warning_panel(
                    "WOMM not found",
                    f"No installation found at: {self.target_path}\n"
                    "WOMM may not be installed or may be in a different location",
                )
                return False
            else:
                progress.update(
                    task, status=f"Found installation at: {self.target_path}"
                )

        # Check if force is required
        if not force and not dry_run:
            # Show warning panel for uninstallation
            console.print("")
            show_warning_panel(
                "Uninstallation Confirmation",
                f"This will completely remove WOMM from {self.target_path}.\n\n"
                "This action cannot be undone.",
            )

            # Ask for confirmation
            if not confirm(
                "Do you want to continue and remove WOMM completely?",
                default=False,
            ):
                console.print("❌ Uninstallation cancelled", style="red")
                return False

            console.print("")
            print_system("Proceeding with uninstallation...")

        if dry_run:
            print_system("DRY RUN MODE - No changes will be made")

        # Get list of files to remove
        print("")
        with create_spinner_with_status("Analyzing installed files...") as (
            progress,
            task,
        ):
            progress.update(task, status="Scanning installation directory...")
            files_to_remove = get_files_to_remove(self.target_path)
            progress.update(
                task, status=f"Found {len(files_to_remove)} files to remove"
            )

        if dry_run:
            print_install("Would remove from PATH configuration")
            print_install(f"Would remove {len(files_to_remove)} files")
            print_install(f"Would remove directory: {self.target_path}")
            if verbose:
                print_system("🔍 Dry run mode - detailed logging enabled")
                for file_path in files_to_remove[:5]:  # Show first 5 files as sample
                    print_system(f"  📄 Would remove: {file_path}")
                if len(files_to_remove) > 5:
                    print_system(f"  ... and {len(files_to_remove) - 5} more files")
            return True

        # Define uninstallation stages with DynamicLayeredProgress
        stages = [
            {
                "name": "main_uninstallation",
                "type": "main",
                "steps": [
                    "PATH Cleanup",
                    "File Removal",
                    "Verification",
                ],
                "description": "WOMM Uninstallation Progress",
                "style": "bold bright_white",
            },
            {
                "name": "path_cleanup",
                "type": "spinner",
                "description": "Removing from PATH...",
                "style": "bright_red",
            },
            {
                "name": "file_removal",
                "type": "progress",
                "total": len(files_to_remove),
                "description": "Removing installation files...",
                "style": "bright_red",
            },
            {
                "name": "verification",
                "type": "steps",
                "steps": [
                    "File removal check",
                    "Command accessibility test",
                ],
                "description": "Verifying uninstallation...",
                "style": "bright_green",
            },
        ]

        print("")
        with create_dynamic_layered_progress(stages) as progress:
            animations = ProgressAnimations(progress.progress)

            # Stage 1: PATH Cleanup
            progress.update_layer("path_cleanup", 0, "Removing WOMM from PATH...")
            if not remove_from_path(self.target_path):
                progress.emergency_stop("Failed to remove from PATH")
                print_error("Failed to remove from PATH")
                if verbose:
                    print_system("❌ PATH cleanup failed")
                return False

            progress.update_layer("path_cleanup", 0, "PATH cleanup completed")
            from time import sleep

            sleep(0.2)

            # Complete PATH cleanup
            progress.complete_layer("path_cleanup")
            # Get task_id for animation
            path_task_id = None
            for tid, metadata in progress.layer_metadata.items():
                if metadata["name"] == "path_cleanup":
                    path_task_id = tid
                    break
            if path_task_id:
                animations.success_flash(path_task_id, duration=0.5)

            # Update main uninstallation progress
            progress.update_layer("main_uninstallation", 0, "PATH cleanup completed")
            sleep(0.3)

            # Stage 2: File Removal
            if not self._remove_files_with_progress(files_to_remove, progress, verbose):
                progress.emergency_stop("Failed to remove files")
                print_error("Failed to remove files")
                if verbose:
                    print_system("❌ File removal failed")
                return False

            # Complete file removal
            progress.complete_layer("file_removal")
            # Get task_id for animation
            file_task_id = None
            for tid, metadata in progress.layer_metadata.items():
                if metadata["name"] == "file_removal":
                    file_task_id = tid
                    break
            if file_task_id:
                animations.success_flash(file_task_id, duration=0.5)

            # Update main uninstallation progress
            progress.update_layer(
                "main_uninstallation", 1, "Files removed successfully"
            )
            sleep(0.3)

            # Stage 3: Verification
            if not self._verify_uninstallation_with_progress(progress):
                progress.emergency_stop("Uninstallation verification failed")
                print_error("Uninstallation verification failed")
                if verbose:
                    print_system("❌ Verification checks failed")
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

            # Complete main uninstallation progress
            progress.update_layer(
                "main_uninstallation", 2, "Uninstallation completed successfully!"
            )
            sleep(0.3)

            # Final animation for main uninstallation
            main_task_id = None
            for tid, metadata in progress.layer_metadata.items():
                if metadata["name"] == "main_uninstallation":
                    main_task_id = tid
                    break
            if main_task_id:
                animations.success_flash(main_task_id, duration=1.0)
                sleep(1.2)

            # Complete and remove main uninstallation layer
            progress.complete_layer("main_uninstallation")

        print("")
        print_success("✅ W.O.M.M uninstallation completed successfully!")
        print_system(f"📁 Removed from: {self.target_path}")

        # Show completion panel
        completion_content = (
            "WOMM has been successfully removed from your system.\n\n"
            "To complete the cleanup:\n"
            "• Restart your terminal for PATH changes to take effect\n"
            "• Remove any remaining WOMM references from your shell config files\n\n"
            "Thank you for using Works On My Machine!"
        )

        completion_panel = create_panel(
            completion_content,
            title="✅ Uninstallation Complete",
            style="bright_green",
            border_style="bright_green",
            padding=(1, 1),
        )
        print("")
        console.print(completion_panel)

        return True

    def _remove_files_with_progress(
        self, files_to_remove: list[str], progress, verbose: bool = False
    ) -> bool:
        """Remove WOMM installation files with progress tracking.

        Args:
            files_to_remove: List of files and directories to remove for progress tracking
            progress: DynamicLayeredProgress instance
            verbose: Show detailed progress information

        Returns:
            True if successful, False otherwise
        """
        try:
            import shutil
            from time import sleep

            # Remove each file and directory in order (files first, then directories)
            for i, item_path in enumerate(files_to_remove):
                target_item = self.target_path / item_path.rstrip("/")

                if not target_item.exists():
                    continue

                # Update progress
                item_name = Path(item_path).name
                if item_path.endswith("/"):
                    progress.update_layer(
                        "file_removal", i + 1, f"Removing directory: {item_name}"
                    )
                else:
                    progress.update_layer(
                        "file_removal", i + 1, f"Removing file: {item_name}"
                    )

                try:
                    if target_item.is_file():
                        target_item.unlink()
                        sleep(0.01)
                        if verbose:
                            from ...ui.common.console import print_system

                            print_system(f"🗑️ Removed file: {item_path}")
                    elif target_item.is_dir():
                        shutil.rmtree(target_item)
                        sleep(0.02)
                        if verbose:
                            from ...ui.common.console import print_system

                            print_system(f"🗑️ Removed directory: {item_path}")
                except Exception as e:
                    from ...ui.common.console import print_error

                    print_error(f"Failed to remove {item_path}: {e}")

            # Finally remove the root directory itself
            if self.target_path.exists():
                progress.update_layer(
                    "file_removal",
                    len(files_to_remove) + 1,
                    "Removing installation directory",
                )
                shutil.rmtree(self.target_path)
                sleep(0.1)

                if verbose:
                    from ...ui.common.console import print_system

                    print_system(
                        f"🗑️ Removed installation directory: {self.target_path}"
                    )

            return True

        except Exception as e:
            from ...ui.common.console import print_error

            print_error(f"Error removing files: {e}")
            return False

    def _verify_uninstallation_with_progress(self, progress) -> bool:
        """Verify uninstallation with progress tracking.

        Args:
            progress: DynamicLayeredProgress instance

        Returns:
            True if verification passed, False otherwise
        """
        try:
            from time import sleep

            # Step 1: File removal check
            progress.update_layer("verification", 0, "Checking file removal...")
            if self.target_path.exists():
                from ...ui.common.console import print_error

                print_error(f"Installation directory still exists: {self.target_path}")
                return False
            sleep(0.2)

            # Step 2: Command accessibility test
            progress.update_layer("verification", 1, "Testing command accessibility...")
            verification_result = verify_uninstallation_complete(self.target_path)
            if not verification_result["success"]:
                from ...ui.common.console import print_error

                print_error(
                    f"Verification failed: {verification_result.get('error', 'Unknown error')}"
                )
                return False
            sleep(0.2)

            return True

        except Exception as e:
            from ...ui.common.console import print_error

            print_error(f"Error during verification: {e}")
            return False
