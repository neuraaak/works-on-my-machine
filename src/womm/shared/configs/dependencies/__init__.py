#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPENDENCIES CONFIGS - Dependencies Configuration Modules
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependencies configuration modules for Works On My Machine.

This package contains configuration classes for the two strata WOMM cares
about:
- Runtimes (python, node, git)
- Runtime package managers (pip, uv, npm, yarn)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .runtime_config import RuntimeConfig
from .runtime_package_manager_config import RuntimePackageManagerConfig

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "RuntimeConfig",
    "RuntimePackageManagerConfig",
]
