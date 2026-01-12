#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONFIGS - Configuration Modules
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Configuration modules for Works On My Machine.

This package contains configuration classes organized by domain:
- dependencies: Package managers, runtimes, and dev tools
- project: Project structure, types, and variants
- system: System detection and environment
- context: Context menu configuration
- lint: Linting configuration
- security: Security patterns
- scanner: File scanner configuration
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .context import ContextConfig
from .dependencies import DevToolsConfig, RuntimeConfig, SystemPackageManagerConfig
from .lint import PythonLintingConfig
from .project import (
    JavaScriptProjectConfig,
    ProjectConfig,
    ProjectStructureConfig,
    ProjectVariantConfig,
    PythonProjectConfig,
)
from .security import FileScannerConfig, SecurityPatternsConfig
from .system import PackageManagerConfig, SystemDetectorConfig, SystemEnvironmentConfig
from .womm_setup.womm_deployment_config import WOMMDeploymentConfig

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ContextConfig",
    "DevToolsConfig",
    "FileScannerConfig",
    "JavaScriptProjectConfig",
    "PackageManagerConfig",
    "ProjectConfig",
    "ProjectStructureConfig",
    "ProjectVariantConfig",
    "PythonLintingConfig",
    "PythonProjectConfig",
    "RuntimeConfig",
    "SecurityPatternsConfig",
    "SystemDetectorConfig",
    "SystemEnvironmentConfig",
    "SystemPackageManagerConfig",
    "WOMMDeploymentConfig",
]
