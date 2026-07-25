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

This interface never raises and never renders: every public method returns a
typed Result, and presentation is left to the ``ui`` layer.
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
from ...shared.results import (
    DependencyCheckResult,
    DependencyInventoryEntry,
    DependencyInventoryResult,
    DependencyManagerStatus,
    DependencyProbe,
    DependencyStatusResult,
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


def _as_entry(name: str, result: ProbeResult) -> DependencyProbe:
    """Adapt a :class:`ProbeResult` to the transport-level record."""
    return DependencyProbe(
        name=name,
        available=result.available,
        path=result.path,
        version=result.version,
    )


def _probe_managers(detect_version: bool) -> list[DependencyProbe]:
    """Probe the system package managers supported on the current platform."""
    platform = _current_platform()
    return [
        _as_entry(name, probe(str(info["command"]), detect_version=detect_version))
        for name, info in SystemPackageManagerConfig.SYSTEM_PACKAGE_MANAGERS.items()
        if info["platform"] == platform
    ]


def _probe_runtimes() -> list[DependencyProbe]:
    """Probe every configured runtime (python, node, git)."""
    return [_as_entry(runtime, probe(runtime)) for runtime in RuntimeConfig.RUNTIMES]


def _probe_tools() -> list[DependencyProbe]:
    """Probe every configured dev tool (availability only)."""
    return [
        _as_entry(tool, probe(tool, detect_version=False))
        for tools in DevToolsConfig.DEVTOOLS_DEPENDENCIES.values()
        for tool_list in tools.values()
        for tool in tool_list
    ]


# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class DepsInterface:
    """Read-only diagnostic across all dependency strata (probe-based)."""

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def check_all(self, detect_versions: bool = False) -> DependencyCheckResult:
        """
        Check availability of every dependency across all strata.

        Args:
            detect_versions: Whether to resolve per-component version strings.

        Returns:
            DependencyCheckResult: Probe results per strata. Always successful —
            a missing dependency is data, not a failure of the check itself.
        """
        return DependencyCheckResult(
            success=True,
            message="Dependency check completed",
            system=_probe_managers(detect_version=detect_versions),
            runtime=_probe_runtimes(),
            tools=_probe_tools(),
        )

    def show_status(self, detect_versions: bool = False) -> DependencyStatusResult:
        """
        Collect a comprehensive status report across all strata.

        Unlike :meth:`check_all`, this reports every configured package manager,
        including those unsupported on the current platform.

        Args:
            detect_versions: Whether to resolve per-component version strings.

        Returns:
            DependencyStatusResult: Status data per strata.
        """
        platform = _current_platform()
        system_status: list[DependencyManagerStatus] = []
        for name, info in SystemPackageManagerConfig.SYSTEM_PACKAGE_MANAGERS.items():
            supported = info["platform"] == platform
            result = (
                probe(str(info["command"]), detect_version=detect_versions)
                if supported
                else None
            )
            system_status.append(
                DependencyManagerStatus(
                    name=name,
                    supported_on_current_platform=supported,
                    available=bool(result and result.available),
                    version=result.version if result else None,
                    priority=str(info.get("priority", "N/A")),
                )
            )

        return DependencyStatusResult(
            success=True,
            message="Dependency status collected",
            system=system_status,
            runtime=_probe_runtimes(),
            tools=_probe_tools(),
        )

    def list_all(self) -> DependencyInventoryResult:
        """
        List the dependencies WOMM knows about (static inventory, no probing).

        Returns:
            DependencyInventoryResult: Configured dependencies per strata for the
            current platform.
        """
        platform = _current_platform()

        system = [
            DependencyInventoryEntry(name=name, detail=str(info["command"]))
            for name, info in SystemPackageManagerConfig.SYSTEM_PACKAGE_MANAGERS.items()
            if info["platform"] == platform
        ]
        runtime = [
            DependencyInventoryEntry(name=name, detail=f">= {info['version']}")
            for name, info in RuntimeConfig.RUNTIMES.items()
        ]
        tools = [
            DependencyInventoryEntry(
                name=f"{language}/{category}", detail=", ".join(tool_list)
            )
            for language, categories in DevToolsConfig.DEVTOOLS_DEPENDENCIES.items()
            for category, tool_list in categories.items()
        ]

        return DependencyInventoryResult(
            success=True,
            message="Dependency inventory collected",
            platform=platform,
            system=system,
            runtime=runtime,
            tools=tools,
        )


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["DepsInterface"]
