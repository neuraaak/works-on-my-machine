#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT CONFIG - Context Menu Configuration Facade
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Facade configuration for context menu operations.

This module re-exports context configuration from specialized modules
for backward compatibility. New code should import directly from:
- context_paths_config.py - Registry paths and command parameters
- context_limits_config.py - Validation limits, patterns, extensions
- context_file_types_config.py - File type extension mappings
- context_types_config.py - Context type constants
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import re
from dataclasses import dataclass
from typing import ClassVar

# Local imports - Re-export for backward compatibility
from .context_file_types_config import ContextFileTypesConfig
from .context_limits_config import ContextLimitsConfig
from .context_paths_config import ContextPathsConfig

# ///////////////////////////////////////////////////////////////
# FACADE CLASS DEFINITION
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class ContextConfig:
    """Context menu configuration facade (backward compatibility).

    This class aggregates context configuration from specialized modules.
    For new code, prefer importing directly from:
    - ContextPathsConfig: Registry paths, command parameters
    - ContextLimitsConfig: Validation limits, patterns, extensions
    - ContextFileTypesConfig: File type extension mappings
    """

    # ///////////////////////////////////////////////////////////
    # REGISTRY PATTERNS (from ContextLimitsConfig)
    # ///////////////////////////////////////////////////////////

    REGISTRY_KEY_PATTERN: ClassVar[re.Pattern[str]] = (
        ContextLimitsConfig.REGISTRY_KEY_PATTERN
    )

    # ///////////////////////////////////////////////////////////
    # VALID EXTENSIONS (from ContextLimitsConfig)
    # ///////////////////////////////////////////////////////////

    VALID_SCRIPT_EXTENSIONS: ClassVar[set[str]] = (
        ContextLimitsConfig.VALID_SCRIPT_EXTENSIONS
    )
    VALID_ICON_EXTENSIONS: ClassVar[set[str]] = (
        ContextLimitsConfig.VALID_ICON_EXTENSIONS
    )

    # ///////////////////////////////////////////////////////////
    # MAXIMUM LENGTHS (from ContextLimitsConfig)
    # ///////////////////////////////////////////////////////////

    MAX_LABEL_LENGTH: ClassVar[int] = ContextLimitsConfig.MAX_LABEL_LENGTH
    MAX_REGISTRY_KEY_LENGTH: ClassVar[int] = ContextLimitsConfig.MAX_REGISTRY_KEY_LENGTH
    MAX_PATH_LENGTH: ClassVar[int] = ContextLimitsConfig.MAX_PATH_LENGTH
    MAX_ICON_FILE_SIZE: ClassVar[int] = ContextLimitsConfig.MAX_ICON_FILE_SIZE

    # ///////////////////////////////////////////////////////////
    # REGISTRY PATHS (from ContextPathsConfig)
    # ///////////////////////////////////////////////////////////

    CONTEXT_PATHS: ClassVar[dict[str, str]] = ContextPathsConfig.CONTEXT_PATHS
    REGISTRY_PATHS_BY_TYPE: ClassVar[dict[str, str]] = (
        ContextPathsConfig.REGISTRY_PATHS_BY_TYPE
    )
    COMMAND_PARAMETERS: ClassVar[dict[str, str]] = ContextPathsConfig.COMMAND_PARAMETERS

    # ///////////////////////////////////////////////////////////
    # FILE TYPE EXTENSIONS (from ContextFileTypesConfig)
    # ///////////////////////////////////////////////////////////

    FILE_TYPE_EXTENSIONS: ClassVar[dict[str, set[str]]] = (
        ContextFileTypesConfig.FILE_TYPE_EXTENSIONS
    )

    # ///////////////////////////////////////////////////////////
    # RESERVED NAMES (from ContextLimitsConfig)
    # ///////////////////////////////////////////////////////////

    RESERVED_REGISTRY_NAMES: ClassVar[set[str]] = (
        ContextLimitsConfig.RESERVED_REGISTRY_NAMES
    )

    # ///////////////////////////////////////////////////////////
    # INVALID CHARACTERS (from ContextLimitsConfig)
    # ///////////////////////////////////////////////////////////

    INVALID_LABEL_CHARS: ClassVar[list[str]] = ContextLimitsConfig.INVALID_LABEL_CHARS

    # ///////////////////////////////////////////////////////////
    # SPECIAL ICON VALUES (from ContextLimitsConfig)
    # ///////////////////////////////////////////////////////////

    SPECIAL_ICON_VALUES: ClassVar[set[str]] = ContextLimitsConfig.SPECIAL_ICON_VALUES


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ContextConfig",
    "ContextFileTypesConfig",
    "ContextLimitsConfig",
    "ContextPathsConfig",
]
