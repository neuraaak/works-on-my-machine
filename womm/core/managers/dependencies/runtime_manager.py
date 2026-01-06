#!/usr/bin/env python3
"""
Runtime Manager for Works On My Machine.
Manages runtime dependencies (Python, Node.js, Git).
"""

import logging
import platform
import shutil
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from ....common.results import BaseResult
from ...exceptions.dependencies import (
    InstallationError,
    RuntimeManagerError,
    ValidationError,
)
from ...utils.cli_utils import CLIUtils, run_silent

# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class RuntimeResult(BaseResult):
    """Result of a runtime operation."""

    runtime_name: str = ""
    version: Optional[str] = None
    path: Optional[str] = None


# =============================================================================
# RUNTIME DEFINITIONS
# =============================================================================

RUNTIMES = {
    "python": {
        "version": "3.9+",
        "priority": 1,
        "package_managers": [
            "winget",
            "chocolatey",
            "homebrew",
            "apt",
            "dnf",
            "pacman",
        ],
        "package_names": {
            "winget": "Python.Python.3.11",
            "chocolatey": "python",
            "homebrew": "python@3.11",
            "apt": "python3",
            "dnf": "python3",
            "pacman": "python",
        },
    },
    "node": {
        "version": "18+",
        "priority": 2,
        "package_managers": [
            "winget",
            "chocolatey",
            "homebrew",
            "apt",
            "dnf",
            "pacman",
        ],
        "package_names": {
            "winget": "OpenJS.NodeJS",
            "chocolatey": "nodejs",
            "homebrew": "node",
            "apt": "nodejs",
            "dnf": "nodejs",
            "pacman": "nodejs",
        },
    },
    "git": {
        "version": "2.30+",
        "priority": 3,
        "package_managers": [
            "winget",
            "chocolatey",
            "homebrew",
            "apt",
            "dnf",
            "pacman",
        ],
        "package_names": {
            "winget": "Git.Git",
            "chocolatey": "git",
            "homebrew": "git",
            "apt": "git",
            "dnf": "git",
            "pacman": "git",
        },
    },
}


# =============================================================================
# MAIN CLASS
# =============================================================================


class RuntimeManager:
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

        except Exception as e:
            logger.error(f"Failed to initialize RuntimeManager: {e}")
            raise RuntimeManagerError(
                runtime_name="runtime_manager",
                operation="initialization",
                reason=f"Failed to initialize runtime manager: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

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
                raise ValidationError(
                    component="runtime_check",
                    validation_type="input_validation",
                    reason="Runtime name must not be empty",
                    details="Runtime parameter must be a non-empty string",
                )

            from ...ui.common.progress import create_spinner

            with create_spinner(f"Checking [bold cyan]{runtime}[/bold cyan]...") as (
                progress,
                task,
            ):
                if runtime not in RUNTIMES:
                    progress.update(
                        task, description=f"Runtime {runtime} not supported"
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
                        task, description=f"Runtime {runtime} already installed"
                    )
                    return RuntimeResult(
                        success=available,
                        runtime_name=runtime,
                        version=version,
                        path=shutil.which(runtime) if available else None,
                        message=f"Runtime {runtime} {'available' if available else 'not found'}",
                        error=None if available else f"Runtime {runtime} not installed",
                    )

                # Check runtime
                try:
                    available, version = self._check_runtime_installation(runtime)
                except Exception as e:
                    logger.warning(
                        f"Failed to check runtime installation for {runtime}: {e}"
                    )
                    available, version = False, None

                self.cache[runtime] = (available, version)

                progress.update(
                    task,
                    description=f"Runtime {runtime} {'available' if available else 'not found'}",
                )
                return RuntimeResult(
                    success=available,
                    runtime_name=runtime,
                    version=version,
                    path=shutil.which(runtime) if available else None,
                    message=f"Runtime {runtime} {'available' if available else 'not found'}",
                    error=None if available else f"Runtime {runtime} not installed",
                )

        except (RuntimeManagerError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in check_runtime: {e}")
            raise RuntimeManagerError(
                runtime_name=runtime,
                operation="check",
                reason=f"Failed to check runtime: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def install_runtime(
        self, runtime: str, extra_pm_args: Optional[List[str]] = None
    ) -> RuntimeResult:
        """
        Install a runtime.

        Args:
            runtime: Name of the runtime to install
            extra_pm_args: Extra arguments to pass to the package manager (optional)

        Returns:
            RuntimeResult: Result of the installation operation

        Raises:
            RuntimeManagerError: If runtime installation fails
            InstallationError: If installation process fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not runtime:
                raise ValidationError(
                    component="runtime_installation",
                    validation_type="input_validation",
                    reason="Runtime name must not be empty",
                    details="Runtime parameter must be a non-empty string",
                )

            from ...ui.common.progress import create_spinner

            with create_spinner(f"Installing [bold cyan]{runtime}[/bold cyan]...") as (
                progress,
                task,
            ):
                if runtime not in RUNTIMES:
                    return RuntimeResult(
                        success=False,
                        runtime_name=runtime,
                        message=f"Runtime {runtime} not supported",
                        error=f"Runtime {runtime} not supported",
                    )

                # Check if already installed
                try:
                    available, version = self._check_runtime_installation(runtime)
                except Exception as e:
                    logger.warning(
                        f"Failed to check runtime installation for {runtime}: {e}"
                    )
                    available, version = False, None

                if available:
                    progress.update(
                        task,
                        description=f"Runtime {runtime} already installed (version {version})",
                    )
                    return RuntimeResult(
                        success=True,
                        runtime_name=runtime,
                        version=version,
                        path=shutil.which(runtime),
                        message=f"Runtime {runtime} already installed (version {version})",
                    )

                # Ensure a package manager is available
                try:
                    from .package_manager import package_manager

                    preferred = RUNTIMES[runtime].get("package_managers")
                    pm_result = package_manager.ensure_manager(preferred)
                except Exception as e:
                    logger.error(f"Failed to ensure package manager for {runtime}: {e}")
                    raise InstallationError(
                        component=runtime,
                        operation="ensure_package_manager",
                        reason=f"Failed to ensure package manager: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                if not pm_result.success:
                    progress.update(
                        task,
                        description=f"No package manager available for {runtime}",
                    )
                    # Optionally print the tips panel if present
                    if getattr(pm_result, "panel", None) is not None:
                        try:
                            from ...ui.common.console import console

                            console.print(pm_result.panel)
                        except Exception as e:
                            logger.warning(
                                f"Failed to print package manager panel: {e}"
                            )

                    return RuntimeResult(
                        success=False,
                        runtime_name=runtime,
                        message=f"No package manager available for {runtime}",
                        error=pm_result.error or "no_package_manager",
                    )

                # Get package name
                package_name = RUNTIMES[runtime]["package_names"].get(
                    pm_result.package_manager_name
                )
                if not package_name:
                    progress.update(
                        task,
                        description=f"No package found for {runtime} in {pm_result.package_manager_name}",
                    )
                    return RuntimeResult(
                        success=False,
                        runtime_name=runtime,
                        message=f"No package found for {runtime} in {pm_result.package_manager_name}",
                        error=f"No package found for {runtime} in {pm_result.package_manager_name}",
                    )

                # Install via package manager
                try:
                    success = package_manager.install_package(
                        package_name,
                        pm_result.package_manager_name,
                        extra_args=extra_pm_args,
                    ).success
                except Exception as e:
                    logger.error(
                        f"Failed to install package {package_name} for {runtime}: {e}"
                    )
                    raise InstallationError(
                        component=runtime,
                        operation="install_package",
                        reason=f"Failed to install package {package_name}: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                if success:
                    # Re-check after installation
                    try:
                        available, version = self._check_runtime_installation(runtime)
                        self.cache[runtime] = (available, version)
                    except Exception as e:
                        logger.warning(
                            f"Failed to re-check runtime installation for {runtime}: {e}"
                        )
                        available, version = False, None

                    return RuntimeResult(
                        success=True,
                        runtime_name=runtime,
                        version=version,
                        path=shutil.which(runtime) if available else None,
                        message=f"Runtime {runtime} installed successfully",
                    )
                else:
                    return RuntimeResult(
                        success=False,
                        runtime_name=runtime,
                        message=f"Failed to install runtime {runtime}",
                        error="Installation failed",
                    )

        except (RuntimeManagerError, InstallationError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in install_runtime: {e}")
            raise RuntimeManagerError(
                runtime_name=runtime,
                operation="installation",
                reason=f"Failed to install runtime: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def check_and_install_runtimes(
        self, runtimes: List[str]
    ) -> Dict[str, RuntimeResult]:
        """
        Check and install multiple runtimes.

        Args:
            runtimes: List of runtime names to check and install

        Returns:
            Dict[str, RuntimeResult]: Results for each runtime

        Raises:
            RuntimeManagerError: If runtime check/installation fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not runtimes:
                raise ValidationError(
                    component="check_and_install_runtimes",
                    validation_type="input_validation",
                    reason="Runtimes list must not be empty",
                    details="Runtimes parameter must be a non-empty list",
                )

            if not isinstance(runtimes, list):
                raise ValidationError(
                    component="check_and_install_runtimes",
                    validation_type="input_validation",
                    reason="Runtimes must be a list",
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
                    available, version = self._check_runtime_installation(runtime)
                    if available:
                        results[runtime] = RuntimeResult(
                            success=True,
                            runtime_name=runtime,
                            version=version,
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

        except (RuntimeManagerError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in check_and_install_runtimes: {e}")
            raise RuntimeManagerError(
                runtime_name="runtime_manager",
                operation="check_and_install",
                reason=f"Failed to check and install runtimes: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_installation_status(self, runtimes: List[str] = None) -> Dict[str, Dict]:
        """
        Get comprehensive installation status for runtimes.

        Args:
            runtimes: List of runtime names to check (optional)

        Returns:
            Dict[str, Dict]: Status information for each runtime

        Raises:
            RuntimeManagerError: If status retrieval fails
        """
        try:
            from ...ui.common.progress import create_spinner

            if runtimes is None:
                runtimes = list(RUNTIMES.keys())

            status = {}
            for runtime in runtimes:
                with create_spinner(
                    f"Checking [bold cyan]{runtime}[/bold cyan]..."
                ) as (
                    progress,
                    task,
                ):
                    try:
                        available, version = self._check_runtime_installation(runtime)
                        status[runtime] = {
                            "installed": available,
                            "version": version,
                            "path": shutil.which(runtime) if available else None,
                            "supported": runtime in RUNTIMES,
                        }
                        progress.update(
                            task,
                            description=f"Runtime {runtime} {'available' if available else 'not found'}",
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
            raise RuntimeManagerError(
                runtime_name="runtime_manager",
                operation="get_status",
                reason=f"Failed to get installation status: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _check_runtime_installation(self, runtime: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a runtime is installed and return version.

        Args:
            runtime: Name of the runtime to check

        Returns:
            Tuple[bool, Optional[str]]: (available, version)

        Raises:
            RuntimeManagerError: If runtime check fails
        """
        try:
            # Input validation
            if not runtime:
                raise ValidationError(
                    component="check_runtime_installation",
                    validation_type="input_validation",
                    reason="Runtime name must not be empty",
                    details="Runtime parameter must be a non-empty string",
                )

            if runtime == "python":
                return self._check_python()
            elif runtime == "node":
                return self._check_node()
            elif runtime == "git":
                return self._check_git()
            else:
                return False, None

        except ValidationError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _check_runtime_installation: {e}")
            raise RuntimeManagerError(
                runtime_name=runtime,
                operation="check_installation",
                reason=f"Failed to check runtime installation: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _check_python(self) -> Tuple[bool, Optional[str]]:
        """
        Check Python installation.

        Returns:
            Tuple[bool, Optional[str]]: (available, version)

        Raises:
            RuntimeManagerError: If Python check fails
        """
        try:
            python_cmds = ["python3", "python", "py"]

            for cmd in python_cmds:
                try:
                    if CLIUtils().check_command_available(cmd):
                        try:
                            result = run_silent([cmd, "--version"])
                            if result.success and result.stdout.strip():
                                version = result.stdout.strip().split()[1]
                                version_parts = [int(x) for x in version.split(".")]
                                if version_parts >= [3, 8]:
                                    # Optional: enforce minimum version from config
                                    min_spec = RUNTIMES["python"].get("version")
                                    if self._satisfies_min_version(version, min_spec):
                                        return True, version
                        except (IndexError, ValueError) as e:
                            logger.debug(
                                f"Failed to parse Python version for {cmd}: {e}"
                            )
                            continue
                        except Exception as e:
                            logger.warning(
                                f"Failed to check Python version for {cmd}: {e}"
                            )
                            continue
                except Exception as e:
                    logger.warning(f"Failed to check tool availability for {cmd}: {e}")
                    continue

            return False, None

        except Exception as e:
            logger.error(f"Unexpected error in _check_python: {e}")
            raise RuntimeManagerError(
                runtime_name="python",
                operation="check_python",
                reason=f"Failed to check Python installation: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _check_node(self) -> Tuple[bool, Optional[str]]:
        """
        Check Node.js installation.

        Returns:
            Tuple[bool, Optional[str]]: (available, version)

        Raises:
            RuntimeManagerError: If Node.js check fails
        """
        try:
            try:
                if CLIUtils().check_command_available("node"):
                    try:
                        result = run_silent(["node", "--version"])
                        if result.success and result.stdout.strip():
                            version = result.stdout.strip().lstrip("v")
                            # Enforce minimum version if specified
                            min_spec = RUNTIMES["node"].get("version")
                            if self._satisfies_min_version(version, min_spec):
                                return True, version
                    except (IndexError, ValueError) as e:
                        logger.debug(f"Failed to parse Node.js version: {e}")
                    except Exception as e:
                        logger.warning(f"Failed to check Node.js version: {e}")
            except Exception as e:
                logger.warning(f"Failed to check Node.js availability: {e}")

            return False, None

        except Exception as e:
            logger.error(f"Unexpected error in _check_node: {e}")
            raise RuntimeManagerError(
                runtime_name="node",
                operation="check_node",
                reason=f"Failed to check Node.js installation: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _check_git(self) -> Tuple[bool, Optional[str]]:
        """
        Check Git installation.

        Returns:
            Tuple[bool, Optional[str]]: (available, version)

        Raises:
            RuntimeManagerError: If Git check fails
        """
        try:
            try:
                if CLIUtils().check_command_available("git"):
                    try:
                        result = run_silent(["git", "--version"])
                        if result.success and result.stdout.strip():
                            version = result.stdout.strip().split()[2]
                            min_spec = RUNTIMES["git"].get("version")
                            if self._satisfies_min_version(version, min_spec):
                                return True, version
                    except (IndexError, ValueError) as e:
                        logger.debug(f"Failed to parse Git version: {e}")
                    except Exception as e:
                        logger.warning(f"Failed to check Git version: {e}")
            except Exception as e:
                logger.warning(f"Failed to check Git availability: {e}")

            return False, None

        except Exception as e:
            logger.error(f"Unexpected error in _check_git: {e}")
            raise RuntimeManagerError(
                runtime_name="git",
                operation="check_git",
                reason=f"Failed to check Git installation: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _satisfies_min_version(
        self, actual: Optional[str], min_spec: Optional[str]
    ) -> bool:
        """
        Return True if actual version satisfies min_spec like '18+' or '2.30+'.

        Args:
            actual: Actual version string
            min_spec: Minimum version specification

        Returns:
            bool: True if version satisfies minimum requirement

        If min_spec is None or invalid, default to True.
        """
        try:
            if not actual or not min_spec or not min_spec.endswith("+"):
                return True

            min_version = min_spec[:-1]

            def parse(v: str) -> List[int]:
                return [int(x) for x in v.split(".") if x.isdigit()]

            a = parse(actual)
            m = parse(min_version)
            # pad shorter list with zeros
            length = max(len(a), len(m))
            a += [0] * (length - len(a))
            m += [0] * (length - len(m))
            return a >= m

        except Exception as e:
            logger.warning(f"Failed to parse version comparison: {e}")
            return True


# GLOBAL INSTANCE
########################################################

runtime_manager = RuntimeManager()
