#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INTERFACES - Interface Modules (Facades)
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Interface modules (Facades) for Works On My Machine.

This package contains interface modules that orchestrate services
and provide simplified APIs for the WOMM system.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports - Context interfaces
from .context import (
    ContextMenuInterface,
    ContextRegistryInterface,
    ContextScriptDetectorInterface,
)

# Local imports - Core interfaces
from .core import DoctorInterface

# Local imports - Dependencies interfaces
from .dependencies import DepsInterface

# Local imports - Lint interfaces
from .lint import PythonLintInterface

# Local imports - Project interfaces
from .project import (
    ProjectCreateInterface,
    ProjectDetectionInterface,
    ProjectManagerInterface,
    ProjectSetupInterface,
    TemplateInterface,
)

# Local imports - System interfaces
from .system import (
    SystemDetectorInterface,
    SystemEnvironmentInterface,
    SystemPathInterface,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Context interfaces
    "ContextMenuInterface",
    "ContextRegistryInterface",
    "ContextScriptDetectorInterface",
    # Core interfaces
    "DoctorInterface",
    # Dependencies interfaces
    "DepsInterface",
    # Project interfaces
    "ProjectCreateInterface",
    "ProjectDetectionInterface",
    "ProjectManagerInterface",
    "ProjectSetupInterface",
    # Lint interfaces
    "PythonLintInterface",
    # System interfaces
    "SystemDetectorInterface",
    "SystemEnvironmentInterface",
    "SystemPathInterface",
    "TemplateInterface",
]
