#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SERVICES SYSTEM - System Services
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System services for Works On My Machine.

This package contains services for system management operations including
system detection, PATH management, and environment operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .detector_service import SystemDetectorService
from .environment_service import SystemEnvironmentService
from .path_service import SystemPathService

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "SystemDetectorService",
    "SystemEnvironmentService",
    "SystemPathService",
]
