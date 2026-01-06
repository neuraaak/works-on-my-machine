#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# MANAGERS DEPENDENCIES - Dependencies Management
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependencies management for Works On My Machine.

This package contains all dependency management modules for runtimes, package managers,
and development tools. Provides unified interface for managing system dependencies.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .dev_tools_manager import dev_tools_manager
from .package_manager import package_manager
from .runtime_manager import runtime_manager

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "runtime_manager",
    "package_manager",
    "dev_tools_manager",
]
