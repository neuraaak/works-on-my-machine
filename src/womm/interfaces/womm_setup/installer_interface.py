#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INSTALLATION MANAGER - WOMM Installation Management
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Installation Manager for Works On My Machine.

Orchestrates WommInstallerService and SystemPathInterface and converts their
exceptions into a Result. The interface carries no UI: it does not print,
log to the console, or drive interactive elements — the command layer owns
presentation, and supplies stage-by-stage progress feedback through a
``DeploymentProgressReporter`` (see ``progress.py``). It never re-raises;
service exceptions are converted into ``InstallationResult``.

Public flow is split in two so the command can size its progress UI before
opening it:
    1. ``precheck_install()`` — validates source/target, builds the file
       manifest. No progress UI needed yet.
    2. ``execute_install()`` — performs the copy/backup/PATH/verify steps,
       reporting through the supplied ``DeploymentProgressReporter``.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import os
import platform
import shutil
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.womm_deployment import WommDeploymentServiceError
from ...services import CommandRunnerService, WommInstallerService
from ...shared.configs.womm_setup import WOMMDeploymentConfig
from ...shared.results import InstallationResult, InstallPlanResult
from ...utils.womm_setup import (
    create_installation_proof,
    create_womm_executable,
    get_current_womm_path,
    get_default_womm_path,
    verify_files_copied,
)
from ..system import SystemPathInterface
from .progress import DeploymentProgressReporter, NullProgressReporter

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class WommInstallerInterface:
    """Orchestrates the installation of Works On My Machine.

    Singleton pattern for safe installation operations. Pure orchestration:
    no UI, no re-raise. ``WommDeploymentServiceError``/``OSError``/
    ``ValueError`` raised by services or utils are translated into
    ``InstallationResult``. Unexpected errors are not swallowed — they
    propagate to the top-level CLI catch-all.
    """

    _instance: ClassVar[WommInstallerInterface | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> WommInstallerInterface:
        """Create or return the singleton instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize the installation manager (only once)."""
        if WommInstallerInterface._initialized:
            return

        # For dev installations: use project root (contains womm/, womm.py, womm.bat)
        # For pip installations: use womm package directory
        womm_package_path = get_current_womm_path()
        project_root = womm_package_path.parent

        if (project_root / "womm.py").exists() and (project_root / "womm.bat").exists():
            self.source_path = project_root
        else:
            self.source_path = womm_package_path

        self.target_path = get_default_womm_path()

        self._installation_service: WommInstallerService | None = None
        self._command_runner = CommandRunnerService()
        self.platform = platform.system()
        self._path_backup_file: str | None = None
        self._installed_files: list[str] = []

        WommInstallerInterface._initialized = True

    # ///////////////////////////////////////////////////////////////
    # SERVICE PROPERTIES (LAZY INITIALIZATION)
    # ///////////////////////////////////////////////////////////////

    @property
    def installation_service(self) -> WommInstallerService:
        """Lazy load WommInstallerService when needed."""
        if self._installation_service is None:
            self._installation_service = WommInstallerService()
        return self._installation_service

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS - PLANNING (NO PROGRESS UI NEEDED)
    # ///////////////////////////////////////////////////////////////

    def precheck_install(
        self, target: str | None = None, force: bool = False
    ) -> InstallPlanResult:
        """
        Validate source/target directories and build the file manifest.

        Args:
            target: Custom target directory (default: ~/.womm)
            force: Allow installing over an existing, non-empty target

        Returns:
            InstallPlanResult: ``success=False`` if the source structure is
                incomplete or the target already exists without ``force``;
                otherwise carries ``files_to_copy`` for the command to size
                its progress UI.
        """
        if target:
            self.target_path = Path(target).expanduser().resolve()

        if not self._precheck_source_files():
            return InstallPlanResult(
                success=False,
                error="Pre-check failed: source files missing "
                "(womm/bin or womm/assets not found)",
                source_path=str(self.source_path),
                target_path=str(self.target_path),
            )

        target_exists = self.target_path.exists()
        target_has_files = any(self.target_path.iterdir()) if target_exists else False
        if target_exists and target_has_files and not force:
            return InstallPlanResult(
                success=False,
                error="Installation directory already exists",
                message=f"Target directory: {self.target_path}. "
                "Use --force to overwrite existing installation",
                source_path=str(self.source_path),
                target_path=str(self.target_path),
            )

        try:
            files_to_copy = self._build_installation_file_list()
        except WommDeploymentServiceError as e:
            return InstallPlanResult(
                success=False,
                error=str(e),
                source_path=str(self.source_path),
                target_path=str(self.target_path),
            )

        return InstallPlanResult(
            success=True,
            message=f"Found {len(files_to_copy)} files to copy",
            source_path=str(self.source_path),
            target_path=str(self.target_path),
            files_to_copy=files_to_copy,
        )

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS - EXECUTION
    # ///////////////////////////////////////////////////////////////

    def execute_install(
        self,
        plan: InstallPlanResult,
        reporter: DeploymentProgressReporter | None = None,
        refresh_env: bool = False,
        verbose: bool = False,
    ) -> InstallationResult:
        """
        Run the installation described by a successful ``precheck_install()``.

        Args:
            plan: Result of ``precheck_install()`` (must have ``success=True``)
            reporter: Stage-by-stage progress feedback; defaults to a no-op
            refresh_env: Refresh environment variables after PATH setup
                (Windows only, disabled by default)
            verbose: Show detailed progress information

        Returns:
            InstallationResult: success/failure; failure carries the error.
        """
        reporter = reporter or NullProgressReporter()
        self.target_path = Path(plan.target_path)
        self.source_path = Path(plan.source_path)
        files_to_copy = list(plan.files_to_copy or [])
        self._installed_files = files_to_copy
        self._refresh_env = refresh_env

        try:
            reporter.update_layer(
                "preparation", 0, "Preparing installation environment..."
            )
            reporter.complete_layer("preparation")
            reporter.update_layer("main_installation", 0, "Preparation completed")

            self._copy_files_with_progress(files_to_copy, reporter, verbose)
            reporter.complete_layer("file_copy")
            reporter.update_layer("main_installation", 1, "Files copied")

            reporter.update_layer("executable", 0, "Creating womm.py executable...")
            executable_result = create_womm_executable(self.target_path)
            if not executable_result["success"]:
                error_message = str(executable_result.get("error") or "Unknown error")
                reporter.emergency_stop(f"Failed to create executable: {error_message}")
                raise WommDeploymentServiceError(
                    operation="executable_verification",
                    reason=error_message,
                    details="executable_name=womm | Failed to create WOMM executable",
                )
            reporter.complete_layer("executable")
            reporter.update_layer("main_installation", 2, "Executable created")

            reporter.update_layer("backup", 0, "Creating installation proof...")
            try:
                proof_result = create_installation_proof(self.target_path)
                if not proof_result.get("success"):
                    logger.warning("Failed to create installation proof file")
            except (WommDeploymentServiceError, OSError, ValueError) as e:
                logger.warning(f"Could not create proof file: {e}")

            reporter.update_layer(
                "backup", 0, "Backing up current PATH configuration..."
            )
            if not self._backup_path():
                reporter.emergency_stop("Failed to backup PATH")
                raise WommDeploymentServiceError(
                    operation="backup",
                    reason="Could not create PATH backup before installation",
                    details=f"path={self.target_path} | PATH backup operation failed",
                )
            reporter.complete_layer("backup")
            reporter.update_layer("main_installation", 3, "PATH backup completed")

            reporter.update_layer(
                "path_setup", 0, "Configuring PATH environment variable..."
            )
            self._setup_path(reporter)
            reporter.complete_layer("path_setup")
            reporter.update_layer("main_installation", 4, "PATH configured")

            self._verify_installation_with_progress(reporter)
            reporter.complete_layer("verification")
            reporter.update_layer("main_installation", 5, "Installation completed!")
            reporter.complete_layer("main_installation")

        except (WommDeploymentServiceError, OSError, ValueError) as e:
            reporter.emergency_stop(f"Installation failed: {type(e).__name__}")
            details = getattr(e, "details", None)
            error = f"{e}" + (f" | Details: {details}" if details else "")
            return InstallationResult(
                success=False,
                message="Installation failed",
                error=error,
                target_path=str(self.target_path),
                installation_location=str(self.target_path),
            )

        return InstallationResult(
            success=True,
            message="Installation completed successfully",
            target_path=str(self.target_path),
            installation_location=str(self.target_path),
            files_copied=len(files_to_copy),
            path_configured=True,
            executable_created=True,
            verification_passed=True,
            details={"installed_files": list(files_to_copy)},
        )

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _copy_files_with_progress(
        self,
        files_to_copy: list[str],
        reporter: DeploymentProgressReporter,
        verbose: bool = False,
    ) -> None:
        """
        Copy files from source to target directory, reporting progress.

        Args:
            files_to_copy: List of relative file paths to copy
            reporter: Progress feedback for the "file_copy" stage
            verbose: Unused placeholder kept for signature stability

        Raises:
            WommDeploymentServiceError: If a file cannot be copied
        """
        del verbose  # no console output at this layer; kept for call-site parity
        self.target_path.mkdir(parents=True, exist_ok=True)

        for i, relative_file in enumerate(files_to_copy):
            source_file = self.source_path / relative_file
            target_file = self.target_path / relative_file

            file_name = Path(relative_file).name
            reporter.update_layer("file_copy", i + 1, f"Copying: {file_name}")

            try:
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)
            except OSError as e:
                reporter.emergency_stop("File copy failed")
                raise WommDeploymentServiceError(
                    operation="file_copy",
                    reason=str(e),
                    details=f"file_path={source_file} | "
                    f"Failed at file {i + 1}/{len(files_to_copy)}: {relative_file}",
                ) from e

    # ------------------------------------------------
    # PRIVATE METHODS - PRE-INSTALLATION CHECKS
    # ------------------------------------------------

    def _precheck_source_files(self) -> bool:
        """
        Check that all required source files and directories exist.

        Returns:
            bool: True if all required components are present.
        """
        womm_dir = self.source_path / "womm"
        bin_dir = womm_dir / "bin"
        assets_dir = womm_dir / "assets"
        womm_py = self.source_path / "womm.py"
        womm_bat = self.source_path / "womm.bat"

        return (
            womm_dir.is_dir()
            and bin_dir.is_dir()
            and assets_dir.is_dir()
            and womm_py.is_file()
            and womm_bat.is_file()
        )

    def _build_installation_file_list(self) -> list[str]:
        """
        Build list of files to copy during installation.

        Returns:
            List of relative file paths to copy

        Raises:
            WommDeploymentServiceError: If file list building fails
        """
        files: list[str] = []
        try:
            womm_dir = self.source_path / "womm"
            for root, _dirs, file_names in os.walk(womm_dir):
                for file_name in file_names:
                    file_path = Path(root) / file_name
                    relative_path = file_path.relative_to(self.source_path)
                    files.append(str(relative_path))

            womm_py = self.source_path / "womm.py"
            womm_bat = self.source_path / "womm.bat"
            if womm_py.exists():
                files.append("womm.py")
            if womm_bat.exists():
                files.append("womm.bat")
        except OSError as e:
            raise WommDeploymentServiceError(
                operation="install",
                reason=f"Failed to build file list: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

        return sorted(files)

    # ------------------------------------------------
    # PRIVATE METHODS - PATH OPERATIONS
    # ------------------------------------------------

    def _setup_path(self, reporter: DeploymentProgressReporter) -> None:
        """
        Setup PATH environment variable using SystemPathInterface.

        Args:
            reporter: Progress feedback used for the emergency-stop signal

        Raises:
            WommDeploymentServiceError: If PATH setup fails
        """
        path_manager = SystemPathInterface(target=str(self.target_path))
        result = path_manager.add_to_path()

        if not result.success:
            error_msg = result.error or result.message or "Unknown error"
            logger.error(f"PATH setup returned failure: {result}")
            reporter.emergency_stop(f"PATH setup failed: {error_msg}")
            raise WommDeploymentServiceError(
                operation="path_setup",
                reason="PATH setup failed",
                details=f"path={self.target_path} | PathManager error: {error_msg}",
            )

    def _backup_path(self) -> bool:
        """
        Backup current PATH configuration using SystemPathInterface.

        Returns:
            True if backup successful, False otherwise

        Raises:
            WommDeploymentServiceError: If PATH backup fails unexpectedly
        """
        path_manager = SystemPathInterface(target=str(self.target_path))
        backup_result = path_manager.create_backup()

        if not backup_result.success:
            raise WommDeploymentServiceError(
                operation="backup",
                reason="PATH backup failed",
                details=f"path={self.target_path} | "
                f"PathManager backup error: {backup_result.error}",
            )

        if backup_result.backup_file:
            self._path_backup_file = str(Path(backup_result.backup_file).resolve())
        return True

    # ------------------------------------------------
    # PRIVATE METHODS - VERIFICATION OPERATIONS
    # ------------------------------------------------

    def _verify_installation_with_progress(
        self, reporter: DeploymentProgressReporter
    ) -> None:
        """
        Verify installation with progress reporting.

        Args:
            reporter: Progress feedback for the "verification" stage

        Raises:
            WommDeploymentServiceError: If any verification step fails
        """
        reporter.update_layer("verification", 0, "Checking file integrity...")
        try:
            verify_files_copied(
                self.source_path, self.target_path, self._installed_files
            )
        except OSError as e:
            reporter.emergency_stop("File verification failed")
            raise WommDeploymentServiceError(
                operation="file_integrity",
                reason=str(e),
                details=f"file_path={self.target_path} | Files are missing or corrupted",
            ) from e

        reporter.update_layer("verification", 1, "Verifying essential files...")
        for essential_file in WOMMDeploymentConfig.ESSENTIAL_FILES:
            file_path = self.target_path / essential_file
            if not file_path.exists():
                reporter.emergency_stop("Essential file missing")
                raise WommDeploymentServiceError(
                    operation="essential_files",
                    reason=f"Essential file missing: {essential_file}",
                    details=f"file_path={file_path} | Required file not found at {file_path}",
                )

        reporter.update_layer("verification", 2, "Testing command accessibility...")
        try:
            result = self.installation_service.verify_commands_accessible(
                str(self.target_path)
            )
            if not result.success:
                raise WommDeploymentServiceError(
                    operation="executable_verification",
                    reason=result.message or "Command verification failed",
                    details=f"executable_name=womm | {result.error or ''}",
                )
        except WommDeploymentServiceError as e:
            if self.platform == "Windows":
                # PATH visibility lags a fresh install on Windows; a working
                # local executable (checked by the service before raising)
                # is enough — WOMM will be reachable in new terminal sessions.
                reporter.update_layer(
                    "verification",
                    2,
                    "Command verification failed but continuing on Windows "
                    "(PATH timing issue) - WOMM will be available in new "
                    "terminal sessions",
                )
            else:
                reporter.emergency_stop("Command verification failed")
                raise WommDeploymentServiceError(
                    operation="executable_verification",
                    reason=str(e),
                    details="executable_name=womm | WOMM commands are not accessible",
                ) from e

        reporter.update_layer("verification", 3, "Verifying PATH configuration...")
        try:
            self.installation_service.verify_path_configuration(str(self.target_path))
        except WommDeploymentServiceError as e:
            reporter.emergency_stop("PATH verification failed")
            raise WommDeploymentServiceError(
                operation="path_configuration",
                reason=str(e),
                details=f"path={self.target_path} | "
                "PATH environment variable is not configured correctly",
            ) from e


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["WommInstallerInterface"]
