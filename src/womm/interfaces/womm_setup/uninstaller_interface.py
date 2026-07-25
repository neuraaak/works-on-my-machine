#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UNINSTALLATION MANAGER - WOMM Uninstallation Management
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Uninstallation Manager for Works On My Machine.

Orchestrates WommUninstallerService and SystemPathService and converts their
exceptions into a Result. The interface carries no UI, including no
interactive confirmation — that belongs to the command layer, which decides
whether to proceed based on the plan and the user's answer.

Public flow mirrors the installer:
    1. ``plan_uninstall()`` — resolves the target, checks it exists, builds
       the file manifest. No progress UI needed yet.
    2. ``execute_uninstall()`` — performs the PATH cleanup/removal/verify
       steps, reporting through the supplied ``DeploymentProgressReporter``.
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
from typing import ClassVar

# Local imports
from ...exceptions.common import FileServiceError
from ...exceptions.womm_deployment import WommDeploymentServiceError
from ...services import WommUninstallerService
from ...services.system.path_service import SystemPathService
from ...shared.results import UninstallationResult, UninstallPlanResult
from ...utils.common import safe_rmtree
from ...utils.womm_setup import (
    get_default_womm_path,
    get_files_to_remove,
    verify_directory_removed,
)
from .progress import DeploymentProgressReporter, NullProgressReporter

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class WommUninstallerInterface:
    """Orchestrates the uninstallation of Works On My Machine.

    Singleton pattern for safe uninstallation operations. Pure orchestration:
    no UI, no re-raise. ``WommDeploymentServiceError``/``OSError``/
    ``ValueError`` raised by services or utils are translated into
    ``UninstallationResult``. Unexpected errors are not swallowed — they
    propagate to the top-level CLI catch-all.
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
        """Initialize the uninstallation manager (only once).

        Args:
            target: Custom target directory (default: ~/.womm)
        """
        if WommUninstallerInterface._initialized:
            return

        self.target_path = (
            Path(target).expanduser().resolve() if target else get_default_womm_path()
        )
        self.platform = platform.system()
        self._uninstallation_service = WommUninstallerService()
        self._path_service = SystemPathService()
        WommUninstallerInterface._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS - PLANNING (NO PROGRESS UI NEEDED)
    # ///////////////////////////////////////////////////////////////

    def plan_uninstall(self) -> UninstallPlanResult:
        """
        Check that a WOMM installation exists and build the removal manifest.

        Returns:
            UninstallPlanResult: ``success=False`` (with a "not found"
                message) if nothing is installed at the target; otherwise
                carries ``files_to_remove`` for the command to size its
                progress UI.
        """
        if not self.target_path.exists():
            return UninstallPlanResult(
                success=False,
                error="WOMM installation not found",
                message=f"No installation found at: {self.target_path}",
                target_path=str(self.target_path),
            )

        try:
            files_to_remove = get_files_to_remove(self.target_path)
        except (OSError, ValueError, FileServiceError) as e:
            return UninstallPlanResult(
                success=False,
                error=f"Failed to scan installation directory: {e}",
                target_path=str(self.target_path),
            )

        return UninstallPlanResult(
            success=True,
            message=f"Found {len(files_to_remove)} files to remove",
            target_path=str(self.target_path),
            files_to_remove=files_to_remove,
        )

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS - EXECUTION
    # ///////////////////////////////////////////////////////////////

    def execute_uninstall(
        self,
        plan: UninstallPlanResult,
        reporter: DeploymentProgressReporter | None = None,
        verbose: bool = False,
    ) -> UninstallationResult:
        """
        Run the uninstallation described by a successful ``plan_uninstall()``.

        Args:
            plan: Result of ``plan_uninstall()`` (must have ``success=True``)
            reporter: Stage-by-stage progress feedback; defaults to a no-op
            verbose: Unused placeholder kept for signature stability

        Returns:
            UninstallationResult: success/failure; failure carries the error.
        """
        del verbose  # no console output at this layer; kept for call-site parity
        reporter = reporter or NullProgressReporter()
        self.target_path = Path(plan.target_path)
        files_to_remove = list(plan.files_to_remove or [])

        try:
            reporter.update_layer(
                "preparation", 0, "Preparing uninstallation environment..."
            )
            reporter.complete_layer("preparation")
            reporter.update_layer("main_uninstallation", 0, "Preparation completed")

            reporter.update_layer("path_cleanup", 0, "Removing WOMM from PATH...")
            self._cleanup_path()
            reporter.complete_layer("path_cleanup")
            reporter.update_layer("main_uninstallation", 1, "PATH cleanup completed")

            self._remove_files_with_progress(files_to_remove, reporter)
            reporter.complete_layer("file_removal")
            reporter.update_layer("main_uninstallation", 2, "Files removed")

            self._verify_uninstallation_with_progress(reporter)
            reporter.complete_layer("verification")
            reporter.update_layer("main_uninstallation", 3, "Uninstallation completed!")
            reporter.complete_layer("main_uninstallation")

        except (
            WommDeploymentServiceError,
            OSError,
            ValueError,
        ) as e:
            reporter.emergency_stop(f"Uninstallation failed: {type(e).__name__}")
            details = getattr(e, "details", None)
            error = f"{e}" + (f" | Details: {details}" if details else "")
            return UninstallationResult(
                success=False,
                message="Uninstallation failed",
                error=error,
                removed_path=str(self.target_path),
                files_removed=0,
                path_cleaned=False,
                verification_passed=False,
            )

        return UninstallationResult(
            success=True,
            message="Uninstallation completed successfully",
            removed_path=str(self.target_path),
            files_removed=len(files_to_remove),
            path_cleaned=True,
            verification_passed=True,
        )

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _cleanup_path(self) -> None:
        """
        Cleanup PATH environment variable using SystemPathService.

        Raises:
            WommDeploymentServiceError: If PATH cleanup fails
        """
        result = self._path_service.remove_from_path(str(self.target_path))
        if not result.success:
            raise WommDeploymentServiceError(
                operation="cleanup",
                reason="PATH cleanup failed",
                details="remove_from_path returned failure. "
                f"Target: {self.target_path}",
            )

    # =============================================================================
    # PRIVATE METHODS - FILE OPERATIONS
    # =============================================================================

    def _remove_files_with_progress(
        self, files_to_remove: list[str], reporter: DeploymentProgressReporter
    ) -> None:
        """
        Remove WOMM installation files, reporting progress.

        Args:
            files_to_remove: Files and directories to remove, files first
            reporter: Progress feedback for the "file_removal" stage

        Raises:
            WommDeploymentServiceError: If a file or directory cannot be removed
        """
        for i, item_path in enumerate(files_to_remove):
            target_item = self.target_path / item_path.rstrip("/")
            if not target_item.exists():
                continue

            item_name = Path(item_path).name
            kind = "directory" if item_path.endswith("/") else "file"
            reporter.update_layer(
                "file_removal", i + 1, f"Removing {kind}: {item_name}"
            )

            try:
                if target_item.is_file():
                    target_item.unlink()
                elif target_item.is_dir():
                    safe_rmtree(target_item, allowed_parent=self.target_path)
            except OSError as e:
                # Covers PermissionError, a subclass of OSError.
                raise WommDeploymentServiceError(
                    operation=f"remove_{kind}",
                    reason=str(e),
                    details=f"file_path={target_item} | "
                    f"Failed to remove {kind}: {item_path}",
                ) from e

        if self.target_path.exists():
            reporter.update_layer(
                "file_removal",
                len(files_to_remove) + 1,
                "Removing installation directory",
            )
            try:
                safe_rmtree(self.target_path, allowed_parent=self.target_path.parent)
            except OSError as e:
                raise WommDeploymentServiceError(
                    operation="remove_directory",
                    reason=str(e),
                    details=f"file_path={self.target_path} | "
                    "Failed to remove installation directory",
                ) from e

    # =============================================================================
    # PRIVATE METHODS - VERIFICATION OPERATIONS
    # =============================================================================

    def _verify_uninstallation_with_progress(
        self, reporter: DeploymentProgressReporter
    ) -> None:
        """
        Verify uninstallation with progress reporting.

        Args:
            reporter: Progress feedback for the "verification" stage

        Raises:
            WommDeploymentServiceError: If any verification step fails
        """
        reporter.update_layer("verification", 0, "Checking file removal...")
        if self.target_path.exists():
            raise WommDeploymentServiceError(
                operation="verification",
                reason=f"Installation directory still exists: {self.target_path}",
                details="file_removal_check failed. "
                f"The target directory was not removed. Target: {self.target_path}",
            )

        reporter.update_layer("verification", 1, "Testing command accessibility...")
        try:
            verify_directory_removed(self.target_path)
            verification_result = (
                self._uninstallation_service.verify_uninstallation_complete(
                    self.target_path
                )
            )
        except OSError as e:
            raise WommDeploymentServiceError(
                operation="verification",
                reason=f"Verification utility failed: {e}",
                details="command_accessibility_test failed. "
                f"Target: {self.target_path}",
            ) from e

        if not verification_result.success:
            failure_message = (
                verification_result.message
                or verification_result.error
                or "Unknown error"
            )
            raise WommDeploymentServiceError(
                operation="verification",
                reason=f"Verification failed: {failure_message}",
                details="command_accessibility_test failed. "
                f"Target: {self.target_path}",
            )


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["WommUninstallerInterface"]
