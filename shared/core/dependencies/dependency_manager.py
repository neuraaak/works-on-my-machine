#!/usr/bin/env python3
"""
Unified Dependency Manager for Works On My Machine.
Coordinates the three specialized managers: Runtime, Package, and DevTools.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from ..results import BaseResult
from .dev_tools_manager import (
    DevToolResult,
    check_and_install_dev_tools,
    check_dev_tool,
    install_dev_tool,
)
from .package_manager import (
    PackageManagerResult,
    check_package_manager,
    get_best_available_manager,
)
from .runtime_manager import (
    RuntimeResult,
    runtime_manager,
)


@dataclass
class DependencyResult(BaseResult):
    """Result of a dependency operation."""

    dependency_type: str = ""
    dependency_name: str = ""
    version: Optional[str] = None
    path: Optional[str] = None


@dataclass
class InstallationResult(BaseResult):
    """Result of an installation operation."""

    installed: List[str] = None
    skipped: List[str] = None
    failed: List[str] = None


# MAIN CLASS
########################################################


class DependencyManager:
    """Unified dependency manager that coordinates specialized managers."""

    def __init__(self):
        """Initialize the dependency manager."""

    def check_runtime(self, runtime: str) -> RuntimeResult:
        """Check if a runtime is installed."""
        return runtime_manager.check_runtime(runtime)

    def install_runtime(self, runtime: str) -> RuntimeResult:
        """Install a runtime."""
        return runtime_manager.install_runtime(runtime)

    def check_package_manager(self, manager_name: str) -> PackageManagerResult:
        """Check if a package manager is available."""
        return check_package_manager(manager_name)

    def get_best_package_manager(self) -> Optional[str]:
        """Get the best available package manager for the current system."""
        return get_best_available_manager()

    def check_dev_tool(self, language: str, tool_type: str, tool: str) -> DevToolResult:
        """Check if a development tool is installed."""
        return check_dev_tool(language, tool_type, tool)

    def install_dev_tool(
        self, language: str, tool_type: str, tool: str
    ) -> DevToolResult:
        """Install a development tool."""
        return install_dev_tool(language, tool_type, tool)

    def check_and_install_runtimes(
        self, runtimes: List[str]
    ) -> Dict[str, RuntimeResult]:
        """Check and install multiple runtimes."""
        return runtime_manager.check_and_install_runtimes(runtimes)

    def check_and_install_dev_tools(self, language: str) -> Dict[str, DevToolResult]:
        """Check and install all dev tools for a language."""
        return check_and_install_dev_tools(language)

    def get_installation_status(
        self, runtimes: List[str] = None, languages: List[str] = None
    ) -> Dict:
        """Get comprehensive installation status."""
        from .runtime_manager import runtime_manager
        from .dev_tools_manager import get_dev_tools_status
        from .package_manager import get_package_manager_status

        status = {
            "runtimes": runtime_manager.get_installation_status(runtimes),
            "package_managers": get_package_manager_status(),
            "dev_tools": {},
        }

        # Get dev tools status for specified languages
        if languages:
            for language in languages:
                status["dev_tools"][language] = get_dev_tools_status(language)
        else:
            status["dev_tools"] = get_dev_tools_status()

        return status


# GLOBAL INSTANCE
########################################################

dependency_manager = DependencyManager()


# CONVENIENCE FUNCTIONS
########################################################


def check_runtime(runtime: str) -> RuntimeResult:
    """Check if a runtime is installed."""
    from .runtime_manager import runtime_manager

    return runtime_manager.check_runtime(runtime)


def install_runtime(runtime: str) -> RuntimeResult:
    """Install a runtime."""
    from .runtime_manager import runtime_manager

    return runtime_manager.install_runtime(runtime)


def check_package_manager(manager_name: str) -> PackageManagerResult:
    """Check if a package manager is available."""
    from .package_manager import check_package_manager as _check_package_manager

    return _check_package_manager(manager_name)


def get_best_package_manager() -> Optional[str]:
    """Get the best available package manager for the current system."""
    from .package_manager import get_best_available_manager

    return get_best_available_manager()


def check_dev_tool(language: str, tool_type: str, tool: str) -> DevToolResult:
    """Check if a development tool is installed."""
    from .dev_tools_manager import check_dev_tool as _check_dev_tool

    return _check_dev_tool(language, tool_type, tool)


def install_dev_tool(language: str, tool_type: str, tool: str) -> DevToolResult:
    """Install a development tool."""
    from .dev_tools_manager import install_dev_tool as _install_dev_tool

    return _install_dev_tool(language, tool_type, tool)


def check_and_install_runtimes(runtimes: List[str]) -> Dict[str, RuntimeResult]:
    """Check and install multiple runtimes."""
    from .runtime_manager import runtime_manager

    return runtime_manager.check_and_install_runtimes(runtimes)


def check_and_install_dev_tools(language: str) -> Dict[str, DevToolResult]:
    """Check and install all dev tools for a language."""
    from .dev_tools_manager import (
        check_and_install_dev_tools as _check_and_install_dev_tools,
    )

    return _check_and_install_dev_tools(language)


def get_installation_status(
    runtimes: List[str] = None, languages: List[str] = None
) -> Dict:
    """Get comprehensive installation status."""
    return dependency_manager.get_installation_status(runtimes, languages)
