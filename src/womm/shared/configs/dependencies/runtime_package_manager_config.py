#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# RUNTIME PACKAGE MANAGER CONFIG - Runtime Package Managers
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Runtime package manager configuration for Works On My Machine.

Defines the package managers (Strata 2) that project setup and template
scaffolding rely on to install a project's own dependencies.

Scope note: only managers shipped with — or installed alongside — a runtime are
covered. System package managers (winget, chocolatey, homebrew, apt, dnf,
pacman) are out of scope, and so are the packages themselves: which linter,
formatter or test runner a project uses is the user's decision, not WOMM's.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import ClassVar

# ///////////////////////////////////////////////////////////////
# RUNTIME PACKAGE MANAGER DEFINITIONS
# ///////////////////////////////////////////////////////////////


class RuntimePackageManagerConfig:
    """Configuration for runtime package managers (Strata 2)."""

    # Manager name -> runtime it depends on (see RuntimeConfig.RUNTIMES).
    RUNTIME_PACKAGE_MANAGERS: ClassVar[dict[str, str]] = {
        "pip": "python",
        "uv": "python",
        "npm": "node",
        "yarn": "node",
    }


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["RuntimePackageManagerConfig"]
