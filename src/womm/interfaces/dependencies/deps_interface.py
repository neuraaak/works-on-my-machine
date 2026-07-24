#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPS INTERFACE - Global Dependencies Diagnostic
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Global dependencies interface for Works On My Machine.

Provides read-only diagnostic operations across the three dependency strata
(system package managers, runtimes, dev tools). Backed by the lightweight
:func:`probe` primitive — no installation, resolution, or god-object machinery.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import sys

# Local imports
from ...shared.configs.dependencies import (
    DevToolsConfig,
    RuntimeConfig,
    SystemPackageManagerConfig,
)
from ...utils.dependencies import ProbeResult, probe

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)


# ///////////////////////////////////////////////////////////////
# HELPER FUNCTIONS
# ///////////////////////////////////////////////////////////////


def _current_platform() -> str:
    """Return the current platform key (windows, darwin, linux)."""
    if sys.platform.startswith("win"):
        return "windows"
    if sys.platform == "darwin":
        return "darwin"
    return "linux"


def _probe_managers(detect_version: bool) -> dict[str, ProbeResult]:
    """Probe the system package managers supported on the current platform."""
    platform = _current_platform()
    return {
        name: probe(str(info["command"]), detect_version=detect_version)
        for name, info in SystemPackageManagerConfig.SYSTEM_PACKAGE_MANAGERS.items()
        if info["platform"] == platform
    }


def _probe_runtimes() -> dict[str, ProbeResult]:
    """Probe every configured runtime (python, node, git)."""
    return {runtime: probe(runtime) for runtime in RuntimeConfig.RUNTIMES}


def _probe_tools() -> dict[str, ProbeResult]:
    """Probe every configured dev tool (availability only)."""
    return {
        tool: probe(tool, detect_version=False)
        for tools in DevToolsConfig.DEVTOOLS_DEPENDENCIES.values()
        for tool_list in tools.values()
        for tool in tool_list
    }


# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class DepsInterface:
    """Read-only diagnostic across all dependency strata (probe-based)."""

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def check_all(self, verbose: bool = False) -> dict:
        """
        Check availability of every dependency across all strata.

        Args:
            verbose: Whether to show per-component version details.

        Returns:
            dict: Probe results keyed by strata (``system``/``runtime``/``tools``).
        """
        from ...ui.system import display_deps_check_results

        system_results = _probe_managers(detect_version=verbose)
        runtime_results = _probe_runtimes()
        tool_results = _probe_tools()

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
        Render a comprehensive status table across all strata.

        Args:
            verbose: Whether to show additional detail columns.

        Returns:
            dict: Status data keyed by strata.
        """
        from ...ui.system import display_deps_status_table

        platform = _current_platform()
        system_status: dict[str, dict] = {}
        for name, info in SystemPackageManagerConfig.SYSTEM_PACKAGE_MANAGERS.items():
            supported = info["platform"] == platform
            result = (
                probe(str(info["command"]), detect_version=verbose)
                if supported
                else None
            )
            system_status[name] = {
                "supported_on_current_platform": supported,
                "available": bool(result and result.available),
                "version": result.version if result else None,
                "priority": info.get("priority", "N/A"),
            }

        runtime_results = _probe_runtimes()
        tool_results = _probe_tools()

        display_deps_status_table(system_status, runtime_results, tool_results, verbose)

        return {
            "system": system_status,
            "runtime": runtime_results,
            "tools": tool_results,
        }

    def list_all(self, verbose: bool = False) -> None:  # noqa: ARG002
        """
        List the dependencies WOMM knows about (static inventory, no probing).

        Args:
            verbose: Unused; kept for CLI symmetry.
        """
        from ...ui.common import ezprinter

        platform = _current_platform()

        ezprinter.info("=== System Package Managers (Strata 1) ===")
        for name, info in SystemPackageManagerConfig.SYSTEM_PACKAGE_MANAGERS.items():
            if info["platform"] == platform:
                ezprinter.info(f"  • {name} ({info['command']})")

        ezprinter.info("\n=== Runtimes (Strata 2) ===")
        for runtime, info in RuntimeConfig.RUNTIMES.items():
            ezprinter.info(f"  • {runtime} (>= {info['version']})")

        ezprinter.info("\n=== Development Tools (Strata 3) ===")
        for language, categories in DevToolsConfig.DEVTOOLS_DEPENDENCIES.items():
            for category, tools in categories.items():
                ezprinter.info(f"  • {language}/{category}: {', '.join(tools)}")


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["DepsInterface"]
