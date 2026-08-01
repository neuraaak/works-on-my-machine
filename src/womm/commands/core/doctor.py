#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DOCTOR - Runtime Diagnostics
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""Read-only runtime diagnostics for the WOMM CLI."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import os
import shutil
import sys
from pathlib import Path

# Third-party imports
import click

# Local imports
from ..._version import __version__
from ...interfaces import ContextMenuInterface
from ...shared.paths import womm_data_path
from ...shared.runtime import get_womm_executable

# ///////////////////////////////////////////////////////////////
# DIAGNOSTIC HELPERS
# ///////////////////////////////////////////////////////////////


def _is_writable(directory: Path) -> bool:
    """Check whether ``directory`` or its closest existing parent is writable."""
    candidate = directory
    while not candidate.exists() and candidate != candidate.parent:
        candidate = candidate.parent
    return candidate.is_dir() and os.access(candidate, os.W_OK)


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
# COMMAND
# ///////////////////////////////////////////////////////////////


@click.command("doctor")
@click.help_option("-h", "--help")
def doctor_cmd() -> None:
    """Report the installed runtime without changing user configuration."""
    data_dir = womm_data_path()
    channel = "standalone" if getattr(sys, "frozen", False) else "package"
    executable = get_womm_executable()
    path_command = shutil.which("womm")
    data_dir_status = "writable" if _is_writable(data_dir) else "not writable"

    click.echo(f"Runtime channel: {channel}")
    click.echo(f"Version: {__version__}")
    click.echo(f"Executable: {executable}")
    click.echo(f"Data directory: {data_dir} ({data_dir_status})")
    click.echo(f"PATH command: {path_command or 'not found'}")
    click.echo(f"Context menu: {_context_menu_status()}")


__all__ = ["doctor_cmd"]
