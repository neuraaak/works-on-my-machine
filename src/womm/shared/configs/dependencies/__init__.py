#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPENDENCIES CONFIGS - Dependencies Configuration Modules
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependencies configuration modules for Works On My Machine.

This package contains configuration classes for:
- Base dependencies configuration
- Package managers
- Runtime dependencies
- Development tools
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .core_config import DependenciesConfig
from .dependencies_hierarchy import DependenciesHierarchy
from .devtools_config import DevToolsConfig
from .runtime_config import RuntimeConfig
from .system_package_manager_config import SystemPackageManagerConfig

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "DependenciesConfig",
    "DependenciesHierarchy",
    "DevToolsConfig",
    "RuntimeConfig",
    "SystemPackageManagerConfig",
]
