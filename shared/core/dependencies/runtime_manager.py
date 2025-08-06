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

from ..cli_manager import check_tool_available, run_command, run_silent
from ..results import BaseResult


@dataclass
class RuntimeResult(BaseResult):
    """Result of a runtime operation."""

    runtime_name: str = ""
    version: Optional[str] = None
    path: Optional[str] = None


# RUNTIME DEFINITIONS
########################################################

RUNTIMES = {
    "python": {
        "version": "3.8+",
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

SYSTEM_PACKAGE_MANAGERS = {
    "winget": {"platform": "windows", "priority": 1},
    "chocolatey": {"platform": "windows", "priority": 2},
    "scoop": {"platform": "windows", "priority": 3},
    "homebrew": {"platform": "darwin", "priority": 1},
    "apt": {"platform": "linux", "priority": 1},
    "dnf": {"platform": "linux", "priority": 2},
    "pacman": {"platform": "linux", "priority": 3},
}


# MAIN CLASS
########################################################


class RuntimeManager:
    """Manages runtime dependencies (Python, Node.js, Git)."""

    def __init__(self):
        self.system = platform.system()
        self.cache = {}

    def check_runtime(self, runtime: str) -> RuntimeResult:
        """Check if a runtime is installed."""
        if runtime not in RUNTIMES:
            return RuntimeResult(
                success=False,
                runtime_name=runtime,
                message=f"Runtime {runtime} not supported",
                error=f"Runtime {runtime} not supported",
            )

        # Check cache first
        if runtime in self.cache:
            available, version = self.cache[runtime]
            return RuntimeResult(
                success=available,
                runtime_name=runtime,
                version=version,
                path=shutil.which(runtime) if available else None,
                message=f"Runtime {runtime} {'available' if available else 'not found'}",
                error=None if available else f"Runtime {runtime} not installed",
            )

        # Check runtime
        available, version = self._check_runtime_installation(runtime)
        self.cache[runtime] = (available, version)

        return RuntimeResult(
            success=available,
            runtime_name=runtime,
            version=version,
            path=shutil.which(runtime) if available else None,
            message=f"Runtime {runtime} {'available' if available else 'not found'}",
            error=None if available else f"Runtime {runtime} not installed",
        )

    def install_runtime(self, runtime: str) -> RuntimeResult:
        """Install a runtime."""
        if runtime not in RUNTIMES:
            return RuntimeResult(
                success=False,
                runtime_name=runtime,
                message=f"Runtime {runtime} not supported",
                error=f"Runtime {runtime} not supported",
            )

        # Check if already installed
        available, version = self._check_runtime_installation(runtime)
        if available:
            return RuntimeResult(
                success=True,
                runtime_name=runtime,
                version=version,
                path=shutil.which(runtime),
                message=f"Runtime {runtime} already installed (version {version})",
            )

        # Get best package manager
        package_manager = self._get_best_package_manager()
        if not package_manager:
            return RuntimeResult(
                success=False,
                runtime_name=runtime,
                message=f"No package manager available for {runtime}",
                error="No package manager available",
            )

        # Get package name
        package_name = RUNTIMES[runtime]["package_names"].get(package_manager)
        if not package_name:
            return RuntimeResult(
                success=False,
                runtime_name=runtime,
                message=f"No package found for {runtime} in {package_manager}",
                error=f"No package found for {runtime} in {package_manager}",
            )

        # Install via package manager
        success = self._install_via_package_manager(package_manager, package_name)

        if success:
            # Re-check after installation
            available, version = self._check_runtime_installation(runtime)
            self.cache[runtime] = (available, version)

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

    def check_and_install_runtimes(
        self, runtimes: List[str]
    ) -> Dict[str, RuntimeResult]:
        """Check and install multiple runtimes."""
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
                results[runtime] = self.install_runtime(runtime)

        return results

    def get_installation_status(self, runtimes: List[str] = None) -> Dict[str, Dict]:
        """Get comprehensive installation status for runtimes."""
        if runtimes is None:
            runtimes = list(RUNTIMES.keys())

        status = {}
        for runtime in runtimes:
            available, version = self._check_runtime_installation(runtime)
            status[runtime] = {
                "installed": available,
                "version": version,
                "path": shutil.which(runtime) if available else None,
                "supported": runtime in RUNTIMES,
            }

        return status

    def _check_runtime_installation(self, runtime: str) -> Tuple[bool, Optional[str]]:
        """Check if a runtime is installed and return version."""
        if runtime == "python":
            return self._check_python()
        elif runtime == "node":
            return self._check_node()
        elif runtime == "git":
            return self._check_git()
        else:
            return False, None

    def _check_python(self) -> Tuple[bool, Optional[str]]:
        """Check Python installation."""
        python_cmds = ["python3", "python", "py"]

        for cmd in python_cmds:
            if check_tool_available(cmd):
                try:
                    result = run_silent([cmd, "--version"])
                    if result.success and result.stdout.strip():
                        version = result.stdout.strip().split()[1]
                        version_parts = [int(x) for x in version.split(".")]
                        if version_parts >= [3, 8]:
                            return True, version
                except (IndexError, ValueError):
                    continue

        return False, None

    def _check_node(self) -> Tuple[bool, Optional[str]]:
        """Check Node.js installation."""
        if check_tool_available("node"):
            try:
                result = run_silent(["node", "--version"])
                if result.success and result.stdout.strip():
                    version = result.stdout.strip().lstrip("v")
                    return True, version
            except (IndexError, ValueError) as e:
                logging.debug(f"Failed to get version for node: {e}")
                # Continue as version check failure is not critical

        return False, None

    def _check_git(self) -> Tuple[bool, Optional[str]]:
        """Check Git installation."""
        if check_tool_available("git"):
            try:
                result = run_silent(["git", "--version"])
                if result.success and result.stdout.strip():
                    version = result.stdout.strip().split()[2]
                    return True, version
            except (IndexError, ValueError) as e:
                logging.debug(f"Failed to get version for git: {e}")
                # Continue as version check failure is not critical

        return False, None

    def _get_best_package_manager(self) -> Optional[str]:
        """Get the best available package manager for the system."""
        available_managers = []

        for manager, config in SYSTEM_PACKAGE_MANAGERS.items():
            if (
                config["platform"] == self.system.lower()
                or config["platform"] == "linux"
            ) and check_tool_available(manager):
                available_managers.append((manager, config["priority"]))

        if available_managers:
            # Sort by priority (lower number = higher priority)
            available_managers.sort(key=lambda x: x[1])
            return available_managers[0][0]

        return None

    def _install_via_package_manager(
        self, package_manager: str, package_name: str
    ) -> bool:
        """Install a package via package manager."""
        if package_manager == "winget":
            cmd = ["winget", "install", package_name, "--accept-source-agreements"]
        elif package_manager == "chocolatey":
            cmd = ["choco", "install", package_name, "-y"]
        elif package_manager == "homebrew":
            cmd = ["brew", "install", package_name]
        elif package_manager == "apt":
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
        elif package_manager == "dnf":
            cmd = ["sudo", "dnf", "install", "-y", package_name]
        elif package_manager == "pacman":
            cmd = ["sudo", "pacman", "-S", "--noconfirm", package_name]
        else:
            return False

        result = run_command(cmd)
        if result.success:
            # Clear cache for this runtime
            self.cache.clear()

        return result.success


# GLOBAL INSTANCE
########################################################

runtime_manager = RuntimeManager()
