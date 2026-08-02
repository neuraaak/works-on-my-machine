#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# RUNTIME CONFIG - Runtime Configuration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Runtime configuration for Works On My Machine.

Defines the runtimes (Strata 1) WOMM needs in order to run project setup and
template scaffolding: Python, Node.js and Git.

WOMM never installs a runtime. It reports what is present and, when a runtime
is missing, tells the user to install it themselves. Installation mappings for
system package managers were removed on 2026-08-02: managing winget / apt /
homebrew is explicitly out of scope.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import ClassVar

# ///////////////////////////////////////////////////////////////
# RUNTIME DEFINITIONS
# ///////////////////////////////////////////////////////////////


class RuntimeConfig:
    """Configuration for runtime dependencies (Strata 1)."""

    RUNTIMES: ClassVar[dict[str, str]] = {
        "python": "3.13+",
        "node": "18+",
        "git": "2.30+",
    }


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["RuntimeConfig"]
