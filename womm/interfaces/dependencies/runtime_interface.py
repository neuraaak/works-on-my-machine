#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPEN - Context Menu Parameters Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Runtime Manager for Works On My Machine.
Manages runtime dependencies (Python, Node.js, Git).
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import platform
import shutil

# Third-party imports
from rich.progress import TaskID

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.dependencies import RuntimeInterfaceError
from ...exceptions.womm_deployment import DependencyServiceError
from ...services import CommandRunnerService, RuntimeService
from ...shared.configs.dependencies import RuntimeConfig
from ...shared.results import RuntimeResult
from ...ui.common import ezprinter
from ...ui.dependencies import display_runtime_table

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)


# ///////////////////////////////////////////////////////////////
# RUNTIME DEFINITIONS
# ///////////////////////////////////////////////////////////////

# Import from config instead of defining here
RUNTIMES = RuntimeConfig.RUNTIMES


# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class RuntimeInterface:
    """Manages runtime dependencies (Python, Node.js, Git)."""

    def __init__(self):
        """
        Initialize the runtime manager.

        Raises:
            RuntimeManagerError: If runtime manager initialization fails
        """
        try:
            self.system = platform.system()
            self.cache = {}
            self._command_runner: CommandRunnerService | None = None
            self._runtime_manager_service: RuntimeService | None = None

        except Exception as e:
            logger.error(f"Failed to initialize RuntimeManager: {e}")
            raise RuntimeInterfaceError(
                message=f"Failed to initialize runtime manager: {e}",
                runtime_name="runtime_manager",
                operation="initialization",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # SERVICE PROPERTIES (LAZY INITIALIZATION)
    # ///////////////////////////////////////////////////////////////

    @property
    def command_runner(self) -> CommandRunnerService:
        """Lazy load CommandRunnerService when needed."""
        if self._command_runner is None:
            self._command_runner = CommandRunnerService()
        return self._command_runner

    @property
    def runtime_manager_service(self) -> RuntimeService:
        """Lazy load RuntimeManagerService when needed."""
        if self._runtime_manager_service is None:
            self._runtime_manager_service = RuntimeService()
        return self._runtime_manager_service

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def check_runtime(self, runtime: str) -> RuntimeResult:
        """
        Check if a runtime is installed.

        Args:
            runtime: Name of the runtime to check

        Returns:
            RuntimeResult: Result of the check operation

        Raises:
            RuntimeManagerError: If runtime check fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not runtime:
                raise ValidationServiceError(
                    reason="Runtime name must not be empty",
                    operation="check_runtime",
                    field="runtime",
                    details="Runtime parameter must be a non-empty string",
                )

            with ezprinter.create_spinner(f"Checking {runtime}...") as (
                progress,
                task,
            ):
                task_id = TaskID(task)
                if runtime not in RUNTIMES:
                    progress.update(
                        task_id, description=f"Runtime {runtime} not supported"
                    )
                    return RuntimeResult(
                        success=False,
                        runtime_name=runtime,
                        message=f"Runtime {runtime} not supported",
                        error=f"Runtime {runtime} not supported",
                    )

                # Check cache first
                if runtime in self.cache:
                    available, version = self.cache[runtime]
                    progress.update(
                        task_id, description=f"Runtime {runtime} already installed"
                    )
                    return RuntimeResult(
                        success=available,
                        runtime_name=runtime,
                        version=version,
                        path=shutil.which(runtime) if available else None,
                        message=f"Runtime {runtime} {'available' if available else 'not found'}",
                        error="" if available else f"Runtime {runtime} not installed",
                    )

                # Check runtime
                try:
                    result = self.runtime_manager_service.check_runtime_installation(
                        runtime
                    )
                    available = result.is_installed
                    version = result.version
                except Exception as e:
                    logger.warning(
                        f"Failed to check runtime installation for {runtime}: {e}"
                    )
                    available, version = False, None

                self.cache[runtime] = (available, version)

                progress.update(
                    task_id,
                    description=f"Runtime {runtime} {'available' if available else 'not found'}",
                )
                return RuntimeResult(
                    success=available,
                    runtime_name=runtime,
                    version=version,
                    path=shutil.which(runtime) if available else None,
                    message=f"Runtime {runtime} {'available' if available else 'not found'}",
                    error="" if available else f"Runtime {runtime} not installed",
                )

        except (RuntimeInterfaceError, ValidationServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in check_runtime: {e}")
            raise RuntimeInterfaceError(
                message=f"Failed to check runtime: {e}",
                runtime_name=runtime,
                operation="check",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def check_all_runtimes(self) -> dict[str, RuntimeResult]:
        """
        Check all configured runtimes with a single spinner and display results.

        Uses a single spinner with status updates for each runtime,
        then displays a summary table.

        Returns:
            Dictionary mapping runtime names to RuntimeResult objects
        """
        runtimes = list(RUNTIMES.keys())
        results = {}

        with ezprinter.create_spinner_with_status(
            "Checking runtime availability..."
        ) as (progress, task):
            task_id = TaskID(task)
            progress.update(task_id, status="Initializing...")

            for runtime in runtimes:
                progress.update(task_id, status=f"Checking {runtime}")

                try:
                    # Call service directly (no spinner)
                    service_result = (
                        self.runtime_manager_service.check_runtime_installation(runtime)
                    )
                    available = service_result.is_installed
                    version = service_result.version

                    # Cache the result
                    self.cache[runtime] = (available, version)

                    results[runtime] = RuntimeResult(
                        success=available,
                        runtime_name=runtime,
                        version=version,
                        path=shutil.which(runtime) if available else None,
                        message=f"Runtime {runtime} {'available' if available else 'not found'}",
                        error="" if available else f"Runtime {runtime} not installed",
                    )
                except Exception as e:
                    logger.warning(f"Failed to check runtime {runtime}: {e}")
                    results[runtime] = RuntimeResult(
                        success=False,
                        runtime_name=runtime,
                        message=f"Failed to check {runtime}",
                        error=str(e),
                    )

            progress.update(task_id, status="Check completed")

        # Display results table via UI
        print()
        display_runtime_table(results)

        return results

    def install_runtime(
        self, runtime: str, _extra_pm_args: list[str] | None = None
    ) -> RuntimeResult:
        """
        Install a runtime with UI feedback.

        Delegates to RuntimeService which handles dependency resolution via DependencyHierarchy.

        Args:
            runtime: Name of the runtime to install
            extra_pm_args: Extra arguments to pass to the package manager (optional, currently unused)

        Returns:
            RuntimeResult: Result of the installation operation

        Raises:
            RuntimeManagerError: If runtime installation fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not runtime:
                raise ValidationServiceError(
                    reason="Runtime name must not be empty",
                    operation="install_runtime",
                    field="runtime",
                    details="Runtime parameter must be a non-empty string",
                )

            with ezprinter.create_spinner_with_status(f"Installing {runtime}...") as (
                progress,
                task,
            ):
                task_id = TaskID(task)
                if runtime not in RUNTIMES:
                    ezprinter.error(f"Runtime {runtime} not supported")
                    return RuntimeResult(
                        success=False,
                        runtime_name=runtime,
                        message=f"Runtime {runtime} not supported",
                        error=f"Runtime {runtime} not supported",
                    )

                # Check if already installed
                progress.update(task_id, status="Checking current installation...")
                try:
                    result = self.runtime_manager_service.check_runtime_installation(
                        runtime
                    )
                    if result.is_installed:
                        progress.update(
                            task_id,
                            status=f"Already installed (version {result.version})",
                        )
                        ezprinter.success(
                            f"Runtime {runtime} already installed (version {result.version})"
                        )
                        return RuntimeResult(
                            success=True,
                            runtime_name=runtime,
                            version=result.version,
                            path=shutil.which(runtime),
                            message=f"Runtime {runtime} already installed (version {result.version})",
                        )
                except Exception as e:
                    logger.warning(
                        f"Failed to check runtime installation for {runtime}: {e}"
                    )

                # Delegate to service - it handles system package manager resolution
                progress.update(
                    task_id, status="Finding best system package manager..."
                )
                try:
                    result = self.runtime_manager_service.install_runtime(runtime)
                except Exception as e:
                    progress.update(task_id, status="Installation failed")
                    logger.error(f"Failed to install runtime {runtime}: {e}")
                    ezprinter.error(f"Failed to install runtime {runtime}: {e}")
                    return RuntimeResult(
                        success=False,
                        runtime_name=runtime,
                        message=f"Failed to install runtime {runtime}",
                        error=str(e),
                    )

                # Update cache
                if result.is_installed:
                    self.cache[runtime] = (result.is_installed, result.version)
                    progress.update(
                        task_id, status="Installation completed successfully!"
                    )
                    ezprinter.success(f"Runtime {runtime} installed successfully")
                    return RuntimeResult(
                        success=True,
                        runtime_name=runtime,
                        version=result.version,
                        path=shutil.which(runtime),
                        message=f"Runtime {runtime} installed successfully",
                    )
                else:
                    progress.update(task_id, status="Installation failed")
                    ezprinter.error(f"Failed to install runtime {runtime}")
                    return RuntimeResult(
                        success=False,
                        runtime_name=runtime,
                        message=f"Failed to install runtime {runtime}",
                        error="Installation failed",
                    )

        except (
            RuntimeInterfaceError,
            DependencyServiceError,
            ValidationServiceError,
        ):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in install_runtime: {e}")
            raise RuntimeInterfaceError(
                message=f"Failed to install runtime: {e}",
                runtime_name=runtime,
                operation="installation",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def show_runtime_check(self, runtime: str, verbose: bool = False) -> RuntimeResult:
        """
        Check a runtime and display the result.

        Args:
            runtime: Runtime name to check
            verbose: Whether to show detailed information

        Returns:
            RuntimeResult: Check result
        """
        from ...ui.dependencies import display_runtime_check_specific

        result = self.check_runtime(runtime)
        display_runtime_check_specific(result, runtime, verbose)
        return result

    def show_runtime_install(
        self, runtime: str, verbose: bool = False
    ) -> RuntimeResult:
        """
        Install a runtime and display the result.

        Args:
            runtime: Runtime name to install
            verbose: Whether to show detailed information

        Returns:
            RuntimeResult: Installation result
        """
        from ...ui.dependencies import display_runtime_install_result

        result = self.install_runtime(runtime)
        display_runtime_install_result(result, runtime, verbose)
        return result

    def show_runtimes_list(self, verbose: bool = False) -> None:
        """
        Display the list of available runtimes.

        Args:
            verbose: Whether to show detailed information
        """
        from ...ui.dependencies import display_runtimes_list

        display_runtimes_list(verbose)

    def check_and_install_runtimes(
        self, runtimes: list[str]
    ) -> dict[str, RuntimeResult]:
        """
        Check and install multiple runtimes.

        Args:
            runtimes: List of runtime names to check and install

        Returns:
            dict[str, RuntimeResult]: Results for each runtime

        Raises:
            RuntimeManagerError: If runtime check/installation fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not runtimes:
                raise ValidationServiceError(
                    reason="Runtimes list must not be empty",
                    operation="check_and_install_runtimes",
                    field="runtimes",
                    details="Runtimes parameter must be a non-empty list",
                )

            if not isinstance(runtimes, list):
                raise ValidationServiceError(
                    reason="Runtimes must be a list",
                    operation="check_and_install_runtimes",
                    field="runtimes",
                    details="Runtimes parameter must be a list of strings",
                )

            results = {}

            for runtime in runtimes:
                if runtime not in RUNTIMES:
                    results[runtime] = RuntimeResult(
                        success=False,
                        runtime_name=runtime,
                        message=f"Runtime {runtime} not supported",
                        error=f"Runtime {runtime} not supported",
                    )
                    continue

                # Check if already installed
                try:
                    result = self.runtime_manager_service.check_runtime_installation(
                        runtime
                    )
                    if result.is_installed:
                        results[runtime] = RuntimeResult(
                            success=True,
                            runtime_name=runtime,
                            version=result.version,
                            path=shutil.which(runtime),
                            message=f"Runtime {runtime} already installed",
                        )
                    else:
                        # Install runtime
                        try:
                            results[runtime] = self.install_runtime(runtime)
                        except Exception as e:
                            logger.warning(f"Failed to install runtime {runtime}: {e}")
                            results[runtime] = RuntimeResult(
                                success=False,
                                runtime_name=runtime,
                                message=f"Failed to install runtime {runtime}",
                                error=str(e),
                            )
                except Exception as e:
                    logger.warning(f"Failed to check runtime {runtime}: {e}")
                    results[runtime] = RuntimeResult(
                        success=False,
                        runtime_name=runtime,
                        message=f"Failed to check runtime {runtime}",
                        error=str(e),
                    )

            return results

        except (RuntimeInterfaceError, ValidationServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in check_and_install_runtimes: {e}")
            raise RuntimeInterfaceError(
                message=f"Failed to check and install runtimes: {e}",
                runtime_name="runtime_manager",
                operation="check_and_install",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_installation_status(
        self, runtimes: list[str] | None = None
    ) -> dict[str, dict]:
        """
        Get comprehensive installation status for runtimes.

        Args:
            runtimes: List of runtime names to check (optional)

        Returns:
            dict[str, dict]: Status information for each runtime

        Raises:
            RuntimeManagerError: If status retrieval fails
        """
        try:
            if runtimes is None:
                runtimes = list(RUNTIMES.keys())

            status = {}
            for runtime in runtimes:
                with ezprinter.create_spinner(f"Checking {runtime}...") as (
                    progress,
                    task,
                ):
                    task_id = TaskID(task)
                    try:
                        result = (
                            self.runtime_manager_service.check_runtime_installation(
                                runtime
                            )
                        )
                        status[runtime] = {
                            "installed": result.is_installed,
                            "version": result.version,
                            "path": (
                                shutil.which(runtime) if result.is_installed else None
                            ),
                            "supported": runtime in RUNTIMES,
                        }
                        progress.update(
                            task_id,
                            description=f"Runtime {runtime} {'available' if result.is_installed else 'not found'}",
                        )
                    except Exception as e:
                        logger.warning(f"Failed to get status for {runtime}: {e}")
                        status[runtime] = {
                            "installed": False,
                            "version": None,
                            "path": None,
                            "supported": runtime in RUNTIMES,
                        }

            return status

        except Exception as e:
            logger.error(f"Unexpected error in get_installation_status: {e}")
            raise RuntimeInterfaceError(
                message=f"Failed to get installation status: {e}",
                runtime_name="runtime_manager",
                operation="get_status",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////
    def _check_runtime_installation(self, runtime: str) -> tuple[bool, str | None]:
        """
        Check if a runtime is installed and return version.

        Args:
            runtime: Name of the runtime to check

        Returns:
            tuple[bool, str | None]: (available, version)

        Raises:
            RuntimeManagerError: If runtime check fails
        """
        try:
            # Input validation
            if not runtime:
                raise ValidationServiceError(
                    reason="Runtime name must not be empty",
                    operation="check_runtime_installation",
                    field="runtime",
                    details="Runtime parameter must be a non-empty string",
                )

            # Delegate to service - it handles all runtime checks internally
            result = self.runtime_manager_service.check_runtime_installation(runtime)
            return (result.is_installed, result.version)

        except ValidationServiceError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _check_runtime_installation: {e}")
            raise RuntimeInterfaceError(
                message=f"Failed to check runtime installation: {e}",
                runtime_name=runtime,
                operation="check_installation",
                details=f"Exception type: {type(e).__name__}",
            ) from e
