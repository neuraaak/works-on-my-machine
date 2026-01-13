#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PACKAGE MANAGER - System Package Manager Management
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Package Manager for Works On My Machine.

Manages system package managers (winget, chocolatey, homebrew, apt, etc.).
Provides unified interface for detecting, checking, and installing packages
across different package managers and platforms.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import os
import platform
from dataclasses import dataclass

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.dependencies import SystemPkgManagerInterfaceError
from ...exceptions.womm_deployment import DependencyServiceError
from ...services import CommandRunnerService, SystemPackageManagerService
from ...shared.configs.dependencies import SystemPackageManagerConfig
from ...shared.results import BaseResult, PackageManagerResult
from ...ui.common import ezconsole, ezprinter
from ...ui.dependencies import display_system_table

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)


# ///////////////////////////////////////////////////////////////
# MODELS
# ///////////////////////////////////////////////////////////////


@dataclass
class BestManagerInfo:
    """Information about the best available package manager."""

    manager_name: str
    version: str | None = None


# ///////////////////////////////////////////////////////////////
# PACKAGE MANAGER DEFINITIONS
# ///////////////////////////////////////////////////////////////

# Import from config instead of defining here
SYSTEM_PACKAGE_MANAGERS = SystemPackageManagerConfig.SYSTEM_PACKAGE_MANAGERS


# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class SystemPackageManagerInterface:
    """Manages system package managers."""

    def __init__(self):
        """
        Initialize the package manager.

        Raises:
            PackageManagerError: If package manager initialization fails
        """
        try:
            self.system = platform.system()
            self.cache = {}
            self._command_runner: CommandRunnerService | None = None
            self._package_manager_service: SystemPackageManagerService | None = None

        except Exception as e:
            logger.error(f"Failed to initialize PackageManager: {e}")
            raise SystemPkgManagerInterfaceError(
                message=f"Failed to initialize package manager: {e}",
                manager_name="package_manager",
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
    def package_manager_service(self) -> SystemPackageManagerService:
        """Lazy load PackageManagerService when needed."""
        if self._package_manager_service is None:
            self._package_manager_service = SystemPackageManagerService()
        return self._package_manager_service

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def detect_available_managers(
        self, show_ui: bool = True
    ) -> dict[str, PackageManagerResult]:
        """
        Detect all available package managers for the current system.

        Args:
            show_ui: Whether to show UI spinner

        Returns:
            dict[str, PackageManagerResult]: Results for each package manager

        Raises:
            PackageManagerError: If package manager detection fails
        """
        try:
            results = {}

            if show_ui:
                with ezprinter.create_spinner(
                    "Checking system package managers..."
                ) as (_progress, _task):
                    for manager_name, _config in SYSTEM_PACKAGE_MANAGERS.items():
                        platform_result = self.package_manager_service.is_manager_for_current_platform(
                            manager_name
                        )
                        if platform_result.is_for_current_platform:
                            try:
                                result = self._check_package_manager_internal(
                                    manager_name, None, None
                                )
                                results[manager_name] = result
                            except Exception as e:
                                logger.warning(
                                    f"Failed to check package manager {manager_name}: {e}"
                                )
                                results[manager_name] = PackageManagerResult(
                                    success=False,
                                    package_manager_name=manager_name,
                                    message=f"Failed to check package manager {manager_name}",
                                    error=str(e),
                                )
            else:
                # No UI version
                for manager_name, _config in SYSTEM_PACKAGE_MANAGERS.items():
                    platform_result = (
                        self.package_manager_service.is_manager_for_current_platform(
                            manager_name
                        )
                    )
                    if platform_result.is_for_current_platform:
                        try:
                            result = self._check_package_manager_internal(
                                manager_name, None, None
                            )
                            results[manager_name] = result
                        except Exception as e:
                            logger.warning(
                                f"Failed to check package manager {manager_name}: {e}"
                            )
                            results[manager_name] = PackageManagerResult(
                                success=False,
                                package_manager_name=manager_name,
                                message=f"Failed to check package manager {manager_name}",
                                error=str(e),
                            )

            return results

        except Exception as e:
            logger.error(f"Unexpected error in detect_available_managers: {e}")
            raise SystemPkgManagerInterfaceError(
                manager_name="package_manager",
                operation="detect_available_managers",
                message=f"Failed to detect available managers: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def check_all_managers(self) -> dict[str, PackageManagerResult]:
        """
        Check all system package managers with a single spinner and display results.

        Uses a single spinner with status updates, then displays a summary table.

        Returns:
            Dictionary mapping manager names to PackageManagerResult objects
        """
        results = {}

        with ezprinter.create_spinner_with_status(
            "Checking system package manager availability..."
        ) as (progress, task):
            progress.update(task, status="Initializing...")

            # Get list of managers for current platform
            platform_managers = []
            for manager_name in SYSTEM_PACKAGE_MANAGERS:
                platform_result = (
                    self.package_manager_service.is_manager_for_current_platform(
                        manager_name
                    )
                )
                if platform_result.is_for_current_platform:
                    platform_managers.append(manager_name)

            for manager_name in platform_managers:
                progress.update(task, status=f"Checking {manager_name}")

                try:
                    result = self._check_package_manager_internal(
                        manager_name, None, None
                    )
                    results[manager_name] = result
                except Exception as e:
                    logger.warning(f"Failed to check {manager_name}: {e}")
                    results[manager_name] = PackageManagerResult(
                        success=False,
                        package_manager_name=manager_name,
                        message=f"Failed to check {manager_name}",
                        error=str(e),
                    )

            progress.update(task, status="Check completed")

        # Display results via UI
        print()
        display_system_table(results)

        return results

    def check_package_manager(
        self, manager_name: str, show_ui: bool = True, verbose: bool = False
    ) -> PackageManagerResult:
        """
        Check if a package manager is available and display the result.

        Args:
            manager_name: Name of the package manager to check
            show_ui: Whether to show spinner UI
            verbose: Whether to show detailed information

        Returns:
            PackageManagerResult: Result of the check operation

        Raises:
            PackageManagerError: If package manager check fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not manager_name:
                raise ValidationServiceError(
                    component="package_manager_check",
                    validation_type="input_validation",
                    message="Manager name must not be empty",
                    details="Manager name parameter must be a non-empty string",
                )

            if show_ui:
                with ezprinter.create_spinner(f"Checking {manager_name}...") as (
                    progress,
                    task,
                ):
                    result = self._check_package_manager_internal(
                        manager_name, progress, task
                    )
            else:
                result = self._check_package_manager_internal(manager_name, None, None)

            # Display result
            if result.success:
                msg = f"{manager_name} is available"
                if result.version:
                    msg += f" (version {result.version})"
                ezprinter.success(msg)

                if verbose:
                    if result.platform:
                        ezprinter.info(f"Platform: {result.platform}")
                    if result.priority is not None:
                        ezprinter.info(f"Priority: {result.priority}")
            else:
                ezprinter.error(f"{manager_name} is not available")
                if verbose and result.error:
                    ezprinter.info(f"Error: {result.error}")

            return result

        except (SystemPkgManagerInterfaceError, ValidationServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in check_package_manager: {e}")
            raise SystemPkgManagerInterfaceError(
                manager_name=manager_name,
                operation="check",
                message=f"Failed to check package manager: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _check_package_manager_internal(
        self, manager_name: str, progress, task
    ) -> PackageManagerResult:
        """Internal method to check package manager without UI."""
        if manager_name not in SYSTEM_PACKAGE_MANAGERS:
            if progress:
                progress.update(
                    task,
                    description=f"Package manager {manager_name} not supported",
                )
            return PackageManagerResult(
                success=False,
                package_manager_name=manager_name,
                message=f"Package manager {manager_name} not supported",
                error=f"Package manager {manager_name} not supported",
            )

        # Check cache first
        if manager_name in self.cache:
            available, version = self.cache[manager_name]
            config = SYSTEM_PACKAGE_MANAGERS[manager_name]
            if progress:
                progress.update(
                    task,
                    description=f"Package manager {manager_name} {'available' if available else 'not found'}",
                )
            return PackageManagerResult(
                success=available,
                package_manager_name=manager_name,
                version=version,
                platform=config["platform"],
                priority=config["priority"],
                message=f"Package manager {manager_name} {'available' if available else 'not found'}",
                error=(
                    None
                    if available
                    else f"Package manager {manager_name} not installed"
                ),
            )

        # Check if manager is available
        try:
            avail_result = self.package_manager_service.check_manager_availability(
                manager_name
            )
            available = avail_result.is_available
            version = avail_result.version
        except Exception as e:
            logger.warning(f"Failed to check availability for {manager_name}: {e}")
            available, version = False, None

        self.cache[manager_name] = (available, version)

        config = SYSTEM_PACKAGE_MANAGERS[manager_name]
        if progress:
            progress.update(
                task,
                description=f"Package manager {manager_name} {'available' if available else 'not found'}",
            )
        return PackageManagerResult(
            success=available,
            package_manager_name=manager_name,
            version=version,
            platform=config["platform"],
            priority=config["priority"],
            message=f"Package manager {manager_name} {'available' if available else 'not found'}",
            error=(
                None if available else f"Package manager {manager_name} not installed"
            ),
        )

    def get_best_available_manager(
        self, show_ui: bool = True
    ) -> BestManagerInfo | None:
        """
        Get the best available package manager for the current system.

        Args:
            show_ui: Whether to show UI (spinner and table)

        Returns:
            BestManagerInfo | None: Best manager info with name and version, or None if none available

        Raises:
            PackageManagerError: If package manager detection fails
        """
        try:
            if show_ui:
                ezprinter.info(
                    "Determining best system package manager for your machine and checking their availability..."
                )

            available_managers = []
            available_managers_dict = {}

            # Check availability with spinner
            if show_ui:
                with ezprinter.create_spinner(
                    "Checking system package managers..."
                ) as (_progress, _task):
                    for manager_name, config in SYSTEM_PACKAGE_MANAGERS.items():
                        platform_result = self.package_manager_service.is_manager_for_current_platform(
                            manager_name
                        )
                        if platform_result.is_for_current_platform:
                            try:
                                avail_result = self.package_manager_service.check_manager_availability(
                                    manager_name
                                )
                                if avail_result.is_available:
                                    available_managers.append(
                                        (manager_name, config["priority"])
                                    )
                                    available_managers_dict[manager_name] = (
                                        avail_result.version or "unknown"
                                    )
                            except Exception as e:
                                logger.warning(
                                    f"Failed to check availability for {manager_name}: {e}"
                                )
                # Exit spinner context before displaying table
            else:
                # No UI version
                for manager_name, config in SYSTEM_PACKAGE_MANAGERS.items():
                    platform_result = (
                        self.package_manager_service.is_manager_for_current_platform(
                            manager_name
                        )
                    )
                    if platform_result.is_for_current_platform:
                        try:
                            avail_result = (
                                self.package_manager_service.check_manager_availability(
                                    manager_name
                                )
                            )
                            if avail_result.is_available:
                                available_managers.append(
                                    (manager_name, config["priority"])
                                )
                                available_managers_dict[manager_name] = (
                                    avail_result.version or "unknown"
                                )
                        except Exception as e:
                            logger.warning(
                                f"Failed to check availability for {manager_name}: {e}"
                            )

            # Display table AFTER spinner exits
            if show_ui and available_managers_dict:
                ezconsole.print()
                table = ezprinter.create_dependency_table(available_managers_dict)
                ezconsole.print(table)
                ezconsole.print()

            if available_managers:
                # Sort by priority (lower number = higher priority)
                available_managers.sort(key=lambda x: x[1])
                best_manager = available_managers[0][0]
                best_version = available_managers_dict.get(best_manager, "unknown")
                return BestManagerInfo(manager_name=best_manager, version=best_version)

            return None

        except Exception as e:
            logger.error(f"Unexpected error in get_best_available_manager: {e}")
            raise SystemPkgManagerInterfaceError(
                manager_name="package_manager",
                operation="get_best_available",
                message=f"Failed to get best available manager: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def show_best_manager(self, verbose: bool = False) -> BestManagerInfo | None:
        """
        Get and display the best available package manager.

        Args:
            verbose: Whether to show additional details

        Returns:
            BestManagerInfo | None: Best manager info, or None if none available
        """
        from ...ui.system import display_best_manager

        best = self.get_best_available_manager(show_ui=False)

        # Get config for verbose display
        platform_str = None
        priority = None
        if best:
            config = self.package_manager_service.get_manager_config(best.manager_name)
            if config:
                platform_str = config.get("platform")
                priority = config.get("priority")

        display_best_manager(
            manager_name=best.manager_name if best else None,
            version=best.version if best else None,
            platform=platform_str,
            priority=priority,
            verbose=verbose,
        )

        return best

    def list_managers(self, verbose: bool = False) -> dict:
        """
        Get and display the list of all system package managers.

        Args:
            verbose: Whether to show additional details

        Returns:
            dict: Status dictionary of all managers
        """
        from ...ui.system import display_system_managers_list

        status = self.get_installation_status()
        display_system_managers_list(status, verbose)
        return status

    def ensure_manager(
        self, preferred: list[str] | None = None
    ) -> PackageManagerResult:
        """
        Ensure that at least one package manager is available.

        Args:
            preferred: List of preferred package managers (optional)

        Returns:
            PackageManagerResult: Result of the ensure operation

        Raises:
            PackageManagerError: If package manager ensure fails
            ValidationError: If validation fails
        """
        try:
            # Build candidate list
            def is_supported(m: str) -> bool:
                platform_result = (
                    self.package_manager_service.is_manager_for_current_platform(m)
                )
                return platform_result.is_for_current_platform

            candidates: list[str]
            if preferred:
                # Input validation for preferred list
                if not isinstance(preferred, list):
                    raise ValidationServiceError(
                        component="ensure_manager",
                        validation_type="input_validation",
                        message="Preferred must be a list",
                        details="Preferred parameter must be a list of strings",
                    )
                candidates = [m for m in preferred if is_supported(m)]
            else:
                candidates = [
                    m
                    for m in SYSTEM_PACKAGE_MANAGERS
                    if self.package_manager_service.is_manager_for_current_platform(
                        m
                    ).is_for_current_platform
                ]

            # Gather available with priorities
            available: list[tuple[str, int]] = []
            for m in candidates:
                try:
                    avail_result = (
                        self.package_manager_service.check_manager_availability(m)
                    )
                    if avail_result.is_available:
                        available.append((m, SYSTEM_PACKAGE_MANAGERS[m]["priority"]))
                except Exception as e:
                    logger.warning(f"Failed to check availability for {m}: {e}")

            if available:
                available.sort(key=lambda x: x[1])
                best = available[0][0]
                try:
                    ver_result = (
                        self.package_manager_service.check_manager_availability(best)
                    )
                    ver = ver_result.version
                except Exception as e:
                    logger.warning(f"Failed to get version for {best}: {e}")
                    ver = None

                return PackageManagerResult(
                    success=True,
                    package_manager_name=best,
                    version=ver,
                    platform=SYSTEM_PACKAGE_MANAGERS[best]["platform"],
                    priority=SYSTEM_PACKAGE_MANAGERS[best]["priority"],
                    message=f"Using package manager: {best}",
                )

            # No manager available → provide tips panel
            try:
                panel = self._build_no_pm_panel(candidates)
            except Exception as e:
                logger.warning(f"Failed to build no PM panel: {e}")
                panel = None

            return PackageManagerResult(
                success=False,
                package_manager_name="none",
                message="No package manager available on this system",
                error="no_package_manager",
                panel=panel,
            )

        except (SystemPkgManagerInterfaceError, ValidationServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in ensure_manager: {e}")
            raise SystemPkgManagerInterfaceError(
                manager_name="package_manager",
                operation="ensure",
                message=f"Failed to ensure package manager: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _build_no_pm_panel(self, candidates: list[str]) -> object:
        """
        Create a tips panel to guide user to install a package manager safely.

        Args:
            candidates: List of candidate package managers

        Returns:
            Any: Rich panel with installation tips

        Raises:
            PackageManagerError: If panel creation fails
        """
        try:
            # Input validation
            if not isinstance(candidates, list):
                raise ValidationServiceError(
                    component="build_no_pm_panel",
                    validation_type="input_validation",
                    message="Candidates must be a list",
                    details="Candidates parameter must be a list of strings",
                )

            sys_name = self.system.lower()

            supported_on_platform = [
                m
                for m in SYSTEM_PACKAGE_MANAGERS
                if self.package_manager_service.is_manager_for_current_platform(
                    m
                ).is_for_current_platform
            ]

            header: list[str] = []
            if sys_name == "windows":
                header.append(
                    "Aucun gestionnaire de paquets détecté (winget/chocolatey/scoop)."
                )
            elif sys_name == "darwin":
                header.append("Aucun gestionnaire de paquets détecté (Homebrew).")
            else:
                header.append(
                    "Aucun gestionnaire de paquets détecté (apt/dnf/pacman/zypper)."
                )

            if candidates:
                header.append(
                    "Candidats compatibles pour cette opération: "
                    + ", ".join(candidates)
                )
            else:
                header.append(
                    "Gestionnaires supportés sur cette plateforme: "
                    + ", ".join(supported_on_platform)
                )

            header.append("")

            instructions = SystemPackageManagerConfig.get_installation_instructions(
                sys_name
            )
            body = instructions["body"]

            content = "\n".join(header + body)
            return ezprinter.create_info_panel(
                "Gestionnaire de paquets requis",
                content,
                style="yellow",
                border_style="yellow",
            )

        except (SystemPkgManagerInterfaceError, ValidationServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _build_no_pm_panel: {e}")
            raise SystemPkgManagerInterfaceError(
                manager_name="package_manager",
                operation="build_panel",
                message=f"Failed to build no PM panel: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def install_package(
        self,
        package_name: str,
        manager_name: str | None = None,
        extra_args: list[str] | None = None,
    ) -> PackageManagerResult:
        """
        Install a package using the specified or best available package manager.

        Args:
            package_name: Name of the package to install
            manager_name: Name of the package manager to use (optional)
            extra_args: Extra arguments to pass to the package manager (optional)

        Returns:
            PackageManagerResult: Result of the installation operation

        Raises:
            PackageManagerError: If package installation fails
            InstallationError: If installation process fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not package_name:
                raise ValidationServiceError(
                    component="install_package",
                    validation_type="input_validation",
                    message="Package name must not be empty",
                    details="Package name parameter must be a non-empty string",
                )

            # DRY-RUN: skip real installation when WOMM_DRY_RUN is enabled
            if os.environ.get("WOMM_DRY_RUN", "").lower() in ("1", "true", "yes"):
                try:
                    best_info = (
                        self.get_best_available_manager() if not manager_name else None
                    )
                    selected_manager = manager_name or (
                        best_info.manager_name if best_info else None
                    )
                except Exception as e:
                    logger.warning(
                        f"Failed to get best available manager for dry-run: {e}"
                    )
                    selected_manager = manager_name

                if not selected_manager:
                    return PackageManagerResult(
                        success=False,
                        package_manager_name="none",
                        message="No package manager available (dry-run)",
                        error="No package manager available",
                    )
                cfg = SYSTEM_PACKAGE_MANAGERS.get(selected_manager, {})
                args_desc = f" args={extra_args}" if extra_args else ""
                return PackageManagerResult(
                    success=True,
                    package_manager_name=selected_manager,
                    version=None,
                    platform=cfg.get("platform"),
                    priority=cfg.get("priority"),
                    message=f"[dry-run] Would install {package_name} via {selected_manager}{args_desc}",
                )

            if manager_name is None:
                try:
                    best_info = self.get_best_available_manager()
                    manager_name = best_info.manager_name if best_info else None
                except Exception as e:
                    logger.error(f"Failed to get best available manager: {e}")
                    return PackageManagerResult(
                        success=False,
                        package_manager_name="none",
                        message="Failed to get best available manager",
                        error=str(e),
                    )

                if not manager_name:
                    return PackageManagerResult(
                        success=False,
                        package_manager_name="none",
                        message="No package manager available",
                        error="No package manager available",
                    )

            if manager_name not in SYSTEM_PACKAGE_MANAGERS:
                return PackageManagerResult(
                    success=False,
                    package_manager_name=manager_name,
                    message=f"Package manager {manager_name} not supported",
                    error=f"Package manager {manager_name} not supported",
                )

            # Check if manager is available
            try:
                (
                    available,
                    version,
                ) = self.package_manager_service.check_manager_availability(
                    manager_name
                )
            except Exception as e:
                logger.warning(f"Failed to check availability for {manager_name}: {e}")
                available, version = False, None

            if not available:
                return PackageManagerResult(
                    success=False,
                    package_manager_name=manager_name,
                    message=f"Package manager {manager_name} not available",
                    error=f"Package manager {manager_name} not installed",
                )

            # Install package
            try:
                success = self._install_package_via_manager(
                    manager_name, package_name, _extra_args=extra_args
                )
            except Exception as e:
                logger.error(
                    f"Failed to install package {package_name} via {manager_name}: {e}"
                )
                raise DependencyServiceError(
                    component=package_name,
                    operation="install",
                    message=f"Failed to install package via {manager_name}: {e}",
                    details=f"Exception type: {type(e).__name__}",
                ) from e

            config = SYSTEM_PACKAGE_MANAGERS[manager_name]
            if success:
                return PackageManagerResult(
                    success=True,
                    package_manager_name=manager_name,
                    version=version,
                    platform=config["platform"],
                    priority=config["priority"],
                    message=f"Package {package_name} installed successfully via {manager_name}",
                )
            else:
                return PackageManagerResult(
                    success=False,
                    package_manager_name=manager_name,
                    version=version,
                    platform=config["platform"],
                    priority=config["priority"],
                    message=f"Failed to install package {package_name} via {manager_name}",
                    error="Installation failed",
                )

        except (
            SystemPkgManagerInterfaceError,
            DependencyServiceError,
            ValidationServiceError,
        ):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in install_package: {e}")
            raise SystemPkgManagerInterfaceError(
                manager_name=manager_name or "unknown",
                operation="install_package",
                message=f"Failed to install package: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def search_package(
        self, package_name: str, manager_name: str | None = None
    ) -> PackageManagerResult:
        """
        Search for a package using the specified or best available package manager.

        Args:
            package_name: Name of the package to search for
            manager_name: Name of the package manager to use (optional)

        Returns:
            PackageManagerResult: Result of the search operation

        Raises:
            PackageManagerError: If package search fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not package_name:
                raise ValidationServiceError(
                    component="search_package",
                    validation_type="input_validation",
                    message="Package name must not be empty",
                    details="Package name parameter must be a non-empty string",
                )

            if manager_name is None:
                try:
                    best_info = self.get_best_available_manager()
                    manager_name = best_info.manager_name if best_info else None
                except Exception as e:
                    logger.error(f"Failed to get best available manager: {e}")
                    return PackageManagerResult(
                        success=False,
                        package_manager_name="none",
                        message="Failed to get best available manager",
                        error=str(e),
                    )

                if not manager_name:
                    return PackageManagerResult(
                        success=False,
                        package_manager_name="none",
                        message="No package manager available",
                        error="No package manager available",
                    )

            if manager_name not in SYSTEM_PACKAGE_MANAGERS:
                return PackageManagerResult(
                    success=False,
                    package_manager_name=manager_name,
                    message=f"Package manager {manager_name} not supported",
                    error=f"Package manager {manager_name} not supported",
                )

            # Check if manager is available
            try:
                (
                    available,
                    version,
                ) = self.package_manager_service.check_manager_availability(
                    manager_name
                )
            except Exception as e:
                logger.warning(f"Failed to check availability for {manager_name}: {e}")
                available, version = False, None

            if not available:
                return PackageManagerResult(
                    success=False,
                    package_manager_name=manager_name,
                    message=f"Package manager {manager_name} not available",
                    error=f"Package manager {manager_name} not installed",
                )

            # Search package
            try:
                result = self._search_package_via_manager(manager_name, package_name)
            except Exception as e:
                logger.error(
                    f"Failed to search package {package_name} via {manager_name}: {e}"
                )
                return PackageManagerResult(
                    success=False,
                    package_manager_name=manager_name,
                    version=version,
                    platform=SYSTEM_PACKAGE_MANAGERS[manager_name]["platform"],
                    priority=SYSTEM_PACKAGE_MANAGERS[manager_name]["priority"],
                    message=f"Failed to search for {package_name} via {manager_name}",
                    error=str(e),
                )

            config = SYSTEM_PACKAGE_MANAGERS[manager_name]
            if result.success:
                return PackageManagerResult(
                    success=True,
                    package_manager_name=manager_name,
                    version=version,
                    platform=config["platform"],
                    priority=config["priority"],
                    message=f"Search results for {package_name} via {manager_name}",
                    error=None,
                )
            else:
                return PackageManagerResult(
                    success=False,
                    package_manager_name=manager_name,
                    version=version,
                    platform=config["platform"],
                    priority=config["priority"],
                    message=f"Failed to search for {package_name} via {manager_name}",
                    error=result.stderr,
                )

        except (SystemPkgManagerInterfaceError, ValidationServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in search_package: {e}")
            raise SystemPkgManagerInterfaceError(
                manager_name=manager_name or "unknown",
                operation="search_package",
                message=f"Failed to search package: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_installation_status(self) -> dict[str, dict]:
        """
        Get comprehensive status of all package managers.

        Returns:
            dict[str, dict]: Status information for each package manager

        Raises:
            PackageManagerError: If status retrieval fails
        """
        try:
            status = {}

            for manager_name, config in SYSTEM_PACKAGE_MANAGERS.items():
                try:
                    avail_result = (
                        self.package_manager_service.check_manager_availability(
                            manager_name
                        )
                    )
                    available = avail_result.is_available
                    version = avail_result.version
                    platform_result = (
                        self.package_manager_service.is_manager_for_current_platform(
                            manager_name
                        )
                    )
                    status[manager_name] = {
                        "available": available,
                        "version": version,
                        "platform": config["platform"],
                        "priority": config["priority"],
                        "description": config.get("description", ""),
                        "supported_on_current_platform": platform_result.is_for_current_platform,
                    }
                except Exception as e:
                    logger.warning(f"Failed to get status for {manager_name}: {e}")
                    status[manager_name] = {
                        "available": False,
                        "version": None,
                        "platform": config["platform"],
                        "priority": config["priority"],
                        "description": config.get("description", ""),
                        "supported_on_current_platform": self._is_manager_for_current_platform(
                            config
                        ),
                    }

            return status

        except Exception as e:
            logger.error(f"Unexpected error in get_installation_status: {e}")
            raise SystemPkgManagerInterfaceError(
                manager_name="package_manager",
                operation="get_status",
                message=f"Failed to get installation status: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _is_manager_for_current_platform(self, config: dict) -> bool:
        """
        Check if a package manager is supported on the current platform.

        Args:
            config: Package manager configuration

        Returns:
            bool: True if supported on current platform, False otherwise
        """
        # Extract manager name from config if possible, otherwise use service method
        manager_name = None
        for name, cfg in SYSTEM_PACKAGE_MANAGERS.items():
            if cfg == config:
                manager_name = name
                break

        if manager_name:
            return self.package_manager_service.is_manager_for_current_platform(
                manager_name
            )

        # Fallback to old logic if manager name not found
        try:
            return (
                config["platform"] == self.system.lower()
                or config["platform"] == "linux"
            )
        except Exception as e:
            logger.warning(f"Failed to check platform compatibility: {e}")
            return False

    def _check_manager_availability(self, manager_name: str) -> tuple[bool, str | None]:
        """
        Check if a package manager is available and return version.

        Args:
            manager_name: Name of the package manager to check

        Returns:
            tuple[bool, str | None]: (available, version)

        Raises:
            PackageManagerError: If availability check fails
        """
        # Delegate to service and extract availability
        result = self.package_manager_service.check_manager_availability(manager_name)
        return (result.is_available, result.version)

    def _install_package_via_manager(
        self,
        manager_name: str,
        package_name: str,
        _extra_args: list[str] | None = None,
    ) -> bool:
        """
        Install a package via a specific package manager.

        Delegates to SystemPackageManagerService which handles command construction
        and execution via SystemPackageManagerConfig.

        Args:
            manager_name: Name of the package manager
            package_name: Name of the package to install
            extra_args: Extra arguments to pass to the package manager (currently unused)

        Returns:
            bool: True if installation successful, False otherwise

        Raises:
            InstallationError: If installation fails
        """
        try:
            # Input validation
            if not manager_name or not package_name:
                raise ValidationServiceError(
                    component="install_package_via_manager",
                    validation_type="input_validation",
                    message="Manager name and package name must not be empty",
                    details="Both parameters must be non-empty strings",
                )

            # Validate manager exists
            if manager_name not in SYSTEM_PACKAGE_MANAGERS:
                logger.error(f"Package manager {manager_name} not supported")
                return False

            # Delegate to service - it handles command construction and execution
            try:
                success = self.package_manager_service.install_package(
                    manager_name=manager_name,
                    package_name=package_name,
                    package_id=package_name,  # Use same as display name by default
                )
                return success
            except Exception as e:
                logger.error(
                    f"Failed to install package {package_name} via {manager_name}: {e}"
                )
                raise DependencyServiceError(
                    component=package_name,
                    operation="execute_install",
                    message=f"Failed to install package: {e}",
                    details=f"Manager: {manager_name}",
                ) from e

        except (DependencyServiceError, ValidationServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _install_package_via_manager: {e}")
            raise DependencyServiceError(
                component=package_name,
                operation="install_via_manager",
                message=f"Failed to install package via manager: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _search_package_via_manager(self, manager_name: str, package_name: str):
        """
        Search for a package via a specific package manager.

        Args:
            manager_name: Name of the package manager
            package_name: Name of the package to search for

        Returns:
            BaseResult: Result of the search operation

        Raises:
            PackageManagerError: If search fails
        """
        try:
            # Input validation
            if not manager_name or not package_name:
                raise ValidationServiceError(
                    component="search_package_via_manager",
                    validation_type="input_validation",
                    message="Manager name and package name must not be empty",
                    details="Both parameters must be non-empty strings",
                )

            search_commands = {
                "winget": ["winget", "search", package_name],
                "chocolatey": ["choco", "search", package_name],
                "scoop": ["scoop", "search", package_name],
                "homebrew": ["brew", "search", package_name],
                "apt": ["apt", "search", package_name],
                "dnf": ["dnf", "search", package_name],
                "pacman": ["pacman", "-Ss", package_name],
                "zypper": ["zypper", "search", package_name],
            }

            if manager_name not in search_commands:
                return BaseResult(success=False, stderr="Unsupported package manager")

            try:
                return self.command_runner.run(search_commands[manager_name])
            except Exception as e:
                logger.error(
                    f"Failed to execute search command for {package_name}: {e}"
                )
                raise SystemPkgManagerInterfaceError(
                    manager_name=manager_name,
                    operation="execute_search",
                    message=f"Failed to execute search command: {e}",
                    details=f"Command: {' '.join(search_commands[manager_name])}",
                ) from e

        except (SystemPkgManagerInterfaceError, ValidationServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _search_package_via_manager: {e}")
            raise SystemPkgManagerInterfaceError(
                manager_name=manager_name,
                operation="search_via_manager",
                message=f"Failed to search package via manager: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e
