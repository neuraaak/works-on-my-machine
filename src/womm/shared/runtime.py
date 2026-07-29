#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SHARED RUNTIME - Executable Resolution
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""Resolve the stable command entry point used by integrations."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import shutil
import sys
from pathlib import Path


def get_womm_executable() -> Path:
    """Return the executable integrations should invoke.

    Frozen distributions expose their real executable through ``sys.executable``.
    For package installs, prefer uv's stable user shim and fall back to the
    command currently resolvable on PATH. The returned path may not exist in a
    source checkout; callers that need an executable must validate it.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable)

    executable_name = "womm.exe" if sys.platform == "win32" else "womm"
    uv_shim = Path.home() / ".local" / "bin" / executable_name
    if uv_shim.is_file():
        return uv_shim

    resolved = shutil.which("womm")
    return Path(resolved) if resolved else uv_shim


__all__ = ["get_womm_executable"]
