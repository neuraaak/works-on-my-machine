#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INSTALLATION MANAGER - WOMM Installation Management
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Installation Manager for Works On My Machine.

This module handles the complete installation process of WOMM to the user's
home directory, using utility functions for core operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import contextlib
import json
import logging
import os
import platform
import shutil
import tempfile
from pathlib import Path
from threading import Lock
from time import sleep
from typing import ClassVar

# Third-party imports
from rich.progress import TaskID

# Local imports
from ...exceptions.system import (
    FileSystemServiceError,
    RegistryServiceError,
    UserPathServiceError,
)
from ...exceptions.womm_deployment import (
    InstallerInterfaceError,
    WommDeploymentServiceError,
)
from ...services import CommandRunnerService, WommInstallerService
from ...shared.configs.womm_setup import WOMMDeploymentConfig
from ...shared.results import InstallationResult
from ...ui.common import ezprinter
from ...utils.womm_setup import (
    create_installation_proof,
    create_womm_executable,
    get_current_womm_path,
    get_default_womm_path,
    verify_files_copied,
)
from ..system import SystemEnvironmentInterface, SystemPathInterface

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class WommInstallerInterface:
    """Manages the installation process for Works On My Machine.

    Singleton pattern for safe installation operations.

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
        """
        Initialize the installation manager.

        Raises:
            InstallationManagerInterfaceError: If installation manager initialization fails
        """
        if WommInstallerInterface._initialized:
            return

        try:
            # Initialize utility modules
            try:
                # Determine source path for installation
                # For dev installations: use project root (contains womm/, womm.py, womm.bat)
                # For pip installations: use womm package directory

                womm_package_path = get_current_womm_path()
                project_root = womm_package_path.parent

                # Check if we're in dev mode (project root has womm.py and womm.bat)
                if (project_root / "womm.py").exists() and (
                    project_root / "womm.bat"
                ).exists():
                    # Dev installation: use project root as source
                    self.source_path = project_root
                else:
                    # Pip installation: use womm package directory as source
                    self.source_path = womm_package_path

                self.target_path = get_default_womm_path()
            except (WommDeploymentServiceError, OSError, ValueError):
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                # Wrap unexpected external exceptions
                raise InstallerInterfaceError(
                    message=f"Failed to initialize paths: {e}",
                    operation="initialization",
                    details=f"Exception type: {type(e).__name__}",
                ) from e

            # Initialize services
            self._installation_service: WommInstallerService | None = None
            self._command_runner = CommandRunnerService()

            self.actions = []
            self.platform = platform.system()
            # Track backup file for potential rollback after failures
            self._path_backup_file: str | None = None
            # Store list of files installed
            self._installed_files: list[str] = []

            WommInstallerInterface._initialized = True

        except InstallerInterfaceError:
            # Re-raise interface exceptions
            raise
        except (WommDeploymentServiceError, OSError, ValueError):
            # Convert service exceptions to interface exceptions
            raise InstallerInterfaceError(
                message="Failed to initialize installation manager",
                operation="initialization",
                details="Exception during initialization",
            ) from WommDeploymentServiceError(
                operation="install",
                reason="Failed to initialize",
                details="Service initialization error",
            )
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.exception("Failed to initialize InstallationManager")
            raise InstallerInterfaceError(
                message=f"Installation manager initialization failed: {e}",
                operation="initialization",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # SERVICE PROPERTIES (LAZY INITIALIZATION)
    # ///////////////////////////////////////////////////////////////

    @property
    def installation_service(self) -> WommInstallerService:
        """Lazy load WOMMInstallerService when needed."""
        if self._installation_service is None:
            self._installation_service = WommInstallerService()
        return self._installation_service

    @installation_service.setter
    def installation_service(self, value: WommInstallerService | None) -> None:
        """Set the installation service."""
        self._installation_service = value

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def install(
        self,
        target: str | None = None,
        force: bool = False,
        _backup: bool = True,
        verbose: bool = False,
        refresh_env: bool = False,
    ) -> InstallationResult:
        """
        Install Works On My Machine to the user's system.

        Args:
            target: Custom target directory (default: ~/.womm)
            force: Force installation even if already installed
            backup: Create backup before installation
            verbose: Show detailed progress information
            refresh_env: Refresh environment variables after PATH setup (Windows only, disabled by default)

        Returns:
            InstallationResult: Result of the installation operation

        Raises:
            InstallationManagerInterfaceError: If installation fails
            InstallationUtilityError: If utility operations fail
            InstallationFileError: If file operations fail
            InstallationPathError: If PATH operations fail
            InstallationSystemError: If system operations fail
            InstallationVerificationInterfaceError: If verification fails
        """
        try:
            # Override target path if specified
            if target:
                self.target_path = Path(target).expanduser().resolve()

            # Store refresh_env setting for use in _setup_path
            self._refresh_env = refresh_env

            ezprinter.print_header("W.O.M.M Installation")

            # ============================================================================
            # PHASE 1: PRE-CHECK - Verify source files and structure
            # ============================================================================
            with ezprinter.create_spinner_with_status(
                "Pre-checking installation requirements..."
            ) as (progress, task):
                task_id = TaskID(task)
                progress.update(task_id, status="Verifying source structure...")
                # Pre-check will validate bin, assets, and project structure
                precheck_result = self._precheck_source_files(verbose)
                if not precheck_result:
                    raise InstallerInterfaceError(
                        message="Pre-check failed: Source files missing",
                        operation="precheck",
                        details="womm/bin or womm/assets missing",
                    )
                progress.update(task_id, status="Source structure verified")

            ezprinter._console.print("")

            # ============================================================================
            # PRE-VALIDATION: Check target directory before starting progress
            # ============================================================================
            target_exists = self.target_path.exists()
            target_has_files = (
                any(self.target_path.iterdir()) if target_exists else False
            )

            # Check target directory existence
            # Check if already installed BEFORE starting progress spinner
            if target_exists and target_has_files and not force:
                ezprinter.print_panel(
                    "Installation directory already exists\n\n"
                    f"Target directory: {self.target_path}\n"
                    "Use --force to overwrite existing installation"
                )
                return InstallationResult(
                    success=False,
                    message="Installation directory already exists",
                    error="Installation directory already exists",
                    target_path=str(self.target_path),
                    installation_location=str(self.target_path),
                )

            # Only start progress spinner if checks passed
            with ezprinter.create_spinner_with_status(
                "Checking target directory..."
            ) as (
                progress,
                task,
            ):
                task_id = TaskID(task)
                progress.update(
                    task_id, status="Analyzing installation requirements..."
                )
                # Validation passed, ready to continue with installation

            # ============================================================================
            # PHASE 2: ANALYZE SOURCE FILES - Build list of files to copy
            # ============================================================================

            ezprinter._console.print("")

            with ezprinter.create_spinner_with_status("Analyzing source files...") as (
                progress,
                task,
            ):
                task_id = TaskID(task)
                progress.update(task_id, status="Scanning source directory...")
                try:
                    files_to_copy = self._build_installation_file_list()
                except Exception as e:
                    raise WommDeploymentServiceError(
                        operation="install",
                        reason=f"Failed to build file list: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                progress.update(
                    task_id, status=f"Found {len(files_to_copy)} files to copy"
                )

            # Store files list for later verification
            self._installed_files = files_to_copy

            # Define installation stages with DynamicLayeredProgress
            # Color palette: unified cyan for all steps, semantic colors for states
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
                    "style": "bright_blue",
                },
                {
                    "name": "file_copy",
                    "type": "progress",
                    "total": len(files_to_copy),
                    "description": "Copying project files...",
                    "style": "bright_blue",
                },
                {
                    "name": "executable",
                    "type": "spinner",
                    "description": "Creating executable script...",
                    "style": "bright_blue",
                },
                {
                    "name": "backup",
                    "type": "spinner",
                    "description": "Creating PATH backup...",
                    "style": "bright_blue",
                },
                {
                    "name": "path_setup",
                    "type": "spinner",
                    "description": "Configuring PATH environment...",
                    "style": "bright_blue",
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
                    "style": "bright_blue",
                },
            ]

            ezprinter._console.print("")
            with ezprinter.create_dynamic_layered_progress(stages) as progress:
                try:
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

                    # Update main installation progress
                    progress.update_layer(
                        "main_installation", 0, "Preparation completed"
                    )
                    sleep(0.3)

                    # Stage 2: Copy files
                    self._copy_files_with_progress(files_to_copy, progress, verbose)

                    # Complete file copy
                    progress.complete_layer("file_copy")

                    # Update main installation progress
                    progress.update_layer("main_installation", 1, "Files copied")
                    sleep(0.3)

                    # Stage 3: Create executable
                    progress.update_layer(
                        "executable", 0, "Creating womm.py executable..."
                    )
                    try:
                        executable_result = create_womm_executable(self.target_path)
                    except (WommDeploymentServiceError, OSError, ValueError):
                        # Re-raise our custom exceptions
                        raise
                    except Exception as e:
                        # Wrap unexpected external exceptions
                        raise WommDeploymentServiceError(
                            operation="install",
                            reason=f"Failed to create executable: {e}",
                            details=f"Exception type: {type(e).__name__}",
                        ) from e

                    if not executable_result["success"]:
                        error_value = executable_result.get("error")
                        error_message = (
                            str(error_value) if error_value else "Unknown error"
                        )
                        progress.emergency_stop(
                            f"Failed to create executable: {error_message}"
                        )
                        raise WommDeploymentServiceError(
                            operation="executable_verification",
                            reason=error_message,
                            details="executable_name=womm"
                            + " | "
                            + "Failed to create WOMM executable",
                        )

                    progress.update_layer(
                        "executable", 0, "Creating womm.bat wrapper..."
                    )
                    sleep(0.2)

                    # Complete executable creation
                    progress.complete_layer("executable")

                    # Update main installation progress
                    progress.update_layer("main_installation", 2, "Executable created")
                    sleep(0.3)

                    # Stage 3.5: Create installation proof
                    progress.update_layer("backup", 0, "Creating installation proof...")
                    try:
                        proof_result = create_installation_proof(self.target_path)
                        if not proof_result.get("success"):
                            logger.warning("Failed to create installation proof file")
                    except (WommDeploymentServiceError, OSError, ValueError) as e:
                        logger.warning(f"Could not create proof file: {e}")
                    except Exception as e:
                        logger.warning(f"Unexpected error creating proof: {e}")
                    sleep(0.1)

                    # Stage 4: Backup PATH
                    progress.update_layer(
                        "backup", 0, "Backing up current PATH configuration..."
                    )
                    try:
                        if not self._backup_path():
                            progress.emergency_stop("Failed to backup PATH")
                            raise WommDeploymentServiceError(
                                operation="backup",
                                reason="Could not create PATH backup before installation",
                                details=f"path={str(self.target_path)}"
                                + " | "
                                + "PATH backup operation failed",
                            )
                    except (WommDeploymentServiceError, OSError, ValueError):
                        # Re-raise our custom exceptions
                        raise
                    except Exception as e:
                        # Wrap unexpected external exceptions
                        raise WommDeploymentServiceError(
                            operation="install",
                            reason=f"Failed to backup PATH: {e}",
                            details=f"Exception type: {type(e).__name__}",
                        ) from e

                    progress.update_layer("backup", 0, "PATH backup completed")
                    sleep(0.2)

                    # Complete backup
                    progress.complete_layer("backup")

                    # Update main installation progress
                    progress.update_layer(
                        "main_installation", 3, "PATH backup completed"
                    )
                    sleep(0.3)

                    # Stage 5: Setup PATH
                    progress.update_layer(
                        "path_setup", 0, "Configuring PATH environment variable..."
                    )
                    try:
                        self._setup_path()  # Always raises exception on failure, never returns False
                    except WommDeploymentServiceError as e:
                        # Re-raise system exception with full details
                        progress.emergency_stop(
                            f"PATH setup failed: {type(e).__name__}"
                        )
                        ezprinter.error(f"PATH setup error: {e.message}")
                        if e.details and e.details != e.message:
                            ezprinter.error(f"Details: {e.details}")
                        raise
                    except (OSError, ValueError):
                        # Let filesystem/validation errors propagate unwrapped
                        raise
                    except Exception as e:
                        # Wrap unexpected external exceptions
                        progress.emergency_stop("Unexpected error during PATH setup")
                        logger.exception("Unexpected error in PATH setup")
                        raise WommDeploymentServiceError(
                            operation="install",
                            reason=f"Failed to setup PATH: {e}",
                            details=f"Exception type: {type(e).__name__}",
                        ) from e

                    progress.update_layer(
                        "path_setup", 0, "PATH configuration completed"
                    )
                    sleep(0.2)

                    # Complete PATH setup
                    progress.complete_layer("path_setup")

                    # Update main installation progress
                    progress.update_layer("main_installation", 4, "PATH configured")
                    sleep(0.3)

                    # Stage 5: Verification
                    try:
                        self._verify_installation_with_progress(progress)
                    except (WommDeploymentServiceError, OSError, ValueError):
                        # Re-raise our custom exceptions
                        raise
                    except Exception as e:
                        # Wrap unexpected external exceptions
                        raise WommDeploymentServiceError(
                            operation="install",
                            reason=f"Failed to verify installation: {e}",
                            details=f"Exception type: {type(e).__name__}",
                        ) from e

                    # Complete verification
                    progress.complete_layer("verification")

                    # Complete main installation progress
                    progress.update_layer(
                        "main_installation", 5, "Installation completed!"
                    )
                    sleep(0.3)

                    # Final completion for main installation
                    sleep(0.5)

                    # Complete and remove main installation layer
                    progress.complete_layer("main_installation")

                except (WommDeploymentServiceError, OSError, ValueError) as e:
                    # Stop progress first, then print error details
                    progress.emergency_stop(f"Installation failed: {type(e).__name__}")

                    # Now safe to print error details
                    ezprinter.error(f"Installation failed: {e}")
                    details = getattr(e, "details", None)
                    if details:
                        ezprinter.error(f"Details: {details}")

                    # Re-raise our custom exceptions
                    raise
                except Exception as e:
                    # Handle any other unexpected errors
                    progress.emergency_stop("Unexpected error during installation")

                    # Print unexpected error details
                    ezprinter.error(f"Unexpected error during installation: {e}")

                    raise WommDeploymentServiceError(
                        operation="install",
                        reason=f"Unexpected error during installation: {e}",
                        details="This is an unexpected error that should be reported",
                    ) from e

            ezprinter._console.print("")
            ezprinter.success("✅ W.O.M.M installation completed successfully!")
            ezprinter.system(f"📁 Installed to: {self.target_path}")

            # Show Windows-specific PATH info if needed
            if self.platform == "Windows":
                ezprinter.tip(
                    "On Windows, the 'womm' command will be available in new terminal sessions."
                )
                ezprinter.tip(
                    "To use it immediately in this terminal, run: womm refresh-env"
                )

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

            completion_panel = ezprinter.create_panel(
                completion_content,
                title="✅ Installation Complete",
                style="bright_green",
                border_style="bright_green",
                padding=(1, 1),
            )
            ezprinter._console.print("")
            ezprinter._console.print(completion_panel)

            return InstallationResult(
                success=True,
                message="Installation completed successfully",
                target_path=str(self.target_path),
                installation_location=str(self.target_path),
                files_copied=len(self._installed_files),
                path_configured=True,
                executable_created=True,
                verification_passed=True,
                details={"installed_files": list(self._installed_files)},
            )

        except (WommDeploymentServiceError, OSError, ValueError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.exception("Unexpected error in install")
            raise WommDeploymentServiceError(
                operation="install",
                reason=f"Installation failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _copy_files_with_progress(
        self,
        files_to_copy: list[str],
        progress,
        verbose: bool = False,
    ) -> bool:
        """
        Copy files from source to target directory with progress tracking.

        Args:
            files_to_copy: List of relative file paths to copy
            progress: DynamicLayeredProgress instance
            verbose: Show detailed progress information

        Returns:
            True if successful, False otherwise

        Raises:
            FileVerificationError: If file copying fails
            InstallationFileError: If file operations fail
            InstallationUtilityError: If unexpected error occurs
        """
        try:
            # Create target root directory
            self.target_path.mkdir(parents=True, exist_ok=True)

            # Copy files with progress tracking
            for i, relative_file in enumerate(files_to_copy):
                source_file = self.source_path / relative_file

                # Determine target path based on file type:
                # - womm/* files go to target/womm/*
                # - womm.py and womm.bat go to target/
                if relative_file.startswith("womm/"):
                    target_file = self.target_path / relative_file
                else:
                    # womm.py, womm.bat go directly to target root
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
                    # Silent mode during progress - details shown in progress bar
                    pass

            return True

        except OSError as e:
            # Stop progress and raise specific exception
            progress.emergency_stop("File copy failed")

            raise WommDeploymentServiceError(
                operation="file_copy",
                reason=str(e),
                details=f"file_path={str(source_file)}"
                + " | "
                + f"Failed at file {i + 1}/{len(files_to_copy)}: {relative_file}",
            ) from e
        except Exception as e:
            # Stop progress and raise manager exception
            progress.emergency_stop("Unexpected error during file copy")

            raise WommDeploymentServiceError(
                operation="copy",
                reason=f"Unexpected error during file copy: {e}",
                details=f"file_path={str(source_file)}"
                + " | "
                + "This is an unexpected error that should be reported",
            ) from e

    def _copy_files(
        self,
        files_to_copy: list[str],
        verbose: bool = False,
        progress=None,
        file_task_id=None,
    ) -> bool:
        """
        Copy files from source to target directory.

        Args:
            files_to_copy: List of relative file paths to copy
            verbose: Show detailed progress information
            progress: Progress instance (optional)
            file_task_id: Progress task ID (optional)

        Returns:
            True if successful, False otherwise

        Raises:
            FileVerificationError: If file copying fails
            InstallationFileError: If file operations fail
            InstallationUtilityError: If unexpected error occurs
        """
        try:
            # Create target root directory
            self.target_path.mkdir(parents=True, exist_ok=True)

            # Copy files with layered progress bar
            for _i, relative_file in enumerate(files_to_copy):
                source_file = self.source_path / relative_file

                # Determine target path based on file type:
                # - womm/* files go to target/womm/*
                # - womm.py and womm.bat go to target/
                if relative_file.startswith("womm/"):
                    target_file = self.target_path / relative_file
                else:
                    # womm.py, womm.bat go directly to target root
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

                if verbose and progress and file_task_id is not None:
                    # Update progress details instead of printing directly
                    progress.update(
                        file_task_id, description=f"Copying files... ({relative_file})"
                    )

        except OSError as e:
            # Stop progress and raise specific exception
            if progress:
                progress.emergency_stop("File copy failed")

            raise WommDeploymentServiceError(
                operation="file_copy",
                reason=str(e),
                details=f"file_path={str(source_file)}"
                + " | "
                + f"Failed at file {_i + 1}/{len(files_to_copy)}: {relative_file}",
            ) from e
        except Exception as e:
            # Stop progress and raise manager exception
            if progress:
                progress.emergency_stop("Unexpected error during file copy")

            raise WommDeploymentServiceError(
                operation="copy",
                reason=f"Unexpected error during file copy: {e}",
                details=f"file_path={str(source_file)}"
                + " | "
                + "This is an unexpected error that should be reported",
            ) from e
        else:
            return True

    # ------------------------------------------------
    # PRIVATE METHODS - PRE-INSTALLATION CHECKS
    # ------------------------------------------------

    def _precheck_source_files(self, verbose: bool = False) -> bool:
        """
        Pre-check that all required source files and directories exist.

        Verifies:
        - womm/bin directory exists
        - womm/assets directory exists
        - womm.py exists in source
        - womm.bat exists in source

        Args:
            verbose: Show detailed information

        Returns:
            True if all checks pass, False otherwise
        """
        try:
            womm_dir = self.source_path / "womm"
            bin_dir = womm_dir / "bin"
            assets_dir = womm_dir / "assets"
            womm_py = self.source_path / "womm.py"
            womm_bat = self.source_path / "womm.bat"

            # Check each required component
            checks = [
                (womm_dir.is_dir(), f"womm directory: {womm_dir}"),
                (bin_dir.is_dir(), f"womm/bin directory: {bin_dir}"),
                (assets_dir.is_dir(), f"womm/assets directory: {assets_dir}"),
                (womm_py.is_file(), f"womm.py file: {womm_py}"),
                (womm_bat.is_file(), f"womm.bat file: {womm_bat}"),
            ]

            all_ok = True
            for check_result, description in checks:
                status = "[OK]" if check_result else "[FAIL]"
                if not check_result:
                    all_ok = False
                if verbose:
                    # Use ASCII-safe logging without unicode characters
                    logger.info(f"  {status} {description}")

            return all_ok

        except Exception:
            logger.exception("Pre-check failed")
            return False

    def _build_installation_file_list(self) -> list[str]:
        """
        Build list of files to copy during installation.

        Collects:
        - All files from womm/ directory (relative paths)
        - womm.py from source root
        - womm.bat from source root

        Returns:
            List of relative file paths to copy

        Raises:
            WommDeploymentServiceError: If file list building fails
        """
        files: list[str] = []

        try:
            # Add all files from womm/ directory
            womm_dir = self.source_path / "womm"
            for root, _dirs, file_names in os.walk(womm_dir):
                for file_name in file_names:
                    file_path = Path(root) / file_name
                    relative_path = file_path.relative_to(self.source_path)
                    files.append(str(relative_path))

            # Add womm.py and womm.bat from source root
            womm_py = self.source_path / "womm.py"
            womm_bat = self.source_path / "womm.bat"

            if womm_py.exists():
                files.append("womm.py")
            if womm_bat.exists():
                files.append("womm.bat")

            return sorted(files)

        except Exception as e:
            logger.exception("Failed to build installation file list")
            raise WommDeploymentServiceError(
                operation="install",
                reason=f"Failed to build file list: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ------------------------------------------------
    # PRIVATE METHODS - PATH OPERATIONS
    # ------------------------------------------------

    def _setup_path(self) -> bool:
        """
        Setup PATH environment variable using PathManager.

        Returns:
            True if successful, False otherwise

        Raises:
            WommDeploymentServiceError: If PATH setup fails
            InstallationPathError: If PATH operations fail
            InstallationUtilityError: If unexpected error occurs
        """
        try:
            path_manager = SystemPathInterface(target=str(self.target_path))
            result = path_manager.add_to_path()

            sleep(0.5)

            if not result.success:
                error_msg = result.error or result.message or "Unknown error"
                ezprinter.error(f"PATH setup failed: {error_msg}")
                logger.error(f"PATH setup returned failure: {result}")

                raise WommDeploymentServiceError(
                    operation="path_setup",
                    reason="PATH setup failed",
                    details=f"path={str(self.target_path)}"
                    + " | "
                    + f"PathManager error: {error_msg}",
                )

        except WommDeploymentServiceError as e:
            # Log and re-raise our custom exception with full details
            logger.exception(f"PATH setup failed: {e.message}")
            if e.details:
                logger.exception(f"Details: {e.details}")
            ezprinter.error(f"PATH setup error: {e.message}")
            if e.details and e.details != e.message:
                ezprinter.error(f"Details: {e.details}")
            raise
        except Exception as e:
            # Note: PATH setup is not called within progress context, safe to print immediately
            logger.exception("Unexpected error setting up PATH")
            ezprinter.error(f"Unexpected error setting up PATH: {e}")

            raise WommDeploymentServiceError(
                operation="path_setup",
                reason="",
                details=f"path={str(self.target_path)}"
                + " | "
                + f"Unexpected error during PATH setup: {e}",
            ) from e
        else:
            return True

    def _refresh_environment(self) -> bool:
        """
        Refresh environment variables using EnvironmentManager (Windows only).

        Returns:
            True if successful, False otherwise

        Raises:
            InstallationSystemError: If environment refresh fails
            InstallationUtilityError: If utility operations fail
        """
        try:
            # Use SystemEnvironmentInterface for environment refresh
            environment_manager = SystemEnvironmentInterface()

            # Use the internal refresh method without UI
            success = environment_manager.refresh_environment()

            if success:
                ezprinter.success("Environment variables refreshed successfully")

                # Verify that environment refresh actually worked
                # by executing RefreshEnv.cmd in a new console and testing womm --version
                try:
                    if platform.system() == "Windows":
                        # Check if RefreshEnv.cmd exists in the installation
                        refresh_env_cmd = self.target_path / "bin" / "RefreshEnv.cmd"
                        if refresh_env_cmd.exists():
                            # Validate paths for security
                            refresh_env_cmd = refresh_env_cmd.resolve()
                            if not refresh_env_cmd.is_file():
                                raise ValueError(
                                    f"RefreshEnv.cmd is not a file: {refresh_env_cmd}"
                                )

                            # Create a temporary batch script that:
                            # 1. Calls RefreshEnv.cmd to refresh environment
                            # 2. Tests womm --version in the same session
                            with tempfile.NamedTemporaryFile(
                                mode="w",
                                suffix=".bat",
                                delete=False,
                                encoding="utf-8",
                            ) as temp_script:
                                temp_script_path = Path(temp_script.name).resolve()
                                # Write script that calls RefreshEnv then tests womm
                                temp_script.write("@echo off\n")
                                temp_script.write(f'call "{refresh_env_cmd}"\n')
                                temp_script.write("womm --version\n")
                                temp_script.write("if errorlevel 1 exit /b 1\n")
                                temp_script.write("exit /b 0\n")

                            try:
                                # Execute in a new cmd.exe session
                                # /c runs the command and exits
                                # Use absolute path to cmd.exe for security
                                cmd_exe = Path(
                                    os.environ.get(
                                        "COMSPEC", "C:\\Windows\\System32\\cmd.exe"
                                    )
                                )
                                if not cmd_exe.is_file():
                                    raise ValueError(f"cmd.exe not found: {cmd_exe}")

                                result = self._command_runner.run(
                                    [
                                        str(cmd_exe),
                                        "/c",
                                        str(temp_script_path),
                                    ],
                                    description="Verify environment refresh",
                                )

                                if result.returncode == 0:
                                    ezprinter.success(
                                        "Environment refresh verification successful - WOMM is accessible"
                                    )
                                    return True
                                else:
                                    ezprinter.warning(
                                        "Environment refresh completed but WOMM verification failed"
                                    )
                                    return True
                            finally:
                                # Clean up temp script
                                with contextlib.suppress(Exception):
                                    temp_script_path.unlink()
                        else:
                            # RefreshEnv.cmd not found, fallback to simple test
                            test_result = self._command_runner.run_silent(
                                ["womm", "--version"], capture_output=True
                            )
                            if bool(test_result):
                                ezprinter.success(
                                    "Environment refresh verification successful - WOMM is accessible"
                                )
                                return True
                            else:
                                ezprinter.warning(
                                    "Environment refresh completed but WOMM not yet accessible in current session"
                                )
                                return True
                    else:
                        # Non-Windows: simple test
                        test_result = self._command_runner.run_silent(
                            ["womm", "--version"], capture_output=True
                        )
                        if bool(test_result):
                            ezprinter.success(
                                "Environment refresh verification successful - WOMM is accessible"
                            )
                            return True
                        else:
                            ezprinter.warning(
                                "Environment refresh completed but WOMM not yet accessible in current session"
                            )
                            return True
                except Exception as e:
                    ezprinter.warning(f"Could not verify environment refresh: {e}")
                    return True
            else:
                ezprinter.warning("Environment refresh completed with warnings")
                ezprinter.info("User may need to restart terminal to access WOMM")
                return True

        except (WommDeploymentServiceError, OSError, ValueError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            ezprinter.error(f"Error refreshing environment: {e}")
            # Don't fail installation if refresh fails, but raise exception for logging
            raise WommDeploymentServiceError(
                operation="environment_refresh",
                reason=f"Environment refresh failed: {e}",
                details="EnvironmentManager refresh failed",
            ) from e

    def _backup_path(self) -> bool:
        """
        Backup current PATH configuration using PathManager.

        Returns:
            True if backup successful, False otherwise

        Raises:
            InstallationPathError: If PATH backup fails
            InstallationUtilityError: If utility operations fail
        """
        try:
            path_manager = SystemPathInterface(target=str(self.target_path))
            backup_result = path_manager.create_backup()

            if backup_result.success:
                # Keep backup reference for potential rollback
                if backup_result.backup_file:
                    self._path_backup_file = str(
                        Path(backup_result.backup_file).resolve()
                    )
                return True
            else:
                ezprinter.error(f"PATH backup failed: {backup_result.error}")

                raise WommDeploymentServiceError(
                    operation="backup",
                    reason="PATH backup failed",
                    details=f"path={str(self.target_path)}"
                    + " | "
                    + f"PathManager backup error: {backup_result.error}",
                )

        except WommDeploymentServiceError:
            # Re-raise our custom exception
            raise
        except Exception as e:
            ezprinter.error(f"Unexpected error during PATH backup: {e}")

            raise WommDeploymentServiceError(
                operation="backup",
                reason=f"Unexpected error during PATH backup: {e}",
                details=f"path={str(self.target_path)}"
                + " | "
                + "This is an unexpected error that should be reported",
            ) from e

    def _rollback_path(self) -> bool:
        """
        Rollback PATH to previous state using PathManager backup.

        Returns:
            True if rollback successful, False otherwise

        Raises:
            InstallationPathError: If PATH rollback fails
            InstallationUtilityError: If utility operations fail
        """
        try:
            if not self._path_backup_file:
                ezprinter.error("No backup file available for rollback")

                raise WommDeploymentServiceError(
                    operation="rollback",
                    reason="No backup file available for rollback",
                    details=f"path={str(self.target_path)}"
                    + " | "
                    + "PATH backup file not found for rollback",
                )

            # Use PathManager to restore from specific backup file

            backup_file = Path(self._path_backup_file)
            if not backup_file.exists():
                ezprinter.error(f"Backup file not found: {backup_file}")

                raise WommDeploymentServiceError(
                    operation="rollback",
                    reason="Backup file not found for rollback",
                    details=f"path={str(backup_file)}"
                    + " | "
                    + f"Backup file not found at: {backup_file}",
                )

            # Read backup data to get the PATH string
            try:
                with open(backup_file, encoding="utf-8") as f:
                    backup_data = json.load(f)
            except Exception as e:
                raise WommDeploymentServiceError(
                    operation="rollback",
                    reason=f"Failed to read backup file: {e}",
                    details=f"path={str(backup_file)}"
                    + " | "
                    + f"Exception type: {type(e).__name__}",
                ) from e

            restored_path = backup_data.get("path_string", "")
            if not restored_path:
                ezprinter.error("Invalid backup file: no PATH string found")

                raise WommDeploymentServiceError(
                    operation="rollback",
                    reason="Invalid backup file for rollback",
                    details=f"path={str(backup_file)}"
                    + " | "
                    + "Backup file contains no PATH string",
                )

            # Use SystemPathInterface's platform-specific restore logic
            path_manager = SystemPathInterface(target=str(self.target_path))

            if path_manager.platform == "Windows":
                try:
                    result = self._command_runner.run_silent(
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
                except Exception as e:
                    raise WommDeploymentServiceError(
                        operation="rollback",
                        reason=f"Failed to execute registry command: {e}",
                        details=f"path={str(self.target_path)}"
                        + " | "
                        + f"Exception type: {type(e).__name__}",
                    ) from e

                if bool(result):
                    ezprinter.success("PATH successfully rolled back to previous state")
                    return True
                else:
                    stderr = getattr(result, "stderr", "")
                    ezprinter.error(f"PATH rollback failed: {stderr}")

                    raise WommDeploymentServiceError(
                        operation="rollback",
                        reason="PATH rollback failed: Registry update failed",
                        details=f"path={str(self.target_path)}"
                        + " | "
                        + f"Windows registry update failed: {stderr}",
                    )
            else:
                # Unix rollback - update environment
                os.environ["PATH"] = restored_path
                ezprinter.success("PATH successfully rolled back to previous state")
                return True

        except (
            UserPathServiceError,
            RegistryServiceError,
            FileSystemServiceError,
        ):
            # Re-raise our custom exceptions
            raise
        except (WommDeploymentServiceError, OSError, ValueError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            ezprinter.error(f"Unexpected error during PATH rollback: {e}")

            raise WommDeploymentServiceError(
                operation="rollback",
                reason=f"Unexpected error during PATH rollback: {e}",
                details=f"path={str(self.target_path)}"
                + " | "
                + "This is an unexpected error that should be reported",
            ) from e

    # ------------------------------------------------
    # PRIVATE METHODS - VERIFICATION OPERATIONS
    # ------------------------------------------------

    def _verify_installation_with_progress(self, progress) -> bool:
        """
        Verify installation with progress tracking.

        Args:
            progress: DynamicLayeredProgress instance

        Returns:
            True if verification passed, False otherwise

        Raises:
            FileVerificationError: If file verification fails
            ExecutableVerificationError: If executable verification fails
            WommDeploymentServiceError: If PATH verification fails
            InstallationVerificationError: If verification fails
            InstallationUtilityError: If unexpected error occurs
        """
        try:
            # Step 1: File integrity check
            progress.update_layer("verification", 0, "Checking file integrity...")

            try:
                verify_files_copied(
                    self.source_path, self.target_path, self._installed_files
                )
                # If we get here, verification passed (no exception raised)
            except (WommDeploymentServiceError, OSError, ValueError):
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                # Stop progress and handle the exception
                progress.emergency_stop("File verification failed")

                # Re-raise as file verification error
                raise WommDeploymentServiceError(
                    operation="file_integrity",
                    reason=str(e),
                    details=f"file_path={str(self.target_path)}"
                    + " | "
                    + "Files are missing or corrupted",
                ) from e

            sleep(0.2)

            # Step 2: Essential files verification
            progress.update_layer("verification", 1, "Verifying essential files...")
            essential_files = WOMMDeploymentConfig.ESSENTIAL_FILES
            for essential_file in essential_files:
                file_path = self.target_path / essential_file
                if not file_path.exists():
                    progress.emergency_stop("Essential file missing")

                    raise WommDeploymentServiceError(
                        operation="essential_files",
                        reason=f"Essential file missing: {essential_file}",
                        details=f"file_path={str(file_path)}"
                        + " | "
                        + f"Required file not found at {file_path}",
                    )
            sleep(0.2)

            # Step 3: Command accessibility test
            progress.update_layer("verification", 2, "Testing command accessibility...")

            # Environment refresh is now handled in a separate step before verification

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
            except (WommDeploymentServiceError, OSError, ValueError):
                # On Windows, be more tolerant of PATH timing issues
                if self.platform == "Windows":
                    # Don't print during progress - pass message to progress dict
                    progress.update_layer(
                        "verification",
                        2,
                        "Command verification failed but continuing on Windows (PATH timing issue) - WOMM will be available in new terminal sessions",
                    )
                    sleep(0.2)
                else:
                    # Re-raise our custom exceptions on non-Windows
                    raise
            except Exception as e:
                # On Windows, check if it's the expected PATH timing issue
                if (
                    self.platform == "Windows"
                    and "Local executable works but global command failed" in str(e)
                ):
                    # Continue with installation since local executable works (don't print during progress)
                    # Note: Windows PATH timing issue - command will be available in new terminals
                    sleep(0.2)
                elif self.platform == "Windows":
                    # On Windows, be more tolerant of PATH timing issues
                    # Don't print during progress - pass message to progress dict
                    progress.update_layer(
                        "verification",
                        2,
                        f"Command verification failed on Windows: {e} - WOMM will be available in new terminal sessions",
                    )
                    sleep(0.2)
                else:
                    # Stop progress and handle the exception
                    progress.emergency_stop("Command verification failed")

                    raise WommDeploymentServiceError(
                        operation="executable_verification",
                        reason=str(e),
                        details="executable_name=womm"
                        + " | "
                        + "WOMM commands are not accessible",
                    ) from e
            sleep(0.2)

            # Step 4: PATH configuration test
            progress.update_layer("verification", 3, "Verifying PATH configuration...")

            try:
                self.installation_service.verify_path_configuration(
                    str(self.target_path)
                )
                # If we get here, verification passed (no exception raised)
            except (WommDeploymentServiceError, OSError, ValueError):
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                # Stop progress and handle the exception
                progress.emergency_stop("PATH verification failed")

                raise WommDeploymentServiceError(
                    operation="path_configuration",
                    reason=str(e),
                    details=f"path={str(self.target_path)}"
                    + " | "
                    + "PATH environment variable is not configured correctly",
                ) from e
            sleep(0.2)

        except (WommDeploymentServiceError, OSError, ValueError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Stop progress and handle unexpected errors
            progress.emergency_stop("Unexpected error during verification")

            raise WommDeploymentServiceError(
                operation="unexpected_error",
                reason=f"Unexpected error during verification: {e}",
                details=f"target_path={str(self.target_path)}"
                + " | "
                + "This is an unexpected error that should be reported",
            ) from e
        else:
            return True

    def _verify_installation(self) -> bool:
        """
        Verify that the installation completed successfully.

        Returns:
            True if verification passed, False otherwise

        Raises:
            FileVerificationError: If file verification fails
            ExecutableVerificationError: If executable verification fails
            WommDeploymentServiceError: If PATH verification fails
            InstallationVerificationError: If verification fails
            InstallationUtilityError: If unexpected error occurs
        """
        try:
            # Use utils for verification

            # 0. Verify all files were copied correctly
            try:
                verify_files_copied(self.source_path, self.target_path)
                # If we get here, verification passed (no exception raised)
            except (WommDeploymentServiceError, OSError, ValueError):
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                ezprinter.error(f"File verification failed: {e}")

                raise WommDeploymentServiceError(
                    operation="file_integrity",
                    reason=str(e),
                    details=f"file_path={str(self.target_path)}"
                    + " | "
                    + "Files are missing or corrupted",
                ) from e

            # 1. Verify essential files exist (basic check during installation)
            essential_files = WOMMDeploymentConfig.ESSENTIAL_FILES
            for essential_file in essential_files:
                file_path = self.target_path / essential_file
                if not file_path.exists():
                    ezprinter.error(f"Essential file missing: {essential_file}")

                    raise WommDeploymentServiceError(
                        operation="essential_files",
                        reason=f"Essential file missing: {essential_file}",
                        details=f"file_path={str(file_path)}"
                        + " | "
                        + f"Required file not found at {file_path}",
                    )

            # 2. Verify commands are accessible in PATH
            try:
                self.installation_service.verify_commands_accessible(
                    str(self.target_path)
                )
                # If we get here, verification passed (no exception raised)
            except (WommDeploymentServiceError, OSError, ValueError):
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                ezprinter.error(f"Commands not accessible: {e}")

                raise WommDeploymentServiceError(
                    operation="executable_verification",
                    reason=str(e),
                    details="executable_name=womm"
                    + " | "
                    + "WOMM commands are not accessible",
                ) from e

            # 3. Verify PATH configuration
            try:
                self.installation_service.verify_path_configuration(
                    str(self.target_path)
                )
                # If we get here, verification passed (no exception raised)
            except (WommDeploymentServiceError, OSError, ValueError):
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                ezprinter.error(f"PATH configuration failed: {e}")

                raise WommDeploymentServiceError(
                    operation="path_configuration",
                    reason=str(e),
                    details=f"path={str(self.target_path)}"
                    + " | "
                    + "PATH environment variable is not configured correctly",
                ) from e
        except (WommDeploymentServiceError, OSError, ValueError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            ezprinter.error(f"Unexpected error during verification: {e}")

            raise WommDeploymentServiceError(
                operation="unexpected_error",
                reason=f"Unexpected error during verification: {e}",
                details=f"target_path={str(self.target_path)}"
                + " | "
                + "This is an unexpected error that should be reported",
            ) from e
        else:
            return True
