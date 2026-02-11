#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UNINSTALLATION MANAGER - WOMM Uninstallation Management
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Uninstallation Manager for Works On My Machine.
Removes WOMM from the system and cleans up PATH entries.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import platform
from pathlib import Path
from threading import Lock
from time import sleep
from typing import ClassVar

# Third-party imports
from rich.progress import TaskID

# Local imports
from ...exceptions.common import DirectoryAccessError, FileScanError
from ...exceptions.system import (
    FileSystemServiceError,
    RegistryServiceError,
    UserPathServiceError,
)
from ...exceptions.womm_deployment import (
    DeploymentFileServiceError,
    DeploymentUtilityError,
    UninstallerInterfaceError,
    VerificationServiceError,
    WommInstallerError,
    WommUninstallerError,
)
from ...services import WommUninstallerService
from ...services.system.path_service import SystemPathService
from ...shared.results import UninstallationResult
from ...ui.common import confirm, ezconsole, ezprinter
from ...utils.womm_setup import (
    get_default_womm_path,
    get_files_to_remove,
    verify_directory_removed,
)

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class WommUninstallerInterface:
    """Manages the uninstallation process for Works On My Machine.

    Singleton pattern for safe uninstallation operations.
    """

    _instance: ClassVar[WommUninstallerInterface | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls, _target: str | None = None) -> WommUninstallerInterface:
        """Create or return the singleton instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, target: str | None = None) -> None:
        """
        Initialize the uninstallation manager.

        Args:
            target: Custom target directory (default: ~/.womm)

        Raises:
            UninstallationManagerInterfaceError: If uninstallation manager initialization fails
        """
        if WommUninstallerInterface._initialized:
            return

        try:
            if target:
                self.target_path = Path(target).expanduser().resolve()
            else:
                try:
                    self.target_path = get_default_womm_path()
                except (DeploymentUtilityError, WommInstallerError):
                    # Re-raise our custom exceptions
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise UninstallerInterfaceError(
                        message=f"Failed to get target path: {e}",
                        operation="initialization",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

            self.platform = platform.system()
            self._uninstallation_service = WommUninstallerService()
            self._path_service = SystemPathService()
            WommUninstallerInterface._initialized = True

        except UninstallerInterfaceError:
            # Re-raise interface exceptions
            raise
        except (
            WommUninstallerError,
            DeploymentUtilityError,
            WommInstallerError,
        ):
            # Convert service exceptions to interface exceptions
            raise UninstallerInterfaceError(
                message="Failed to initialize uninstallation manager",
                operation="initialization",
                details="Exception type: UninstallationManagerError",
            ) from WommUninstallerError(
                message="Failed to initialize",
                details="Service initialization error",
            )
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Failed to initialize UninstallationManager: {e}")
            raise UninstallerInterfaceError(
                message=f"Failed to initialize uninstallation manager: {e}",
                operation="initialization",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def uninstall(
        self,
        force: bool = False,
        verbose: bool = False,
    ) -> UninstallationResult:
        """
        Uninstall Works On My Machine from the user's system.

        Args:
            force: Force uninstallation without confirmation
            verbose: Show detailed progress information

        Returns:
            UninstallationResult: Result of the uninstallation operation

        Raises:
            UninstallationManagerInterfaceError: If uninstallation fails
            UninstallationUtilityError: If utility operations fail
            UninstallationFileError: If file operations fail
            UninstallationVerificationInterfaceError: If verification fails
        """
        try:
            files_to_remove: list[str] = []
            ezprinter.print_header("W.O.M.M Uninstallation")

            # Check target directory existence
            with ezprinter.create_spinner_with_status(
                "Checking target directory..."
            ) as (
                progress,
                task,
            ):
                task_id = TaskID(task)
                progress.update(
                    task_id, status="Analyzing uninstallation requirements..."
                )

                # Check if WOMM is installed
                if not self.target_path.exists():
                    progress.stop()

                    warning_content = (
                        "WOMM not found.\n\n"
                        f"No installation found at: {self.target_path}\n"
                        "WOMM may not be installed or may be in a different location"
                    )
                    warning_panel = ezprinter.create_panel(
                        warning_content,
                        title="✅ Uninstallation Complete",
                        style="bright_orange",
                        border_style="bright_green",
                        padding=(1, 1),
                    )
                    ezconsole.print("")
                    ezconsole.print(warning_panel)
                    return UninstallationResult(
                        success=False,
                        error="WOMM installation not found",
                        removed_path=str(self.target_path),
                        files_removed=0,
                        path_cleaned=False,
                        verification_passed=False,
                    )
                else:
                    progress.update(
                        task_id,
                        status=f"Found installation at: {self.target_path}",
                    )

            # Check if force is required
            if not force:
                # Show warning panel for uninstallation
                ezconsole.print("")

                warning_content = (
                    f"This will completely remove WOMM from {self.target_path}.\n\n"
                    "This action cannot be undone."
                )
                warning_panel = ezprinter.create_warning_panel(
                    title="Uninstallation Confirmation",
                    content=warning_content,
                    border_style="bright_green",
                    padding=(1, 1),
                    style="bright_orange",
                )
                ezconsole.print("")
                ezconsole.print(warning_panel)

                # Ask for confirmation
                if not confirm(
                    "Do you want to continue and remove WOMM completely?",
                    default=False,
                ):
                    ezconsole.print("❌ Uninstallation cancelled", style="red")
                    return UninstallationResult(
                        success=False,
                        error="Uninstallation cancelled by user",
                        removed_path=str(self.target_path),
                        files_removed=0,
                        path_cleaned=False,
                        verification_passed=False,
                    )

                ezconsole.print("")
                ezprinter.system("Proceeding with uninstallation...")

            # Dry run message is already handled in the directory check section

            # Get list of files to remove
            ezconsole.print("")

            with ezprinter.create_spinner_with_status(
                "Analyzing installed files..."
            ) as (
                progress,
                task,
            ):
                task_id = TaskID(task)
                progress.update(task_id, status="Scanning installation directory...")
                try:
                    files_to_remove = get_files_to_remove(self.target_path)
                except (
                    DeploymentUtilityError,
                    FileScanError,
                    DirectoryAccessError,
                ):
                    # Re-raise our custom exceptions
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise WommUninstallerError(
                        message=f"Failed to get files to remove: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                progress.update(
                    task_id,
                    status=f"Found {len(files_to_remove)} files to remove",
                )

            # Define uninstallation stages with DynamicLayeredProgress
            # Color palette: unified cyan for all steps, semantic colors for states
            stages = [
                {
                    "name": "main_uninstallation",
                    "type": "main",
                    "steps": [
                        "Preparation",
                        "PATH Cleanup",
                        "File Removal",
                        "Verification",
                    ],
                    "description": "WOMM Uninstallation Progress",
                    "style": "bold bright_white",
                },
                {
                    "name": "preparation",
                    "type": "spinner",
                    "description": "Preparing uninstallation environment...",
                    "style": "bright_blue",
                },
                {
                    "name": "path_cleanup",
                    "type": "spinner",
                    "description": "Removing from PATH...",
                    "style": "bright_blue",
                },
                {
                    "name": "file_removal",
                    "type": "progress",
                    "total": len(files_to_remove),
                    "description": "Removing installation files...",
                    "style": "bright_blue",
                },
                {
                    "name": "verification",
                    "type": "steps",
                    "steps": [
                        "File removal check",
                        "Command accessibility test",
                    ],
                    "description": "Verifying uninstallation...",
                    "style": "bright_blue",
                },
            ]

            ezconsole.print("")
            with ezprinter.create_dynamic_layered_progress(stages) as progress:
                try:
                    # Stage 1: Preparation
                    prep_messages = [
                        "Analyzing uninstallation requirements...",
                        "Checking installation integrity...",
                        "Validating removal permissions...",
                        "Preparing cleanup operations...",
                    ]

                    for msg in prep_messages:
                        progress.update_layer("preparation", 0, msg)
                        sleep(0.2)

                    # Complete preparation
                    progress.complete_layer("preparation")

                    # Update main uninstallation progress
                    progress.update_layer(
                        "main_uninstallation", 0, "Preparation completed"
                    )
                    sleep(0.3)

                    # Stage 2: PATH Cleanup
                    progress.update_layer(
                        "path_cleanup", 0, "Removing WOMM from PATH..."
                    )
                    try:
                        if not self._cleanup_path():
                            progress.emergency_stop("Failed to remove from PATH")
                            raise WommUninstallerError(
                                message="Failed to remove from PATH",
                                operation="cleanup",
                                details=(
                                    "remove_from_path utility returned False. "
                                    f"Target: {self.target_path}"
                                ),
                            )
                    except (WommUninstallerError, DeploymentUtilityError):
                        # Re-raise our custom exceptions
                        raise
                    except Exception as e:
                        # Wrap unexpected external exceptions
                        raise WommUninstallerError(
                            message=f"Failed to cleanup PATH: {e}",
                            details=f"Exception type: {type(e).__name__}",
                        ) from e

                    progress.update_layer("path_cleanup", 0, "PATH cleanup completed")
                    sleep(0.2)

                    # Complete PATH cleanup
                    progress.complete_layer("path_cleanup")

                    # Update main uninstallation progress
                    progress.update_layer(
                        "main_uninstallation", 1, "PATH cleanup completed"
                    )
                    sleep(0.3)

                    # Stage 3: File Removal
                    try:
                        self._remove_files_with_progress(
                            files_to_remove, progress, verbose
                        )
                    except (DeploymentFileServiceError, DeploymentUtilityError):
                        # Re-raise our custom exceptions
                        raise
                    except Exception as e:
                        # Wrap unexpected external exceptions
                        raise WommUninstallerError(
                            message=f"Failed to remove files: {e}",
                            details=f"Exception type: {type(e).__name__}",
                        ) from e

                    # Complete file removal
                    progress.complete_layer("file_removal")

                    # Update main uninstallation progress
                    progress.update_layer("main_uninstallation", 2, "Files removed")
                    sleep(0.3)

                    # Stage 4: Verification
                    try:
                        self._verify_uninstallation_with_progress(progress)
                    except (
                        WommUninstallerError,
                        DeploymentUtilityError,
                    ):
                        # Re-raise our custom exceptions
                        raise
                    except Exception as e:
                        # Wrap unexpected external exceptions
                        raise WommUninstallerError(
                            message=f"Failed to verify uninstallation: {e}",
                            details=f"Exception type: {type(e).__name__}",
                        ) from e

                    # Complete verification
                    progress.complete_layer("verification")

                    # Complete main uninstallation progress
                    progress.update_layer(
                        "main_uninstallation", 3, "Uninstallation completed!"
                    )
                    sleep(0.3)

                    # Complete and remove main uninstallation layer
                    progress.complete_layer("main_uninstallation")

                except (
                    WommInstallerError,
                    DeploymentFileServiceError,
                    WommUninstallerError,
                    DeploymentUtilityError,
                    FileScanError,
                    DirectoryAccessError,
                    VerificationServiceError,
                    UserPathServiceError,
                    RegistryServiceError,
                    FileSystemServiceError,
                ) as e:
                    # Stop progress first, then print error details
                    progress.emergency_stop(
                        f"Uninstallation failed: {type(e).__name__}"
                    )

                    ezprinter.error(
                        f"Uninstallation failed at stage '{getattr(e, 'stage', 'unknown')}': {e}"
                    )
                    if hasattr(e, "details") and e.details:
                        ezprinter.error(f"Details: {e.details}")

                    # Re-raise our custom exceptions
                    raise
                except Exception as e:
                    # Handle any other unexpected errors
                    progress.emergency_stop("Unexpected error during uninstallation")

                    ezprinter.error(f"Unexpected error during uninstallation: {e}")

                    raise WommUninstallerError(
                        message=f"Unexpected error during uninstallation: {e}",
                        details="This is an unexpected error that should be reported",
                    ) from e

            ezconsole.print("")
            ezprinter.success("✅ W.O.M.M uninstallation completed successfully!")
            ezprinter.system(f"📁 Removed from: {self.target_path}")

            # Show completion panel
            completion_content = (
                "WOMM has been successfully removed from your system.\n\n"
                "To complete the cleanup:\n"
                "• Restart your terminal for PATH changes to take effect\n"
                "• Remove any remaining WOMM references from your shell config files\n\n"
                "Thank you for using Works On My Machine!"
            )

            completion_panel = ezprinter.create_success_panel(
                title="Uninstallation Complete",
                content=completion_content,
                border_style="bright_green",
                padding=(1, 1),
            )
            ezconsole.print("")
            ezconsole.print(completion_panel)

            return UninstallationResult(
                success=True,
                message="Uninstallation completed successfully",
                removed_path=str(self.target_path),
                files_removed=len(files_to_remove),
                path_cleaned=True,
                verification_passed=True,
            )

        except (
            WommUninstallerError,
            DeploymentUtilityError,
            DeploymentFileServiceError,
        ):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in uninstall: {e}")
            raise WommUninstallerError(
                message=f"Uninstallation failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _cleanup_path(self) -> bool:
        """
        Cleanup PATH environment variable using path management utils.

        Returns:
            True if successful, False otherwise

        Raises:
            WommUninstallerError: If PATH cleanup fails
            UninstallationUtilityError: If utility operations fail
        """
        try:
            try:
                result = self._path_service.remove_from_path(str(self.target_path))
            except (
                UserPathServiceError,
                RegistryServiceError,
                FileSystemServiceError,
            ):
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                # Wrap unexpected external exceptions
                raise WommUninstallerError(
                    message=f"remove_from_path utility failed: {e}",
                    operation="cleanup",
                    details=f"Exception type: {type(e).__name__}",
                ) from e

            sleep(0.5)

            if not result.success:
                ezprinter.error("PATH cleanup failed: remove_from_path returned False")

                raise WommUninstallerError(
                    message="PATH cleanup failed",
                    operation="cleanup",
                    details=(
                        "remove_from_path utility returned False. "
                        f"Target: {self.target_path}"
                    ),
                )

            return True

        except (
            UserPathServiceError,
            RegistryServiceError,
            FileSystemServiceError,
        ):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            ezprinter.error(f"Unexpected error during PATH cleanup: {e}")

            raise WommUninstallerError(
                message=f"Unexpected error during PATH cleanup: {e}",
                operation="cleanup",
                details="This is an unexpected error that should be reported",
            ) from e

    # =============================================================================
    # PRIVATE METHODS - FILE OPERATIONS
    # =============================================================================

    def _remove_files_with_progress(
        self, files_to_remove: list[str], progress, verbose: bool = False
    ) -> bool:
        """
        Remove WOMM installation files with progress tracking.

        Args:
            files_to_remove: List of files and directories to remove for progress tracking
            progress: DynamicLayeredProgress instance
            verbose: Show detailed progress information

        Returns:
            True if successful

        Raises:
            UninstallationFileError: If file removal operations fail
            UninstallationUtilityError: If utility operations fail
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
                            ezprinter.system(f"🗑️ Removed file: {item_path}")
                    elif target_item.is_dir():
                        shutil.rmtree(target_item)
                        sleep(0.02)
                        if verbose:
                            ezprinter.system(f"🗑️ Removed directory: {item_path}")
                except PermissionError as e:
                    if target_item.is_file():
                        raise DeploymentFileServiceError(
                            operation="remove_file",
                            file_path=str(target_item),
                            message=f"Permission denied: {e}",
                            details=f"Cannot remove file due to permissions: {item_path}",
                        ) from e
                    else:
                        raise DeploymentFileServiceError(
                            operation="remove_directory",
                            file_path=str(target_item),
                            message=f"Permission denied: {e}",
                            details=f"Cannot remove directory due to permissions: {item_path}",
                        ) from e
                except OSError as e:
                    if target_item.is_file():
                        raise DeploymentFileServiceError(
                            operation="remove_file",
                            file_path=str(target_item),
                            message=f"OS error: {e}",
                            details=f"Failed to remove file: {item_path}",
                        ) from e
                    else:
                        raise DeploymentFileServiceError(
                            operation="remove_directory",
                            file_path=str(target_item),
                            message=f"OS error: {e}",
                            details=f"Failed to remove directory: {item_path}",
                        ) from e

            # Finally remove the root directory itself
            if self.target_path.exists():
                progress.update_layer(
                    "file_removal",
                    len(files_to_remove) + 1,
                    "Removing installation directory",
                )
                try:
                    shutil.rmtree(self.target_path)
                    sleep(0.1)

                    if verbose:
                        ezprinter.system(
                            f"🗑️ Removed installation directory: {self.target_path}"
                        )
                except PermissionError as e:
                    raise DeploymentFileServiceError(
                        operation="remove_directory",
                        file_path=str(self.target_path),
                        message=f"Permission denied: {e}",
                        details="Cannot remove installation directory due to permissions",
                    ) from e
                except OSError as e:
                    raise DeploymentFileServiceError(
                        operation="remove_directory",
                        file_path=str(self.target_path),
                        message=f"OS error: {e}",
                        details="Failed to remove installation directory",
                    ) from e

            return True

        except (DeploymentFileServiceError, DeploymentUtilityError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Convert unexpected errors to our exception type
            raise DeploymentFileServiceError(
                operation="file_removal",
                file_path=str(self.target_path),
                message=f"Unexpected error during file removal: {e}",
                details="This is an unexpected error that should be reported",
            ) from e

    # =============================================================================
    # PRIVATE METHODS - VERIFICATION OPERATIONS
    # =============================================================================

    def _verify_uninstallation_with_progress(self, progress) -> bool:
        """
        Verify uninstallation with progress tracking.

        Args:
            progress: DynamicLayeredProgress instance

        Returns:
            True if verification passed

        Raises:
            UninstallationManagerVerificationError: If verification operations fail
            UninstallationUtilityError: If utility operations fail
        """
        try:
            # Step 1: File removal check
            progress.update_layer("verification", 0, "Checking file removal...")
            if self.target_path.exists():
                raise WommUninstallerError(
                    message=f"Installation directory still exists: {self.target_path}",
                    operation="verification",
                    details=(
                        "file_removal_check failed. "
                        "The target directory was not removed during uninstallation. "
                        f"Target: {self.target_path}"
                    ),
                )
            sleep(0.2)

            # Step 2: Command accessibility test
            progress.update_layer("verification", 1, "Testing command accessibility...")
            try:
                # Verify directory removal (pure utility)
                verify_directory_removed(self.target_path)

                # Verify command removal (service)
                verification_result = (
                    self._uninstallation_service.verify_uninstallation_complete(
                        self.target_path
                    )
                )
            except (VerificationServiceError, DeploymentUtilityError):
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                raise WommUninstallerError(
                    message=f"Verification utility failed: {e}",
                    operation="verification",
                    details=(
                        "command_accessibility_test failed. "
                        "The verification utility function raised an exception. "
                        f"Target: {self.target_path}"
                    ),
                ) from e

            if not verification_result.success:
                failure_message = (
                    verification_result.message
                    or verification_result.error
                    or "Unknown error"
                )
                raise WommUninstallerError(
                    message=f"Verification failed: {failure_message}",
                    operation="verification",
                    details=(
                        "command_accessibility_test failed. "
                        "The verification utility returned a failure status. "
                        f"Target: {self.target_path}"
                    ),
                )
            sleep(0.2)

            return True

        except (WommUninstallerError, DeploymentUtilityError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Convert unexpected errors to our exception type
            raise WommUninstallerError(
                message=f"Unexpected error during verification: {e}",
                operation="verification",
                details="This is an unexpected error that should be reported",
            ) from e
