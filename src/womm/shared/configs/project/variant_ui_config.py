#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# VARIANT UI CONFIG - Project Variant UI Configuration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Configuration for project variant UI display.

This config class exposes variant descriptions and UI choices
used by wizard interfaces and display utilities.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from typing import ClassVar

# Local imports
from .variant_mappings_config import VariantMappingsConfig

# ///////////////////////////////////////////////////////////////
# CLASS DEFINITION
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class VariantUIConfig:
    """Project variant UI configuration (static, read-only).

    Contains variant descriptions, icons, and UI choices
    for wizard interfaces.
    """

    # ///////////////////////////////////////////////////////////
    # VARIANT DESCRIPTIONS FOR UI DISPLAY
    # ///////////////////////////////////////////////////////////

    VARIANT_DESCRIPTIONS: ClassVar[dict[str, dict[str, str]]] = {
        "javascript": {
            "js": "📦 Node.js application (JavaScript)",
            "ts": "📘 Node.js application (TypeScript)",
            "react": "⚛️ React.js application (JavaScript)",
            "vue": "💚 Vue.js application (JavaScript)",
            "react-ts": "⚛️ React.js application (TypeScript)",
            "vue-ts": "💚 Vue.js application (TypeScript)",
            "node": "📦 Node.js application (JavaScript)",  # Alias for js
        },
        "python": {
            "py": "🐍 Standard Python project",
            "django": "🌐 Django web framework project",
        },
    }

    # ///////////////////////////////////////////////////////////
    # JAVASCRIPT PROJECT TYPE CHOICES
    # ///////////////////////////////////////////////////////////

    JAVASCRIPT_PROJECT_TYPE_CHOICES: ClassVar[dict[str, str]] = {
        "node": "📦 Node.js application",
        "library": "📚 JavaScript library",
        "cli": "⚡ CLI application",
    }

    # ///////////////////////////////////////////////////////////
    # UI HELPER METHODS
    # ///////////////////////////////////////////////////////////

    @classmethod
    def get_variants_for_ui(cls, language: str) -> list[tuple[str, str]]:
        """Get list of variants with descriptions for UI display.

        Args:
            language: Project language (javascript, python)

        Returns:
            List of tuples (variant, description) ordered by SUPPORTED_VARIANTS
        """
        if language not in VariantMappingsConfig.SUPPORTED_VARIANTS:
            return []

        variants = VariantMappingsConfig.SUPPORTED_VARIANTS[language]
        descriptions = cls.VARIANT_DESCRIPTIONS.get(language, {})

        return [(variant, descriptions.get(variant, variant)) for variant in variants]

    @classmethod
    def get_javascript_project_type_choices_for_ui(cls) -> list[tuple[str, str]]:
        """Get JavaScript project type choices for wizard UI.

        Returns:
            List of tuples (type, description) for JavaScript project types
        """
        return list(cls.JAVASCRIPT_PROJECT_TYPE_CHOICES.items())

    @classmethod
    def get_variant_description(cls, language: str, variant: str) -> str:
        """Get the description for a specific variant.

        Args:
            language: Project language
            variant: Project variant

        Returns:
            Description string or variant name if not found
        """
        return cls.VARIANT_DESCRIPTIONS.get(language, {}).get(variant, variant)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["VariantUIConfig"]
