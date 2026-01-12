#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PACKAGE MANAGER SERVICE - Package Manager Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Package Manager Service - Singleton service for package manager operations.

Handles package manager detection, availability checking, and package installation
across different platforms and package managers.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import platform
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.dependencies import SystemPkgManagerServiceError
from ...shared.configs.dependencies import SystemPackageManagerConfig
from ...shared.results import (
    PackageManagerAvailabilityResult,
    PackageManagerPlatformResult,
)
from ..common.command_runner_service import CommandRunnerService

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# PACKAGE MANAGER SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class SystemPackageManagerService:
    """Singleton service for package manager operations."""

    _instance: ClassVar[SystemPackageManagerService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> SystemPackageManagerService:
        """Create or return the singleton instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize package manager service (only once)."""
        if SystemPackageManagerService._initialized:
            return

        try:
            self.system = platform.system().lower()
            self.cache: dict[str, tuple[bool, str | None]] = {}
            self._command_runner = CommandRunnerService()
            SystemPackageManagerService._initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize PackageManagerService: {e}")
            raise SystemPkgManagerServiceError(
                manager_name="package_manager",
                operation="initialization",
                reason=f"Failed to initialize package manager service: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def check_manager_availability(
        self, manager_name: str
    ) -> PackageManagerAvailabilityResult:
        """
        Check if a package manager is available and return version.

        Args:
            manager_name: Name of the package manager to check

        Returns:
            PackageManagerAvailabilityResult: Result with availability and version

        Raises:
            PackageManagerError: If availability check fails
            ValidationError: If validation fails
        """
        try:
            # Input validation
            if not manager_name:
                raise ValidationServiceError(
                    component="check_manager_availability",
                    validation_type="input_validation",
                    reason="Manager name must not be empty",
                    details="Manager name parameter must be a non-empty string",
                )

            # Check cache first
            if manager_name in self.cache:
                available, version = self.cache[manager_name]
                return PackageManagerAvailabilityResult(
                    success=True,
                    message=f"Manager {manager_name} availability checked",
                    manager_name=manager_name,
                    is_available=available,
                    version=version or "",
                )

            # Get the actual command to check (e.g., "choco" for chocolatey)
            config = SystemPackageManagerConfig.SYSTEM_PACKAGE_MANAGERS.get(
                manager_name
            )
            if not config:
                self.cache[manager_name] = (False, None)
                return PackageManagerAvailabilityResult(
                    success=True,
                    message=f"Manager {manager_name} not found in configuration",
                    manager_name=manager_name,
                    is_available=False,
                    version="",
                )

            command = config.get("command", manager_name)

            try:
                availability_result = self._command_runner.check_command_available(
                    command
                )
                if not availability_result.is_available:
                    self.cache[manager_name] = (False, None)
                    return PackageManagerAvailabilityResult(
                        success=True,
                        message=f"Manager {manager_name} is not available",
                        manager_name=manager_name,
                        is_available=False,
                        version="",
                    )
            except Exception as e:
                logger.warning(
                    f"Failed to check tool availability for {manager_name}: {e}"
                )
                self.cache[manager_name] = (False, None)
                return PackageManagerAvailabilityResult(
                    success=False,
                    error=str(e),
                    manager_name=manager_name,
                    is_available=False,
                    version="",
                )

            # Try to get version using the command
            version = None
            try:
                # Get version flag from config, default to --version
                version_flag = config.get("version_flag", "--version")
                # Use subprocess directly with shell=True for Windows scripts (.ps1)
                import subprocess

                # nosec B602: shell=True is safe here - command and version_flag
                # are from internal config, not user input
                result = subprocess.run(  # noqa: S602
                    f"{command} {version_flag}",
                    capture_output=True,
                    text=True,
                    shell=True,  # nosec B602
                    timeout=10,
                    check=False,  # We handle errors ourselves
                )

                # Check if command succeeded (returncode == 0)
                if result.returncode == 0 and result.stdout:
                    stdout = result.stdout.strip()
                    if stdout:
                        # Try to extract version number from output
                        # Some managers output just the version, others include the name
                        import re

                        # Search across all lines for version patterns
                        # Pattern 1: tag: vX.Y.Z (scoop style)
                        tag_match = re.search(r"tag:\s*v?(\d+\.\d+(?:\.\d+)?)", stdout)
                        if tag_match:
                            version = tag_match.group(1)
                            logger.debug(
                                f"Parsed version {version} for {manager_name} from tag"
                            )
                        else:
                            # Pattern 2: standard version pattern (X.Y.Z)
                            version_match = re.search(r"v?(\d+\.\d+(?:\.\d+)?)", stdout)
                            if version_match:
                                version = version_match.group(1)
                            else:
                                # Fallback: use first word of first line
                                lines = stdout.split("\n")
                                first_line = lines[0].strip()
                                words = first_line.split()
                                if words:
                                    version = words[0]

                            logger.debug(f"Parsed version {version} for {manager_name}")
            except Exception as e:
                logger.debug(f"Failed to get version for {manager_name}: {e}")
                # Continue execution as version check failure is not critical

            # Command is available if check_command_available confirmed it's in PATH
            # Version is just additional information, not required for availability
            available = True
            self.cache[manager_name] = (available, version)
            return PackageManagerAvailabilityResult(
                success=True,
                message=f"Manager {manager_name} is available",
                manager_name=manager_name,
                is_available=available,
                version=version if version else "unknown",
            )

        except ValidationServiceError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in check_manager_availability: {e}")
            return PackageManagerAvailabilityResult(
                success=False,
                error=str(e),
                manager_name=manager_name,
                is_available=False,
                version="",
            )

    def is_manager_for_current_platform(
        self, manager_name: str
    ) -> PackageManagerPlatformResult:
        """
        Check if a package manager is for the current platform.

        Args:
            manager_name: Name of the package manager

        Returns:
            PackageManagerPlatformResult: Result with platform compatibility
        """
        try:
            # Input validation
            if not manager_name:
                raise ValidationServiceError(
                    component="is_manager_for_current_platform",
                    validation_type="input_validation",
                    reason="Manager name must not be empty",
                    details="Manager name parameter must be a non-empty string",
                )

            if manager_name not in SystemPackageManagerConfig.SYSTEM_PACKAGE_MANAGERS:
                return PackageManagerPlatformResult(
                    success=False,
                    message=f"Manager {manager_name} not found in configuration",
                    manager_name=manager_name,
                    is_for_current_platform=False,
                    current_platform=self.system,
                )

            config = SystemPackageManagerConfig.SYSTEM_PACKAGE_MANAGERS[manager_name]
            manager_platform = config.get("platform", "").lower()

            platform_map = {
                "windows": "windows",
                "darwin": "darwin",
                "linux": "linux",
            }

            expected_system = platform_map.get(manager_platform)
            is_for_platform = (
                expected_system is not None and self.system == expected_system
            )

            return PackageManagerPlatformResult(
                success=True,
                message=f"Platform compatibility checked for {manager_name}",
                manager_name=manager_name,
                is_for_current_platform=is_for_platform,
                current_platform=self.system,
            )

        except ValidationServiceError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in is_manager_for_current_platform: {e}")
            return PackageManagerPlatformResult(
                success=False,
                error=str(e),
                manager_name=manager_name,
                is_for_current_platform=False,
                current_platform=self.system,
            )

    def get_manager_config(self, manager_name: str) -> dict[str, str | int] | None:
        """
        Get configuration for a package manager.

        Args:
            manager_name: Name of the package manager

        Returns:
            dict | None: Manager configuration or None if not found
        """
        return SystemPackageManagerConfig.SYSTEM_PACKAGE_MANAGERS.get(manager_name)

    def get_available_managers_for_platform(self) -> list[str]:
        """
        Get list of package managers available for current platform.

        Returns:
            list[str]: List of manager names

        Raises:
            PackageManagerError: If retrieval fails
        """
        try:
            available_managers = []
            for name in SystemPackageManagerConfig.SYSTEM_PACKAGE_MANAGERS:
                result = self.is_manager_for_current_platform(name)
                if result.success and result.is_for_current_platform:
                    available_managers.append(name)
            return available_managers

        except ValidationServiceError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(
                f"Unexpected error in get_available_managers_for_platform: {e}"
            )
            raise SystemPkgManagerServiceError(
                manager_name="all_managers",
                operation="get_available_managers_for_platform",
                reason=f"Failed to retrieve available managers: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def install_package(
        self, manager_name: str, package_name: str, package_id: str | None = None
    ) -> bool:
        """
        Install a package using the specified system package manager.

        Args:
            manager_name: Name of the package manager to use (winget, choco, brew, etc.)
            package_name: Display name of the package
            package_id: Package identifier (if different from display name)

        Returns:
            bool: True if installation succeeded, False otherwise

        Raises:
            ValidationServiceError: If validation fails
            PackageManagerServiceError: If installation fails
        """
        try:
            # Input validation
            if not manager_name:
                raise ValidationServiceError(
                    component="install_package",
                    validation_type="input_validation",
                    reason="Manager name must not be empty",
                    details="manager_name parameter must be a non-empty string",
                )

            if not package_name:
                raise ValidationServiceError(
                    component="install_package",
                    validation_type="input_validation",
                    reason="Package name must not be empty",
                    details="package_name parameter must be a non-empty string",
                )

            # Check if manager is available
            availability_result = self.check_manager_availability(manager_name)
            if not availability_result.is_available:
                raise SystemPkgManagerServiceError(
                    manager_name=manager_name,
                    operation="install_package",
                    reason=f"Package manager {manager_name} is not available",
                    details="Manager must be installed before installing packages",
                )

            # Get install command from config
            install_cmd = SystemPackageManagerConfig.get_install_command(
                manager_name, package_id or package_name
            )

            if not install_cmd:
                raise SystemPkgManagerServiceError(
                    manager_name=manager_name,
                    operation="install_package",
                    reason=f"No install command configured for {manager_name}",
                    details=f"Package: {package_name}",
                )

            logger.info(
                f"Installing {package_name} using {manager_name}: {' '.join(install_cmd)}"
            )

            # Execute installation command
            result = self._command_runner.run_command(install_cmd)

            if result.returncode == 0:
                logger.info(f"Successfully installed {package_name}")
                return True
            else:
                logger.error(
                    f"Failed to install {package_name}: {result.stderr or result.stdout}"
                )
                return False

        except ValidationServiceError:
            raise
        except SystemPkgManagerServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in install_package: {e}")
            raise SystemPkgManagerServiceError(
                manager_name=manager_name,
                operation="install_package",
                reason=f"Failed to install package: {e}",
                details=f"Package: {package_name}, Exception: {type(e).__name__}",
            ) from e
