#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPENDENCIES SERVICES - Dependencies Services
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependencies services for Works On My Machine.

This package contains singleton services for:
- Package manager operations
- Runtime management
- Development tools management
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .devtools_dependencies_service import DevToolsService
from .runtime_service import RuntimeService
from .system_package_manager_service import SystemPackageManagerService

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "DevToolsService",
    "RuntimeService",
    "SystemPackageManagerService",
]
