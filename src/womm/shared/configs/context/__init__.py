#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT CONFIGS - Context Configuration Modules
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context configuration modules for Works On My Machine.

This package contains configuration classes for:
- Context paths (registry paths, command parameters)
- Context limits (validation, extensions, patterns)
- Context file types (file type extension mappings)
- Context types (type constants)
- Script and icon configuration
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .context_config import ContextConfig
from .context_file_types_config import ContextFileTypesConfig
from .context_limits_config import ContextLimitsConfig
from .context_paths_config import ContextPathsConfig
from .context_types_config import ContextTypesConfig
from .script_config import IconConfig, ScriptConfig

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ContextConfig",
    "ContextFileTypesConfig",
    "ContextLimitsConfig",
    "ContextPathsConfig",
    "ContextTypesConfig",
    "IconConfig",
    "ScriptConfig",
]
