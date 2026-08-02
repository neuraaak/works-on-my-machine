#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPS INTERFACE - Global Dependencies Diagnostic
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Global dependencies interface for Works On My Machine.

Provides read-only diagnostic operations across the two dependency strata WOMM
actually depends on: runtimes (python, node, git) and runtime package managers
(pip, uv, npm, yarn). Backed by the lightweight :func:`probe` primitive — no
installation, resolution, or god-object machinery.

Deliberately out of scope: system package managers (winget, homebrew, apt) and
the packages a project chooses to use. WOMM reports; the user installs.

This interface never raises and never renders: every public method returns a
typed Result, and presentation is left to the ``ui`` layer.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging

from ...services.dependencies import ProbeResult, probe

# Local imports
from ...shared.configs.dependencies import (
    RuntimeConfig,
    RuntimePackageManagerConfig,
)
from ...shared.results import (
    DependencyCheckResult,
    DependencyInventoryEntry,
    DependencyInventoryResult,
    DependencyProbe,
    DependencyStatusResult,
)

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)


# ///////////////////////////////////////////////////////////////
# HELPER FUNCTIONS
# ///////////////////////////////////////////////////////////////


def _as_entry(name: str, result: ProbeResult) -> DependencyProbe:
    """Adapt a :class:`ProbeResult` to the transport-level record."""
    return DependencyProbe(
        name=name,
        available=result.available,
        path=result.path,
        version=result.version,
    )


def _probe_runtimes(detect_version: bool = True) -> list[DependencyProbe]:
    """Probe every configured runtime (python, node, git)."""
    return [
        _as_entry(runtime, probe(runtime, detect_version=detect_version))
        for runtime in RuntimeConfig.RUNTIMES
    ]


def _probe_package_managers(detect_version: bool = True) -> list[DependencyProbe]:
    """Probe every configured runtime package manager (pip, uv, npm, yarn)."""
    return [
        _as_entry(manager, probe(manager, detect_version=detect_version))
        for manager in RuntimePackageManagerConfig.RUNTIME_PACKAGE_MANAGERS
    ]


# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class DepsInterface:
    """Read-only diagnostic across both dependency strata (probe-based)."""

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def check_all(self, detect_versions: bool = False) -> DependencyCheckResult:
        """
        Check availability of every dependency across both strata.

        Args:
            detect_versions: Whether to resolve per-component version strings.

        Returns:
            DependencyCheckResult: Probe results per strata. Always successful —
            a missing dependency is data, not a failure of the check itself.
        """
        return DependencyCheckResult(
            success=True,
            message="Dependency check completed",
            runtime=_probe_runtimes(detect_version=detect_versions),
            package_managers=_probe_package_managers(detect_version=detect_versions),
        )

    def show_status(self, detect_versions: bool = False) -> DependencyStatusResult:
        """
        Collect a comprehensive status report across both strata.

        Args:
            detect_versions: Whether to resolve per-component version strings.

        Returns:
            DependencyStatusResult: Status data per strata.
        """
        return DependencyStatusResult(
            success=True,
            message="Dependency status collected",
            runtime=_probe_runtimes(detect_version=detect_versions),
            package_managers=_probe_package_managers(detect_version=detect_versions),
        )

    def list_all(self) -> DependencyInventoryResult:
        """
        List the dependencies WOMM knows about (static inventory, no probing).

        Returns:
            DependencyInventoryResult: Configured dependencies per strata.
        """
        runtime = [
            DependencyInventoryEntry(name=name, detail=version)
            for name, version in RuntimeConfig.RUNTIMES.items()
        ]
        package_managers = [
            DependencyInventoryEntry(name=name, detail=f"requires {runtime_name}")
            for name, runtime_name in (
                RuntimePackageManagerConfig.RUNTIME_PACKAGE_MANAGERS.items()
            )
        ]

        return DependencyInventoryResult(
            success=True,
            message="Dependency inventory collected",
            runtime=runtime,
            package_managers=package_managers,
        )


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["DepsInterface"]
