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
    verify_files_removed,
    verify_uninstallation_complete,
)
from ...utils.installation.path_management_utils import (
    remove_from_path,
)


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
        from ...ui.common.panels import (
            create_panel,
        )
        from ...ui.common.prompts import (
            confirm,
            show_warning_panel,
        )
        from ...ui.common.progress import (
            create_file_copy_progress,
            create_spinner_with_status,
            create_step_progress,
        )

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

        # Actual uninstallation steps
        uninstallation_steps = ["PATH", "Files", "Verification"]

        print("")
        with create_step_progress(uninstallation_steps, "Uninstalling W.O.M.M...") as (
            progress,
            task,
            steps,
        ):
            # Step 1: Remove from PATH
            progress.update(task, current_step="PATH", step=1)
            if not remove_from_path(self.target_path):
                progress.stop()
                print_error("Failed to remove from PATH")
                if verbose:
                    print_system("❌ PATH cleanup failed")
                return False
            progress.advance(task)
            if verbose:
                print_system("✅ PATH environment variable cleaned")

            # Step 2: Remove files
            progress.update(task, current_step="Files", step=2)
            if not self._remove_files(files_to_remove, verbose):
                progress.stop()
                print_error("Failed to remove files")
                if verbose:
                    print_system("❌ File removal failed")
                return False
            progress.advance(task)
            if verbose:
                print_system(f"✅ Removed installation directory: {self.target_path}")

            # Step 3: Verification
            progress.update(task, current_step="Verification", step=3)
            if not verify_uninstallation_complete(self.target_path):
                progress.stop()
                print_error("Uninstallation verification failed")
                if verbose:
                    print_system("❌ Verification checks failed")
                return False
            progress.advance(task)
            if verbose:
                print_system("✅ Uninstallation verification completed")

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

    def _remove_files(self, files_to_remove: list[str], verbose: bool = False) -> bool:
        """Remove WOMM installation files with progress bar.

        Args:
            files_to_remove: List of files to remove for progress tracking
            verbose: Show detailed progress information

        Returns:
            True if successful, False otherwise
        """
        try:
            # Import progress bar and other utilities
            from ...ui.common.progress import create_file_copy_progress
            import shutil
            from time import sleep

            # Remove files with progress bar
            with create_file_copy_progress(
                files_to_remove, "Removing WOMM files..."
            ) as (
                progress,
                task,
                files,
            ):
                for file_path in files_to_remove:
                    # Update progress with current file
                    progress.update(task, current_file=file_path)

                    # Remove each file/directory
                    target_item = self.target_path / file_path.rstrip("/")

                    if target_item.exists():
                        if target_item.is_file():
                            target_item.unlink()
                        elif target_item.is_dir():
                            shutil.rmtree(target_item)

                    sleep(0.03)

                    if verbose:
                        from ...ui.common.console import print_system

                        print_system(f"🗑️ Removed: {file_path}")

                    # Advance progress
                    progress.advance(task)

            # Remove the root directory itself
            if self.target_path.exists():
                shutil.rmtree(self.target_path)

            return True

        except Exception as e:
            from ...ui.common.console import print_error

            print_error(f"Error removing files: {e}")
            return False
