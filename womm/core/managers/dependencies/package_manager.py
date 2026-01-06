#!/usr/bin/env python3
"""
Package Manager for Works On My Machine.
Manages system package managers (winget, chocolatey, homebrew, apt, etc.).
"""

import logging
import os
import platform
import shlex
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ....common.results import BaseResult
from ...exceptions.dependencies import (
    InstallationError,
    PackageManagerError,
    ValidationError,
)
from ...ui.common.panels import create_info_panel
from ...utils.cli_utils import CLIUtils, run_command, run_silent

# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class PackageManagerResult(BaseResult):
    """Result of a package manager operation."""

    package_manager_name: str = ""
    version: Optional[str] = None
    platform: Optional[str] = None
    priority: Optional[int] = None
    panel: Optional[Any] = None


# =============================================================================
# PACKAGE MANAGER DEFINITIONS
# =============================================================================

SYSTEM_PACKAGE_MANAGERS = {
    "winget": {
        "platform": "windows",
        "priority": 1,
        "description": "Microsoft Windows Package Manager",
        "install_command": "winget install",
        "search_command": "winget search",
        "list_command": "winget list",
    },
    "chocolatey": {
        "platform": "windows",
        "priority": 2,
        "description": "Chocolatey Package Manager",
        "install_command": "choco install",
        "search_command": "choco search",
        "list_command": "choco list",
    },
    "scoop": {
        "platform": "windows",
        "priority": 3,
        "description": "Scoop Package Manager",
        "install_command": "scoop install",
        "search_command": "scoop search",
        "list_command": "scoop list",
    },
    "homebrew": {
        "platform": "darwin",
        "priority": 1,
        "description": "Homebrew Package Manager",
        "install_command": "brew install",
        "search_command": "brew search",
        "list_command": "brew list",
    },
    "apt": {
        "platform": "linux",
        "priority": 1,
        "description": "Advanced Package Tool (Debian/Ubuntu)",
        "install_command": "apt install",
        "search_command": "apt search",
        "list_command": "apt list --installed",
    },
    "dnf": {
        "platform": "linux",
        "priority": 2,
        "description": "Dandified YUM (Fedora/RHEL)",
        "install_command": "dnf install",
        "search_command": "dnf search",
        "list_command": "dnf list installed",
    },
    "pacman": {
        "platform": "linux",
        "priority": 3,
        "description": "Pacman Package Manager (Arch Linux)",
        "install_command": "pacman -S",
        "search_command": "pacman -Ss",
        "list_command": "pacman -Q",
    },
    "zypper": {
        "platform": "linux",
        "priority": 4,
        "description": "Zypper Package Manager (openSUSE)",
        "install_command": "zypper install",
        "search_command": "zypper search",
        "list_command": "zypper packages --installed",
    },
}


# =============================================================================
# MAIN CLASS
# =============================================================================


class PackageManager:
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

        except Exception as e:
            logger.error(f"Failed to initialize PackageManager: {e}")
            raise PackageManagerError(
                manager_name="package_manager",
                operation="initialization",
                reason=f"Failed to initialize package manager: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def detect_available_managers(self) -> Dict[str, PackageManagerResult]:
        """
        Detect all available package managers for the current system.

        Returns:
            Dict[str, PackageManagerResult]: Results for each package manager

        Raises:
            PackageManagerError: If package manager detection fails
        """
        try:
            results = {}

            for manager_name, config in SYSTEM_PACKAGE_MANAGERS.items():
                if self._is_manager_for_current_platform(config):
                    try:
                        result = self.check_package_manager(manager_name)
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
            raise PackageManagerError(
                manager_name="package_manager",
                operation="detect_available_managers",
                reason=f"Failed to detect available managers: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def check_package_manager(self, manager_name: str) -> PackageManagerResult:
        """
        Check if a package manager is available.

        Args:
            manager_name: Name of the package manager to check

        Returns:
            PackageManagerResult: Result of the check operation

        Raises:
            PackageManagerError: If package manager check fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not manager_name:
                raise ValidationError(
                    component="package_manager_check",
                    validation_type="input_validation",
                    reason="Manager name must not be empty",
                    details="Manager name parameter must be a non-empty string",
                )

            from ...ui.common.console import print_system
            from ...ui.common.progress import create_spinner

            print_system(f"Checking [bold cyan]{manager_name}[/bold cyan]...")

            with create_spinner(
                f"Checking [bold cyan]{manager_name}[/bold cyan]..."
            ) as (
                progress,
                task,
            ):
                if manager_name not in SYSTEM_PACKAGE_MANAGERS:
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
                    available, version = self._check_manager_availability(manager_name)
                except Exception as e:
                    logger.warning(
                        f"Failed to check availability for {manager_name}: {e}"
                    )
                    available, version = False, None

                self.cache[manager_name] = (available, version)

                config = SYSTEM_PACKAGE_MANAGERS[manager_name]
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

        except (PackageManagerError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in check_package_manager: {e}")
            raise PackageManagerError(
                manager_name=manager_name,
                operation="check",
                reason=f"Failed to check package manager: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_best_available_manager(self) -> Optional[str]:
        """
        Get the best available package manager for the current system.

        Returns:
            Optional[str]: Name of the best available package manager, or None if none available

        Raises:
            PackageManagerError: If package manager detection fails
        """
        try:
            available_managers = []

            for manager_name, config in SYSTEM_PACKAGE_MANAGERS.items():
                if self._is_manager_for_current_platform(config):
                    try:
                        available, _ = self._check_manager_availability(manager_name)
                        if available:
                            available_managers.append(
                                (manager_name, config["priority"])
                            )
                    except Exception as e:
                        logger.warning(
                            f"Failed to check availability for {manager_name}: {e}"
                        )

            if available_managers:
                # Sort by priority (lower number = higher priority)
                available_managers.sort(key=lambda x: x[1])
                return available_managers[0][0]

            return None

        except Exception as e:
            logger.error(f"Unexpected error in get_best_available_manager: {e}")
            raise PackageManagerError(
                manager_name="package_manager",
                operation="get_best_available",
                reason=f"Failed to get best available manager: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def ensure_manager(
        self, preferred: Optional[List[str]] = None
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
                cfg = SYSTEM_PACKAGE_MANAGERS.get(m)
                return bool(cfg and self._is_manager_for_current_platform(cfg))

            candidates: List[str]
            if preferred:
                # Input validation for preferred list
                if not isinstance(preferred, list):
                    raise ValidationError(
                        component="ensure_manager",
                        validation_type="input_validation",
                        reason="Preferred must be a list",
                        details="Preferred parameter must be a list of strings",
                    )
                candidates = [m for m in preferred if is_supported(m)]
            else:
                candidates = [
                    m
                    for m, cfg in SYSTEM_PACKAGE_MANAGERS.items()
                    if self._is_manager_for_current_platform(cfg)
                ]

            # Gather available with priorities
            available: List[tuple[str, int]] = []
            for m in candidates:
                try:
                    ok, _ = self._check_manager_availability(m)
                    if ok:
                        available.append((m, SYSTEM_PACKAGE_MANAGERS[m]["priority"]))
                except Exception as e:
                    logger.warning(f"Failed to check availability for {m}: {e}")

            if available:
                available.sort(key=lambda x: x[1])
                best = available[0][0]
                try:
                    ver = self._check_manager_availability(best)[1]
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

        except (PackageManagerError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in ensure_manager: {e}")
            raise PackageManagerError(
                manager_name="package_manager",
                operation="ensure",
                reason=f"Failed to ensure package manager: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _build_no_pm_panel(self, candidates: List[str]) -> Any:
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
                raise ValidationError(
                    component="build_no_pm_panel",
                    validation_type="input_validation",
                    reason="Candidates must be a list",
                    details="Candidates parameter must be a list of strings",
                )

            sys_name = self.system.lower()

            supported_on_platform = [
                m
                for m, cfg in SYSTEM_PACKAGE_MANAGERS.items()
                if self._is_manager_for_current_platform(cfg)
            ]

            header: List[str] = []
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

            if sys_name == "windows":
                body = [
                    "Recommandé:",
                    "- winget (Microsoft Store): ouvrez le Microsoft Store et installez 'App Installer'.",
                    "- Chocolatey: PowerShell (Run as Administrator):",
                    "  Set-ExecutionPolicy Bypass -Scope Process -Force;",
                    "  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12;",
                    "  iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))",
                    "- Scoop: PowerShell (Run as Administrator):",
                    "  iwr -useb get.scoop.sh | iex",
                ]
            elif sys_name == "darwin":
                body = [
                    "Installez Homebrew:",
                    "- Ouvrez le Terminal puis exécutez:",
                    '  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
                ]
            else:
                body = [
                    "Vérifiez votre distribution Linux et assurez-vous que l'outil par défaut est installé et accessible dans le PATH.",
                ]

            content = "\n".join(header + body)
            return create_info_panel(
                "Gestionnaire de paquets requis",
                content,
                style="yellow",
                border_style="yellow",
            )

        except (PackageManagerError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _build_no_pm_panel: {e}")
            raise PackageManagerError(
                manager_name="package_manager",
                operation="build_panel",
                reason=f"Failed to build no PM panel: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def install_package(
        self,
        package_name: str,
        manager_name: str = None,
        extra_args: Optional[list[str]] = None,
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
                raise ValidationError(
                    component="install_package",
                    validation_type="input_validation",
                    reason="Package name must not be empty",
                    details="Package name parameter must be a non-empty string",
                )

            # DRY-RUN: skip real installation when WOMM_DRY_RUN is enabled
            if os.environ.get("WOMM_DRY_RUN", "").lower() in ("1", "true", "yes"):
                try:
                    selected_manager = manager_name or self.get_best_available_manager()
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
                    manager_name = self.get_best_available_manager()
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
                available, version = self._check_manager_availability(manager_name)
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
                    manager_name, package_name, extra_args=extra_args
                )
            except Exception as e:
                logger.error(
                    f"Failed to install package {package_name} via {manager_name}: {e}"
                )
                raise InstallationError(
                    component=package_name,
                    operation="install",
                    reason=f"Failed to install package via {manager_name}: {e}",
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

        except (PackageManagerError, InstallationError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in install_package: {e}")
            raise PackageManagerError(
                manager_name=manager_name or "unknown",
                operation="install_package",
                reason=f"Failed to install package: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def search_package(
        self, package_name: str, manager_name: str = None
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
                raise ValidationError(
                    component="search_package",
                    validation_type="input_validation",
                    reason="Package name must not be empty",
                    details="Package name parameter must be a non-empty string",
                )

            if manager_name is None:
                try:
                    manager_name = self.get_best_available_manager()
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
                available, version = self._check_manager_availability(manager_name)
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

        except (PackageManagerError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in search_package: {e}")
            raise PackageManagerError(
                manager_name=manager_name or "unknown",
                operation="search_package",
                reason=f"Failed to search package: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_installation_status(self) -> Dict[str, Dict]:
        """
        Get comprehensive status of all package managers.

        Returns:
            Dict[str, Dict]: Status information for each package manager

        Raises:
            PackageManagerError: If status retrieval fails
        """
        try:
            status = {}

            for manager_name, config in SYSTEM_PACKAGE_MANAGERS.items():
                try:
                    available, version = self._check_manager_availability(manager_name)
                    status[manager_name] = {
                        "available": available,
                        "version": version,
                        "platform": config["platform"],
                        "priority": config["priority"],
                        "description": config["description"],
                        "supported_on_current_platform": self._is_manager_for_current_platform(
                            config
                        ),
                    }
                except Exception as e:
                    logger.warning(f"Failed to get status for {manager_name}: {e}")
                    status[manager_name] = {
                        "available": False,
                        "version": None,
                        "platform": config["platform"],
                        "priority": config["priority"],
                        "description": config["description"],
                        "supported_on_current_platform": self._is_manager_for_current_platform(
                            config
                        ),
                    }

            return status

        except Exception as e:
            logger.error(f"Unexpected error in get_installation_status: {e}")
            raise PackageManagerError(
                manager_name="package_manager",
                operation="get_status",
                reason=f"Failed to get installation status: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _is_manager_for_current_platform(self, config: Dict) -> bool:
        """
        Check if a package manager is supported on the current platform.

        Args:
            config: Package manager configuration

        Returns:
            bool: True if supported on current platform, False otherwise
        """
        try:
            return (
                config["platform"] == self.system.lower()
                or config["platform"] == "linux"
            )
        except Exception as e:
            logger.warning(f"Failed to check platform compatibility: {e}")
            return False

    def _check_manager_availability(
        self, manager_name: str
    ) -> tuple[bool, Optional[str]]:
        """
        Check if a package manager is available and return version.

        Args:
            manager_name: Name of the package manager to check

        Returns:
            tuple[bool, Optional[str]]: (available, version)

        Raises:
            PackageManagerError: If availability check fails
        """
        try:
            # Input validation
            if not manager_name:
                raise ValidationError(
                    component="check_manager_availability",
                    validation_type="input_validation",
                    reason="Manager name must not be empty",
                    details="Manager name parameter must be a non-empty string",
                )

            try:
                if not CLIUtils().check_command_available(manager_name):
                    return False, None
            except Exception as e:
                logger.warning(
                    f"Failed to check tool availability for {manager_name}: {e}"
                )
                return False, None

            # Try to get version
            try:
                result = run_silent([manager_name, "--version"])
                if result.success and result.stdout.strip():
                    version = (
                        result.stdout.strip().split()[0]
                        if result.stdout.strip()
                        else "unknown"
                    )
                    return True, version
            except Exception as e:
                logger.debug(f"Failed to get version for {manager_name}: {e}")
                # Continue execution as version check failure is not critical

            return False, None

        except ValidationError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _check_manager_availability: {e}")
            raise PackageManagerError(
                manager_name=manager_name,
                operation="check_availability",
                reason=f"Failed to check manager availability: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _install_package_via_manager(
        self,
        manager_name: str,
        package_name: str,
        extra_args: Optional[list[str]] = None,
    ) -> bool:
        """
        Install a package via a specific package manager.

        Args:
            manager_name: Name of the package manager
            package_name: Name of the package to install
            extra_args: Extra arguments to pass to the package manager

        Returns:
            bool: True if installation successful, False otherwise

        Raises:
            InstallationError: If installation fails
        """
        try:
            # Input validation
            if not manager_name or not package_name:
                raise ValidationError(
                    component="install_package_via_manager",
                    validation_type="input_validation",
                    reason="Manager name and package name must not be empty",
                    details="Both parameters must be non-empty strings",
                )

            SYSTEM_PACKAGE_MANAGERS[manager_name]

            if manager_name == "winget":
                cmd = ["winget", "install", package_name, "--accept-source-agreements"]
            elif manager_name == "chocolatey":
                cmd = ["choco", "install", package_name, "-y"]
            elif manager_name == "scoop":
                cmd = ["scoop", "install", package_name]
            elif manager_name == "homebrew":
                cmd = ["brew", "install", package_name]
            elif manager_name == "apt":
                cmd = [
                    "sudo",
                    "apt",
                    "update",
                    "&&",
                    "sudo",
                    "apt",
                    "install",
                    "-y",
                    package_name,
                ]
            elif manager_name == "dnf":
                cmd = ["sudo", "dnf", "install", "-y", package_name]
            elif manager_name == "pacman":
                cmd = ["sudo", "pacman", "-S", "--noconfirm", package_name]
            elif manager_name == "zypper":
                cmd = ["sudo", "zypper", "install", "-y", package_name]
            else:
                return False

            # Append any extra args provided by the user
            if extra_args:
                # If user provided a raw string somewhere else, ensure we have tokens
                flattened: list[str] = []
                for a in extra_args:
                    if isinstance(a, str):
                        # Split only if it contains spaces and not already a token
                        tokens = shlex.split(a) if " " in a else [a]
                        flattened.extend(tokens)
                    else:
                        flattened.append(str(a))
                cmd.extend(flattened)

            try:
                result = run_command(cmd)
                return result.success
            except Exception as e:
                logger.error(
                    f"Failed to execute install command for {package_name}: {e}"
                )
                raise InstallationError(
                    component=package_name,
                    operation="execute_install",
                    reason=f"Failed to execute install command: {e}",
                    details=f"Command: {' '.join(cmd)}",
                ) from e

        except (InstallationError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _install_package_via_manager: {e}")
            raise InstallationError(
                component=package_name,
                operation="install_via_manager",
                reason=f"Failed to install package via manager: {e}",
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
                raise ValidationError(
                    component="search_package_via_manager",
                    validation_type="input_validation",
                    reason="Manager name and package name must not be empty",
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
                return run_command(search_commands[manager_name])
            except Exception as e:
                logger.error(
                    f"Failed to execute search command for {package_name}: {e}"
                )
                raise PackageManagerError(
                    manager_name=manager_name,
                    operation="execute_search",
                    reason=f"Failed to execute search command: {e}",
                    details=f"Command: {' '.join(search_commands[manager_name])}",
                ) from e

        except (PackageManagerError, ValidationError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _search_package_via_manager: {e}")
            raise PackageManagerError(
                manager_name=manager_name,
                operation="search_via_manager",
                reason=f"Failed to search package via manager: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e


# GLOBAL INSTANCE
########################################################

package_manager = PackageManager()
