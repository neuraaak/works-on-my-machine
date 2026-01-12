#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# RUNTIME MANAGER SERVICE - Runtime Manager Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Runtime Manager Service - Singleton service for runtime operations.

Handles runtime detection, version checking, and installation coordination
for Python, Node.js, and Git.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import platform
import shutil
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.dependencies import RuntimeManagerServiceError
from ...shared.configs.dependencies.dependencies_hierarchy import DependenciesHierarchy
from ...shared.configs.dependencies.runtime_config import RuntimeConfig
from ...shared.results.dependencies_results import RuntimeInstallationResult
from ..common.command_runner_service import CommandRunnerService

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# RUNTIME MANAGER SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class RuntimeService:
    """Singleton service for runtime operations."""

    _instance: ClassVar[RuntimeService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> RuntimeService:
        """Create or return the singleton instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize runtime manager service (only once)."""
        if RuntimeService._initialized:
            return

        try:
            self.system = platform.system()
            self.cache: dict[str, tuple[bool, str | None]] = {}
            self._command_runner = CommandRunnerService()
            RuntimeService._initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize RuntimeManagerService: {e}")
            raise RuntimeManagerServiceError(
                runtime_name="runtime_manager",
                operation="initialization",
                reason=f"Failed to initialize runtime manager service: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def check_runtime_installation(self, runtime: str) -> RuntimeInstallationResult:
        """
        Check if a runtime is installed and return version.

        Args:
            runtime: Name of the runtime to check (python, node, git)

        Returns:
            RuntimeInstallationResult: Result with installation status and version

        Raises:
            RuntimeManagerError: If runtime check fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not runtime:
                raise ValidationServiceError(
                    component="check_runtime_installation",
                    validation_type="input_validation",
                    reason="Runtime name must not be empty",
                    details="Runtime name parameter must be a non-empty string",
                )

            if runtime not in RuntimeConfig.RUNTIMES:
                raise ValidationServiceError(
                    component="check_runtime_installation",
                    validation_type="input_validation",
                    reason=f"Runtime {runtime} is not supported",
                    details=f"Supported runtimes: {list(RuntimeConfig.RUNTIMES.keys())}",
                )

            # Check cache first
            if runtime in self.cache:
                is_installed, version = self.cache[runtime]
                return RuntimeInstallationResult(
                    success=True,
                    message=f"Runtime {runtime} installation check completed",
                    runtime_name=runtime,
                    is_installed=is_installed,
                    version=version or "",
                )

            # Check runtime-specific installation
            if runtime == "python":
                installed, version = self._check_python()
            elif runtime == "node":
                installed, version = self._check_node()
            elif runtime == "git":
                installed, version = self._check_git()
            else:
                installed, version = False, None

            self.cache[runtime] = (installed, version)
            return RuntimeInstallationResult(
                success=True,
                message=f"Runtime {runtime} installation check completed",
                runtime_name=runtime,
                is_installed=installed,
                version=version or "",
            )

        except ValidationServiceError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in check_runtime_installation: {e}")
            raise RuntimeManagerServiceError(
                runtime_name=runtime,
                operation="check_installation",
                reason=f"Failed to check runtime installation: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _check_python(self) -> tuple[bool, str | None]:
        """Check if Python is installed."""
        try:
            # Try python3 first, then python
            for cmd in ["python3", "python"]:
                if shutil.which(cmd):
                    result = self._command_runner.run_silent([cmd, "--version"])
                    if result.returncode == 0 and result.stdout:
                        version = result.stdout.strip().split()[1]
                        return True, version
            return False, None
        except Exception as e:
            logger.debug(f"Failed to check Python: {e}")
            return False, None

    def _check_node(self) -> tuple[bool, str | None]:
        """Check if Node.js is installed."""
        try:
            if shutil.which("node"):
                result = self._command_runner.run_silent(["node", "--version"])
                if result.returncode == 0 and result.stdout:
                    version = result.stdout.strip().lstrip("v")
                    return True, version
            return False, None
        except Exception as e:
            logger.debug(f"Failed to check Node.js: {e}")
            return False, None

    def _check_git(self) -> tuple[bool, str | None]:
        """Check if Git is installed."""
        try:
            if shutil.which("git"):
                result = self._command_runner.run_silent(["git", "--version"])
                if result.returncode == 0 and result.stdout:
                    version = result.stdout.strip().split()[2]
                    return True, version
            return False, None
        except Exception as e:
            logger.debug(f"Failed to check Git: {e}")
            return False, None

    def get_runtime_config(
        self, runtime: str
    ) -> dict[str, str | int | list[str] | dict[str, str]] | None:
        """
        Get configuration for a runtime.

        Args:
            runtime: Name of the runtime

        Returns:
            dict | None: Runtime configuration or None if not found
        """
        return RuntimeConfig.RUNTIMES.get(runtime)

    def satisfies_min_version(self, actual: str | None, min_spec: str | None) -> bool:
        """
        Check if actual version satisfies minimum version requirement.

        Args:
            actual: Actual version string
            min_spec: Minimum version specification (e.g., "3.9+")

        Returns:
            bool: True if version satisfies requirement
        """
        if not actual or not min_spec:
            return False

        # Remove 'v' prefix if present
        actual = actual.lstrip("v")
        min_spec = min_spec.rstrip("+")

        try:
            # Simple version comparison (major.minor)
            actual_parts = [int(x) for x in actual.split(".")[:2]]
            min_parts = [int(x) for x in min_spec.split(".")[:2]]

            if actual_parts[0] > min_parts[0]:
                return True
            elif actual_parts[0] == min_parts[0]:
                return actual_parts[1] >= min_parts[1]
            else:
                return False
        except (ValueError, IndexError):
            # If version parsing fails, assume it doesn't satisfy
            return False

    def install_runtime(self, runtime: str) -> RuntimeInstallationResult:
        """
        Install a runtime using the best available system package manager.

        Uses DependenciesHierarchy to find the best system package manager,
        then delegates to SystemPackageManagerService for installation.

        Args:
            runtime: Name of the runtime to install (python, node, git)

        Returns:
            RuntimeInstallationResult: Result with installation status

        Raises:
            RuntimeManagerServiceError: If installation fails
            ValidationServiceError: If validation fails
        """
        try:
            # Input validation
            if not runtime:
                raise ValidationServiceError(
                    component="install_runtime",
                    validation_type="input_validation",
                    reason="Runtime name must not be empty",
                    details="Runtime name parameter must be a non-empty string",
                )

            if runtime not in RuntimeConfig.RUNTIMES:
                raise ValidationServiceError(
                    component="install_runtime",
                    validation_type="input_validation",
                    reason=f"Runtime {runtime} is not supported",
                    details=f"Supported runtimes: {list(RuntimeConfig.RUNTIMES.keys())}",
                )

            # Check if already installed
            check_result = self.check_runtime_installation(runtime)
            if check_result.is_installed:
                logger.info(
                    f"Runtime {runtime} is already installed (version {check_result.version})"
                )
                return check_result

            # Get best system package manager for this platform
            best_manager = DependenciesHierarchy.get_best_system_package_manager()
            if not best_manager:
                raise RuntimeManagerServiceError(
                    runtime_name=runtime,
                    operation="install",
                    reason="No suitable system package manager found for this platform",
                    details=f"Platform: {self.system}",
                )

            logger.info(f"Installing {runtime} using {best_manager}...")

            # Get package name for this manager
            runtime_config = RuntimeConfig.RUNTIMES[runtime]
            package_names = runtime_config.get("package_names", {})
            if not isinstance(package_names, dict):
                raise RuntimeManagerServiceError(
                    runtime_name=runtime,
                    operation="install",
                    reason=f"Invalid package_names configuration for {runtime}",
                    details=f"Expected dict, got {type(package_names)}",
                )

            package_id = package_names.get(best_manager)
            if not package_id:
                raise RuntimeManagerServiceError(
                    runtime_name=runtime,
                    operation="install",
                    reason=f"No package ID configured for {runtime} on {best_manager}",
                    details=f"Available managers: {list(package_names.keys())}",
                )

            # Lazy import to avoid circular dependency
            from .system_package_manager_service import SystemPackageManagerService

            pkg_manager_service = SystemPackageManagerService()

            # Install runtime via system package manager
            success = pkg_manager_service.install_package(
                manager_name=best_manager,
                package_name=runtime,
                package_id=package_id,
            )

            if not success:
                raise RuntimeManagerServiceError(
                    runtime_name=runtime,
                    operation="install",
                    reason=f"Installation via {best_manager} failed",
                    details=f"Package: {package_id}",
                )

            logger.info(f"Successfully installed {runtime} via {best_manager}")

            # Invalidate cache
            if runtime in self.cache:
                del self.cache[runtime]

            # Check again after installation
            return self.check_runtime_installation(runtime)

        except ValidationServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in install_runtime: {e}")
            raise RuntimeManagerServiceError(
                runtime_name=runtime,
                operation="install",
                reason=f"Failed to install runtime: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def ensure_runtime_package_manager(self, rpm_name: str) -> bool:
        """
        Ensure a runtime package manager (pip, npm, etc.) is available.

        Runtime package managers are bundled with their runtimes, so this method
        checks if the corresponding runtime is installed.

        Args:
            rpm_name: Name of the runtime package manager (pip, uv, npm, yarn)

        Returns:
            bool: True if available, False otherwise

        Raises:
            ValidationServiceError: If validation fails
        """
        try:
            # Input validation
            if not rpm_name:
                raise ValidationServiceError(
                    component="ensure_runtime_package_manager",
                    validation_type="input_validation",
                    reason="Runtime package manager name must not be empty",
                    details="rpm_name parameter must be a non-empty string",
                )

            # Get the runtime required for this package manager
            runtime = DependenciesHierarchy.get_runtime_from_package_manager(rpm_name)
            if not runtime:
                raise ValidationServiceError(
                    component="ensure_runtime_package_manager",
                    validation_type="input_validation",
                    reason=f"Unknown runtime package manager: {rpm_name}",
                    details=f"Known managers: {list(DependenciesHierarchy.RUNTIME_PACKAGE_MANAGERS.keys())}",
                )

            # Check if runtime is installed
            check_result = self.check_runtime_installation(runtime)
            if not check_result.is_installed:
                logger.warning(
                    f"Runtime {runtime} not installed (required for {rpm_name})"
                )
                return False

            # Check if the package manager itself is available
            if not shutil.which(rpm_name):
                logger.warning(f"Runtime package manager {rpm_name} not found in PATH")
                return False

            logger.info(f"Runtime package manager {rpm_name} is available")
            return True

        except ValidationServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in ensure_runtime_package_manager: {e}")
            return False
