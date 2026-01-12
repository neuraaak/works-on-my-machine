#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT CONFIGS - Project Configuration Modules
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project configuration modules for Works On My Machine.

This package contains configuration classes for:
- Project structure
- Project types (Python, JavaScript)
- Project variants (mappings, UI, detection)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .javascript_project_config import JavaScriptProjectConfig
from .project_config import ProjectConfig
from .project_structure_config import ProjectStructureConfig
from .project_variant_config import ProjectVariantConfig
from .python_project_config import PythonProjectConfig
from .variant_mappings_config import VariantMappingsConfig
from .variant_ui_config import VariantUIConfig

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "JavaScriptProjectConfig",
    "ProjectConfig",
    "ProjectStructureConfig",
    "ProjectVariantConfig",
    "PythonProjectConfig",
    "VariantMappingsConfig",
    "VariantUIConfig",
]
