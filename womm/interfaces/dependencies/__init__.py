#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INTERFACES DEPENDENCIES - Dependencies Interfaces
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependencies interfaces for Works On My Machine.

This package contains dependency management interfaces that orchestrate services
for runtimes, package managers, and development tools.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .deps_interface import DepsInterface
from .devtools_interface import DevToolsInterface
from .runtime_interface import RuntimeInterface
from .system_package_manager_interface import SystemPackageManagerInterface

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "DepsInterface",
    "DevToolsInterface",
    "RuntimeInterface",
    "SystemPackageManagerInterface",
]
