#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPS INTERFACE - Global Dependencies Orchestration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Global dependencies interface for Works On My Machine.

Provides high-level operations for checking, validating, and
displaying status across all dependency strata.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging

# Local imports
from ...shared.configs.dependencies import (
    DependenciesHierarchy,
    DevToolsConfig,
    RuntimeConfig,
)
from .devtools_interface import DevToolsInterface
from .runtime_interface import RuntimeInterface
from .system_package_manager_interface import SystemPackageManagerInterface

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)


# ///////////////////////////////////////////////////////////////
# HELPER FUNCTION
# ///////////////////////////////////////////////////////////////


def _find_tool_info(tool_name: str) -> tuple[str, str] | None:
    """
    Find the language (category) and tool_type (subcategory) for a given tool.

    Args:
        tool_name: The name of the tool to find

    Returns:
        Tuple of (language, tool_type) if found, None otherwise
    """
    for category, tools in DevToolsConfig.DEVTOOLS_DEPENDENCIES.items():
        for subcategory, tool_list in tools.items():
            if tool_name in tool_list:
                return (category, subcategory)
    return None


# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class DepsInterface:
    """Orchestrates global dependency operations across all strata."""

    def __init__(self):
        """Initialize the deps interface with lazy-loaded sub-interfaces."""
        self._system_interface: SystemPackageManagerInterface | None = None
        self._runtime_interface: RuntimeInterface | None = None
        self._tool_interface: DevToolsInterface | None = None

    # ///////////////////////////////////////////////////////////////
    # SERVICE PROPERTIES (LAZY INITIALIZATION)
    # ///////////////////////////////////////////////////////////////

    @property
    def system_interface(self) -> SystemPackageManagerInterface:
        """Lazy load SystemPackageManagerInterface when needed."""
        if self._system_interface is None:
            self._system_interface = SystemPackageManagerInterface()
        return self._system_interface

    @property
    def runtime_interface(self) -> RuntimeInterface:
        """Lazy load RuntimeInterface when needed."""
        if self._runtime_interface is None:
            self._runtime_interface = RuntimeInterface()
        return self._runtime_interface

    @property
    def tool_interface(self) -> DevToolsInterface:
        """Lazy load DevToolsInterface when needed."""
        if self._tool_interface is None:
            self._tool_interface = DevToolsInterface()
        return self._tool_interface

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def check_all(self, verbose: bool = False) -> dict:
        """
        Check all dependencies across all strata and display results.

        Args:
            verbose: Whether to show detailed information

        Returns:
            dict: All check results organized by strata
        """
        from ...ui.system import display_deps_check_results

        # Collect all results
        system_results = self.system_interface.detect_available_managers()
        runtime_results = {
            rt: self.runtime_interface.check_runtime(rt)
            for rt in RuntimeConfig.RUNTIMES
        }

        # Tool results
        tool_results = {}
        for category, tools in DevToolsConfig.DEVTOOLS_DEPENDENCIES.items():
            for subcategory, tool_list in tools.items():
                for tool in tool_list:
                    result = self.tool_interface.check_dev_tool(
                        category, subcategory, tool
                    )
                    tool_results[tool] = result

        # Display results
        display_deps_check_results(
            system_results, runtime_results, tool_results, verbose
        )

        return {
            "system": system_results,
            "runtime": runtime_results,
            "tools": tool_results,
        }

    def show_status(self, verbose: bool = False) -> dict:
        """
        Show comprehensive dependency status and display table.

        Args:
            verbose: Whether to show additional details

        Returns:
            dict: Status data for all strata
        """
        from ...ui.system import display_deps_status_table

        # Collect data
        system_status = self.system_interface.get_installation_status()
        runtime_results = {
            rt: self.runtime_interface.check_runtime(rt)
            for rt in RuntimeConfig.RUNTIMES
        }

        sample_tools = ["cspell", "ruff", "pytest", "eslint"]
        tool_results = {}
        for tool in sample_tools:
            try:
                tool_info = _find_tool_info(tool)
                if tool_info:
                    language, tool_type = tool_info
                    result = self.tool_interface.check_dev_tool(
                        language, tool_type, tool
                    )
                    tool_results[tool] = result
            except Exception as e:
                logger.debug(f"Could not check tool {tool}: {e}")

        # Display table
        display_deps_status_table(system_status, runtime_results, tool_results, verbose)

        return {
            "system": system_status,
            "runtime": runtime_results,
            "tools": tool_results,
        }

    def validate_chains(self, verbose: bool = False) -> dict:
        """
        Validate all dependency chains and display results.

        Args:
            verbose: Whether to show detailed information

        Returns:
            dict: Validation results with issues and valid count
        """
        from ...ui.system import display_deps_validation_results

        issues = []
        valid_count = 0

        # Check each devtool's chain
        for _category, tools in DevToolsConfig.DEVTOOLS_DEPENDENCIES.items():
            for _subcategory, tool_list in tools.items():
                for tool in tool_list:
                    try:
                        chain = DependenciesHierarchy.get_devtool_chain(tool)

                        if not chain.get("runtime_package_manager"):
                            issues.append(f"❌ {tool}: Missing runtime_package_manager")
                        elif not chain.get("runtime"):
                            issues.append(f"❌ {tool}: Missing runtime")
                        else:
                            valid_count += 1
                    except Exception as e:
                        issues.append(f"❌ {tool}: Invalid chain ({e})")

        # Display results
        display_deps_validation_results(issues, valid_count, verbose)

        return {
            "issues": issues,
            "valid_count": valid_count,
            "total": valid_count + len(issues),
        }


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["DepsInterface"]
