#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT VARIANT CONFIG - Project Variant Configuration Facade
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Facade configuration for project variant detection and management.

This module re-exports variant configuration from specialized modules
for backward compatibility. New code should import directly from:
- variant_mappings_config.py - Variant mappings and validation
- variant_ui_config.py - UI descriptions and choices

Detection logic is in:
- womm.utils.project.variant_detection_utils - Auto-detection
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

# Local imports - Re-export for backward compatibility
from .variant_mappings_config import VariantMappingsConfig
from .variant_ui_config import VariantUIConfig

# ///////////////////////////////////////////////////////////////
# FACADE CLASS DEFINITION
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class ProjectVariantConfig:
    """Project variant configuration facade (backward compatibility).

    This class aggregates variant configuration from specialized modules.
    For new code, prefer importing directly from:
    - VariantMappingsConfig: Mappings, validation, defaults
    - VariantUIConfig: UI descriptions and choices
    """

    # ///////////////////////////////////////////////////////////
    # VARIANT MAPPINGS (from VariantMappingsConfig)
    # ///////////////////////////////////////////////////////////

    SUPPORTED_VARIANTS: ClassVar[dict[str, list[str]]] = (
        VariantMappingsConfig.SUPPORTED_VARIANTS
    )
    VARIANT_TO_ASSETS: ClassVar[dict[str, str]] = (
        VariantMappingsConfig.VARIANT_TO_ASSETS
    )
    DEFAULT_VARIANTS: ClassVar[dict[str, str]] = VariantMappingsConfig.DEFAULT_VARIANTS
    JS_VARIANT_INDICATORS: ClassVar[dict[str, list[str]]] = (
        VariantMappingsConfig.JS_VARIANT_INDICATORS
    )
    PY_VARIANT_INDICATORS: ClassVar[dict[str, list[str]]] = (
        VariantMappingsConfig.PY_VARIANT_INDICATORS
    )

    # ///////////////////////////////////////////////////////////
    # UI CONFIGURATION (from VariantUIConfig)
    # ///////////////////////////////////////////////////////////

    VARIANT_DESCRIPTIONS: ClassVar[dict[str, dict[str, str]]] = (
        VariantUIConfig.VARIANT_DESCRIPTIONS
    )
    JAVASCRIPT_PROJECT_TYPE_CHOICES: ClassVar[dict[str, str]] = (
        VariantUIConfig.JAVASCRIPT_PROJECT_TYPE_CHOICES
    )

    # ///////////////////////////////////////////////////////////
    # DELEGATED METHODS (for backward compatibility)
    # ///////////////////////////////////////////////////////////

    @classmethod
    def get_variants_for_ui(cls, language: str) -> list[tuple[str, str]]:
        """Get list of variants with descriptions for UI display."""
        return VariantUIConfig.get_variants_for_ui(language)

    @classmethod
    def get_javascript_project_type_choices_for_ui(cls) -> list[tuple[str, str]]:
        """Get JavaScript project type choices for wizard UI."""
        return VariantUIConfig.get_javascript_project_type_choices_for_ui()

    @staticmethod
    def get_variant_assets_path(language: str, variant: str) -> str:
        """Get the assets subdirectory path for a variant."""
        return VariantMappingsConfig.get_assets_path(language, variant)

    @staticmethod
    def validate_variant(language: str, variant: str) -> bool:
        """Validate that a variant is supported for a language."""
        return VariantMappingsConfig.validate_variant(language, variant)

    @staticmethod
    def detect_variant(
        project_path: Path, language: str, user_variant: str | None = None
    ) -> str:
        """Detect project variant automatically or use user-specified variant.

        Note: This imports from utils to avoid circular dependencies.
        """
        # Lazy import to avoid circular dependency (absolute import)
        from womm.utils.project.variant_detection_utils import VariantDetectionUtils

        return VariantDetectionUtils.detect_variant(
            project_path, language, user_variant
        )


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ProjectVariantConfig",
    "VariantMappingsConfig",
    "VariantUIConfig",
]
