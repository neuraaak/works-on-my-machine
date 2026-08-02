#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONFIGS - Configuration Modules
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Configuration modules for Works On My Machine.

This package contains configuration classes organized by domain:
- dependencies: Runtimes and runtime package managers
- project: Project structure, types, and variants
- system: System detection and environment
- context: Context menu configuration
- security: Security patterns
- scanner: File scanner configuration
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .context import ContextConfig
from .dependencies import RuntimeConfig, RuntimePackageManagerConfig
from .project import (
    JavaScriptProjectConfig,
    ProjectConfig,
    ProjectStructureConfig,
    ProjectVariantConfig,
    PythonProjectConfig,
)
from .security import FileScannerConfig, SecurityPatternsConfig
from .system import PackageManagerConfig, SystemDetectorConfig, SystemEnvironmentConfig

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ContextConfig",
    "FileScannerConfig",
    "JavaScriptProjectConfig",
    "PackageManagerConfig",
    "ProjectConfig",
    "ProjectStructureConfig",
    "ProjectVariantConfig",
    "PythonProjectConfig",
    "RuntimeConfig",
    "RuntimePackageManagerConfig",
    "SecurityPatternsConfig",
    "SystemDetectorConfig",
    "SystemEnvironmentConfig",
]
