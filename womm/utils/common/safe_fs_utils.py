#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SAFE FILESYSTEM UTILITIES - Protected filesystem operations
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Safe filesystem utilities for Works On My Machine.

Provides guarded wrappers around destructive filesystem operations
(e.g. shutil.rmtree) to prevent accidental deletion of critical
system paths or paths outside an expected boundary.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import platform
import shutil
from pathlib import Path

# Local imports
from ...ui.common import ezlogger

# ///////////////////////////////////////////////////////////////
# CRITICAL PATHS - Never allow deletion
# ///////////////////////////////////////////////////////////////

_CRITICAL_PATHS_UNIX: set[str] = {
    "/",
    "/bin",
    "/boot",
    "/dev",
    "/etc",
    "/home",
    "/lib",
    "/lib64",
    "/opt",
    "/proc",
    "/root",
    "/sbin",
    "/sys",
    # Protected path in delete blocklist, not a temp-file usage.
    "/tmp",  # noqa: S108
    "/usr",
    "/var",
}

_CRITICAL_PATHS_WINDOWS: set[str] = {
    "C:\\",
    "C:\\Windows",
    "C:\\Windows\\System32",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "C:\\Users",
    "C:\\ProgramData",
}


def _get_critical_paths() -> set[Path]:
    """Build the set of critical paths for the current platform."""
    raw: set[str] = set()
    if platform.system() == "Windows":
        raw = _CRITICAL_PATHS_WINDOWS
    else:
        raw = _CRITICAL_PATHS_UNIX
    # Always protect home directory root
    raw.add(str(Path.home()))
    return {Path(p).resolve() for p in raw}


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////


def safe_rmtree(path: Path, *, allowed_parent: Path) -> None:
    """Remove a directory tree with safety guards.

    Performs two safety checks before delegating to ``shutil.rmtree``:

    1. **Boundary check** -- *path* must resolve to a location **inside**
       *allowed_parent*.  This prevents path-traversal attacks where a
       crafted symbolic link or ``..`` component could escape the
       expected directory.

    2. **Critical-path check** -- *path* must not resolve to a known
       system-critical directory (``/``, ``C:\\Windows``, user home, etc.).

    Args:
        path: Directory to remove.  Resolved before any check.
        allowed_parent: The directory that must be an ancestor of *path*.
            Resolved before comparison.

    Raises:
        ValueError: If *path* falls outside *allowed_parent* or resolves
            to a critical system directory.
        FileNotFoundError: If *path* does not exist (no silent no-op).
        PermissionError: Propagated from ``shutil.rmtree``.
        OSError: Propagated from ``shutil.rmtree``.
    """
    resolved = path.resolve()
    parent_resolved = allowed_parent.resolve()

    # --- guard: path must exist ----------------------------------
    if not resolved.exists():
        raise FileNotFoundError(f"Directory does not exist: {resolved}")

    # --- guard: must be a directory ------------------------------
    if not resolved.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {resolved}")

    # --- guard: boundary check -----------------------------------
    if not resolved.is_relative_to(parent_resolved):
        raise ValueError(
            f"Refusing to delete {resolved}: outside allowed boundary {parent_resolved}"
        )

    # --- guard: critical path check ------------------------------
    critical = _get_critical_paths()
    if resolved in critical:
        raise ValueError(f"Refusing to delete critical system path: {resolved}")

    ezlogger.debug(
        "safe_rmtree: removing %s (allowed parent: %s)", resolved, parent_resolved
    )
    ezlogger.debug(
        "safe_rmtree: removing %s (allowed parent: %s)", resolved, parent_resolved
    )
    shutil.rmtree(resolved)
