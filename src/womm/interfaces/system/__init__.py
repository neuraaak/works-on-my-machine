#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INTERFACES SYSTEM - System Interfaces
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System interfaces for Works On My Machine.

This package contains system interface modules that orchestrate services
for system detection, PATH management, and user environment configuration.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .detector_interface import SystemDetectorInterface
from .environment_interface import SystemEnvironmentInterface
from .path_interface import SystemPathInterface

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "SystemDetectorInterface",
    "SystemEnvironmentInterface",
    "SystemPathInterface",
]
