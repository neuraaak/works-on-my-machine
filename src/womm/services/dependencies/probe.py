#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPENDENCY PROBE - Lightweight Executable Detection
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Lightweight dependency probing for Works On My Machine.

Provides a single, read-only primitive to detect whether an executable
(system package manager, runtime, or dev tool) is available on the current
machine and, optionally, its version. Backed by the hardened
:class:`CommandRunnerService` (PATH lookup + security validation), it replaces
the former multi-strata interface/service machinery for diagnostic use.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import shutil
from dataclasses import dataclass

# Local imports
from ..common.command_runner_service import CommandRunnerService

# ///////////////////////////////////////////////////////////////
# RESULT TYPE
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class ProbeResult:
    """Outcome of probing a single executable (read-only)."""

    name: str
    available: bool
    path: str | None = None
    version: str | None = None

    @property
    def success(self) -> bool:
        """Alias for ``available`` (compat with the old *Result contract)."""
        return self.available


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////


def probe(
    executable: str,
    *,
    version_flag: str = "--version",
    detect_version: bool = True,
) -> ProbeResult:
    """Detect whether an executable is installed and optionally its version.

    Args:
        executable: Name of the executable to look up on ``PATH``.
        version_flag: Flag used to query the version (default ``--version``).
        detect_version: Whether to attempt version detection when available.

    Returns:
        ProbeResult: Availability, resolved path, and version (best effort).
    """
    runner = CommandRunnerService()

    availability = runner.check_command_available(executable)
    if not availability.is_available:
        return ProbeResult(name=executable, available=False)

    version: str | None = None
    if detect_version:
        version_result = runner.get_command_version(executable, version_flag)
        if version_result.success and version_result.version:
            version = version_result.version

    return ProbeResult(
        name=executable,
        available=True,
        path=shutil.which(executable),
        version=version,
    )


# ///////////////////////////////////////////////////////////////
# EXPORTS
# ///////////////////////////////////////////////////////////////

__all__ = ["ProbeResult", "probe"]
