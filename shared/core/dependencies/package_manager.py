#!/usr/bin/env python3
"""
Package Manager for Works On My Machine.
Manages system package managers (winget, chocolatey, homebrew, apt, etc.).
"""

import logging
import platform
from dataclasses import dataclass
from typing import Dict, Optional

from ..cli_manager import check_tool_available, run_command, run_silent
from ..results import BaseResult


@dataclass
class PackageManagerResult(BaseResult):
    """Result of a package manager operation."""

    package_manager_name: str = ""
    version: Optional[str] = None
    platform: Optional[str] = None
    priority: Optional[int] = None


# PACKAGE MANAGER DEFINITIONS
########################################################

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


# MAIN CLASS
########################################################


class PackageManager:
    """Manages system package managers."""

    def __init__(self):
        self.system = platform.system()
        self.cache = {}

    def detect_available_managers(self) -> Dict[str, PackageManagerResult]:
        """Detect all available package managers for the current system."""
        results = {}

        for manager_name, config in SYSTEM_PACKAGE_MANAGERS.items():
            if self._is_manager_for_current_platform(config):
                result = self.check_package_manager(manager_name)
                results[manager_name] = result

        return results

    def check_package_manager(self, manager_name: str) -> PackageManagerResult:
        """Check if a package manager is available."""
        if manager_name not in SYSTEM_PACKAGE_MANAGERS:
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
        available, version = self._check_manager_availability(manager_name)
        self.cache[manager_name] = (available, version)

        config = SYSTEM_PACKAGE_MANAGERS[manager_name]
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

    def get_best_available_manager(self) -> Optional[str]:
        """Get the best available package manager for the current system."""
        available_managers = []

        for manager_name, config in SYSTEM_PACKAGE_MANAGERS.items():
            if self._is_manager_for_current_platform(config):
                available, _ = self._check_manager_availability(manager_name)
                if available:
                    available_managers.append((manager_name, config["priority"]))

        if available_managers:
            # Sort by priority (lower number = higher priority)
            available_managers.sort(key=lambda x: x[1])
            return available_managers[0][0]

        return None

    def install_package(
        self, package_name: str, manager_name: str = None
    ) -> PackageManagerResult:
        """Install a package using the specified or best available package manager."""
        if manager_name is None:
            manager_name = self.get_best_available_manager()
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
        available, version = self._check_manager_availability(manager_name)
        if not available:
            return PackageManagerResult(
                success=False,
                package_manager_name=manager_name,
                message=f"Package manager {manager_name} not available",
                error=f"Package manager {manager_name} not installed",
            )

        # Install package
        success = self._install_package_via_manager(manager_name, package_name)

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

    def search_package(
        self, package_name: str, manager_name: str = None
    ) -> PackageManagerResult:
        """Search for a package using the specified or best available package manager."""
        if manager_name is None:
            manager_name = self.get_best_available_manager()
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
        available, version = self._check_manager_availability(manager_name)
        if not available:
            return PackageManagerResult(
                success=False,
                package_manager_name=manager_name,
                message=f"Package manager {manager_name} not available",
                error=f"Package manager {manager_name} not installed",
            )

        # Search package
        result = self._search_package_via_manager(manager_name, package_name)

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

    def get_installation_status(self) -> Dict[str, Dict]:
        """Get comprehensive status of all package managers."""
        status = {}

        for manager_name, config in SYSTEM_PACKAGE_MANAGERS.items():
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

        return status

    def _is_manager_for_current_platform(self, config: Dict) -> bool:
        """Check if a package manager is supported on the current platform."""
        return (
            config["platform"] == self.system.lower() or config["platform"] == "linux"
        )

    def _check_manager_availability(
        self, manager_name: str
    ) -> tuple[bool, Optional[str]]:
        """Check if a package manager is available and return version."""
        if not check_tool_available(manager_name):
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
            logging.debug(f"Failed to get version for {manager_name}: {e}")
            # Continue execution as version check failure is not critical

        return False, None

    def _install_package_via_manager(
        self, manager_name: str, package_name: str
    ) -> bool:
        """Install a package via a specific package manager."""
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

        result = run_command(cmd)
        return result.success

    def _search_package_via_manager(self, manager_name: str, package_name: str):
        """Search for a package via a specific package manager."""
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
            from ..results import BaseResult

            return BaseResult(success=False, stderr="Unsupported package manager")

        return run_command(search_commands[manager_name])


# GLOBAL INSTANCE
########################################################

# Singleton instance for global access
_package_manager_instance = None


def get_package_manager() -> PackageManager:
    """Get the global package manager instance."""
    global _package_manager_instance
    if _package_manager_instance is None:
        _package_manager_instance = PackageManager()
    return _package_manager_instance


# CONVENIENCE FUNCTIONS
########################################################

def check_package_manager(manager_name: str) -> PackageManagerResult:
    """Check if a package manager is available."""
    return get_package_manager().check_package_manager(manager_name)


def get_best_available_manager() -> str:
    """Get the best available package manager for the current system."""
    return get_package_manager().get_best_available_manager()


def get_package_manager_status() -> Dict[str, Dict]:
    """Get comprehensive status of all package managers."""
    return get_package_manager().get_installation_status()
