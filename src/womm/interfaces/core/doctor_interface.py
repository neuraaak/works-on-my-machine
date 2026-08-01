#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DOCTOR INTERFACE - Runtime Diagnostic Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Doctor Interface for Works On My Machine.

Gathers the read-only runtime diagnostic (channel, version, executable,
data directory, PATH registration, context menu status) into a
``DoctorResult``. This interface carries no UI: it does not print or log —
the command layer owns presentation. It never modifies user configuration.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import os
import shutil
import sys
from pathlib import Path

# Local imports
from ..._version import __version__
from ...shared.paths import womm_data_path
from ...shared.results import DoctorResult
from ...shared.runtime import get_womm_executable
from ..context import ContextMenuInterface

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class DoctorInterface:
    """Gathers the runtime diagnostic and returns a Result.

    Pure orchestration: no UI, no re-raise. Every probe is best-effort —
    an unreachable context menu registry is reported inline rather than
    failing the whole diagnostic.
    """

    def diagnose(self) -> DoctorResult:
        """
        Report the installed runtime without changing user configuration.

        Returns:
            DoctorResult: Always successful; individual probes degrade to
            an inline status string rather than failing the report.
        """
        data_dir = womm_data_path()
        channel = "standalone" if getattr(sys, "frozen", False) else "package"

        return DoctorResult(
            success=True,
            message="Runtime diagnostic completed successfully",
            channel=channel,
            version=__version__,
            executable=str(get_womm_executable()),
            data_dir=str(data_dir),
            data_dir_writable=self._is_writable(data_dir),
            path_command=shutil.which("womm"),
            context_menu_status=self._context_menu_status(),
        )

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    @staticmethod
    def _is_writable(directory: Path) -> bool:
        """Check whether ``directory`` or its closest existing parent is writable."""
        candidate = directory
        while not candidate.exists() and candidate != candidate.parent:
            candidate = candidate.parent
        return candidate.is_dir() and os.access(candidate, os.W_OK)

    @staticmethod
    def _context_menu_status() -> str:
        """Return context-menu entry counts without modifying the registry."""
        try:
            result = ContextMenuInterface().list_entries()
        except OSError as error:
            return f"unavailable ({error})"

        if not result.success:
            return f"unavailable ({result.error or 'unknown error'})"

        entries = result.entries_by_type or {}
        return (
            f"{result.total_entries} entries "
            f"(directory: {entries.get('directory', 0)}, "
            f"background: {entries.get('background', 0)})"
        )


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["DoctorInterface"]
