#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SHARED PATHS - Single Authority on Data and Asset Locations
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Path contract for Works On My Machine.

This module is the **single authority** on where things live. It keeps two
notions strictly apart, which the legacy self-installer incorrectly collapsed
into one location:

- **Data** — mutable, user-owned, always under ``~/.womm`` (overridable via
  ``$WOMM_HOME``), in every channel: dev, ``uv tool``, or standalone. This
  directory never contains code.
- **Code and assets** — immutable, shipped inside the package, read through
  :mod:`importlib.resources` so they resolve identically from a source tree,
  a wheel, or a frozen executable.

Directory accessors create their target lazily on access; file accessors
return a path and guarantee only that its parent exists.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import os
from importlib.resources import files
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from importlib.abc import Traversable

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# Environment variable overriding the data directory. Primarily an isolation
# seam for tests, which must never touch the real ``~/.womm``.
WOMM_HOME_ENV = "WOMM_HOME"

# Default data directory name, relative to the user's home.
DEFAULT_DATA_DIRNAME = ".womm"

# Sub-paths, relative to the data directory.
LOGS_DIRNAME = "logs"
TEMPLATES_DIRNAME = "templates"
BACKUPS_DIRNAME = "backups"
PATH_BACKUPS_DIRNAME = "path"
REGISTRY_BACKUPS_DIRNAME = "registry"
CONFIG_FILENAME = "config.toml"
STATE_FILENAME = "state.json"

# Package subdirectory holding the shipped, read-only assets.
ASSETS_DIRNAME = "assets"

# ///////////////////////////////////////////////////////////////
# INTERNAL HELPERS
# ///////////////////////////////////////////////////////////////


def _ensure_dir(directory: Path) -> Path:
    """Create ``directory`` (and parents) if needed and return it."""
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _data_subdir(*parts: str) -> Path:
    """Resolve and create a directory under the data directory."""
    return _ensure_dir(womm_data_dir().joinpath(*parts))


# ///////////////////////////////////////////////////////////////
# PUBLIC API - DATA LOCATIONS
# ///////////////////////////////////////////////////////////////


def womm_data_path() -> Path:
    """Resolve the WOMM data directory without creating it.

    Honors ``$WOMM_HOME`` when set to a non-blank value; otherwise defaults
    to ``~/.womm``. This path holds user data only — never code.

    Returns:
        Path: The data directory location.
    """
    override = os.environ.get(WOMM_HOME_ENV, "").strip()
    return (
        Path(override).expanduser().resolve()
        if override
        else Path.home() / DEFAULT_DATA_DIRNAME
    )


def womm_data_dir() -> Path:
    """Get the WOMM data directory, creating it if absent."""
    return _ensure_dir(womm_data_path())


def logs_dir() -> Path:
    """Get the directory holding WOMM log files."""
    return _data_subdir(LOGS_DIRNAME)


def user_templates_dir() -> Path:
    """Get the directory holding user-created project templates."""
    return _data_subdir(TEMPLATES_DIRNAME)


def path_backups_dir() -> Path:
    """Get the directory holding system ``PATH`` backups (``womm path``)."""
    return _data_subdir(BACKUPS_DIRNAME, PATH_BACKUPS_DIRNAME)


def registry_backups_dir() -> Path:
    """Get the directory holding context-menu registry backups."""
    return _data_subdir(BACKUPS_DIRNAME, REGISTRY_BACKUPS_DIRNAME)


def config_file() -> Path:
    """Get the user configuration file path (not created)."""
    return womm_data_dir() / CONFIG_FILENAME


def state_file() -> Path:
    """Get the data-state file path, used for migrations (not created)."""
    return womm_data_dir() / STATE_FILENAME


# ///////////////////////////////////////////////////////////////
# PUBLIC API - PACKAGED CODE AND ASSETS
# ///////////////////////////////////////////////////////////////


def packaged_assets() -> Traversable:
    """Get the shipped assets tree, read-only.

    Anchored on the ``womm`` package rather than on ``womm.assets``: the
    assets directory carries no ``__init__.py``, so anchoring on it directly
    would depend on namespace-package resolution. Traversing from the parent
    package works identically from a source tree, a wheel, or a frozen
    executable.

    Returns:
        Traversable: The ``assets`` directory inside the installed package.
    """
    return files("womm") / ASSETS_DIRNAME


# ///////////////////////////////////////////////////////////////
# EXPORTS
# ///////////////////////////////////////////////////////////////

__all__ = [
    "WOMM_HOME_ENV",
    "config_file",
    "logs_dir",
    "packaged_assets",
    "path_backups_dir",
    "registry_backups_dir",
    "state_file",
    "user_templates_dir",
    "womm_data_path",
    "womm_data_dir",
]
