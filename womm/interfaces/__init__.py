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
    ContextIconInterface,
    ContextMenuInterface,
    ContextRegistryInterface,
    ContextScriptDetectorInterface,
)

# Local imports - Cspell interfaces
from .cspell import CSpellCheckerInterface, CSpellDictionaryInterface

# Local imports - Dependencies interfaces
from .dependencies import (
    DepsInterface,
    DevToolsInterface,
    RuntimeInterface,
    SystemPackageManagerInterface,
)

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

# Local imports - Womm deployment interfaces
from .womm_setup import WommInstallerInterface, WommUninstallerInterface

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Cspell interfaces
    "CSpellCheckerInterface",
    "CSpellDictionaryInterface",
    # Context interfaces
    "ContextIconInterface",
    "ContextMenuInterface",
    "ContextRegistryInterface",
    "ContextScriptDetectorInterface",
    # Dependencies interfaces
    "DepsInterface",
    "DevToolsInterface",
    # Project interfaces
    "ProjectCreateInterface",
    "ProjectDetectionInterface",
    "ProjectManagerInterface",
    "ProjectSetupInterface",
    # Lint interfaces
    "PythonLintInterface",
    "RuntimeInterface",
    # System interfaces
    "SystemDetectorInterface",
    "SystemEnvironmentInterface",
    "SystemPackageManagerInterface",
    "SystemPathInterface",
    "TemplateInterface",
    # Womm deployment interfaces
    "WommInstallerInterface",
    "WommUninstallerInterface",
]
