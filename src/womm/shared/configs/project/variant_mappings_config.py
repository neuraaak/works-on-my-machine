#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# VARIANT MAPPINGS CONFIG - Project Variant Mappings
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Configuration for project variant mappings.

This config class exposes variant-to-assets mappings and supported variants
used by project creation utilities and services.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from typing import ClassVar

# ///////////////////////////////////////////////////////////////
# CLASS DEFINITION
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class VariantMappingsConfig:
    """Project variant mappings configuration (static, read-only).

    Contains supported variants per language, assets directory mappings,
    and default variant selections.
    """

    # ///////////////////////////////////////////////////////////
    # SUPPORTED VARIANTS PER LANGUAGE
    # ///////////////////////////////////////////////////////////

    SUPPORTED_VARIANTS: ClassVar[dict[str, list[str]]] = {
        "javascript": ["js", "ts", "react", "vue", "react-ts", "vue-ts"],
        "python": ["py", "django"],
    }

    # ///////////////////////////////////////////////////////////
    # VARIANT TO ASSETS DIRECTORY MAPPING
    # ///////////////////////////////////////////////////////////

    VARIANT_TO_ASSETS: ClassVar[dict[str, str]] = {
        # JavaScript variants
        "js": "js",
        "ts": "ts",
        "react": "react",
        "vue": "vue",
        "react-ts": "react-ts",
        "vue-ts": "vue-ts",
        # Python variants
        "py": "py",
        "django": "django",
    }

    # ///////////////////////////////////////////////////////////
    # DEFAULT VARIANTS PER LANGUAGE
    # ///////////////////////////////////////////////////////////

    DEFAULT_VARIANTS: ClassVar[dict[str, str]] = {
        "javascript": "js",
        "python": "py",
    }

    # ///////////////////////////////////////////////////////////
    # VARIANT DETECTION INDICATORS
    # ///////////////////////////////////////////////////////////

    # JavaScript variant detection rules (files/dependencies to look for)
    JS_VARIANT_INDICATORS: ClassVar[dict[str, list[str]]] = {
        "ts": ["tsconfig.json"],
        "react": ["react", "react-dom"],
        "vue": ["vue"],
        "react-ts": ["react", "react-dom", "tsconfig.json"],
        "vue-ts": ["vue", "tsconfig.json"],
    }

    # Python variant detection rules
    PY_VARIANT_INDICATORS: ClassVar[dict[str, list[str]]] = {
        "django": ["manage.py", "django"],
    }

    # ///////////////////////////////////////////////////////////
    # HELPER METHODS
    # ///////////////////////////////////////////////////////////

    @classmethod
    def get_assets_path(cls, language: str, variant: str) -> str:
        """Get the assets subdirectory path for a variant.

        Args:
            language: Project language (javascript, python)
            variant: Project variant (js, ts, react, etc.)

        Returns:
            str: Assets subdirectory path (e.g., "javascript/js")

        Raises:
            ValueError: If variant is not supported for the language
        """
        if language not in cls.SUPPORTED_VARIANTS:
            raise ValueError(f"Unsupported language: {language}")

        if variant not in cls.SUPPORTED_VARIANTS[language]:
            raise ValueError(
                f"Variant '{variant}' not supported for language '{language}'"
            )

        assets_subdir = cls.VARIANT_TO_ASSETS.get(variant, variant)
        return f"{language}/{assets_subdir}"

    @classmethod
    def validate_variant(cls, language: str, variant: str) -> bool:
        """Validate that a variant is supported for a language.

        Args:
            language: Project language
            variant: Project variant

        Returns:
            bool: True if variant is valid for the language
        """
        if language not in cls.SUPPORTED_VARIANTS:
            return False
        return variant in cls.SUPPORTED_VARIANTS[language]

    @classmethod
    def get_default_variant(cls, language: str) -> str | None:
        """Get the default variant for a language.

        Args:
            language: Project language

        Returns:
            Default variant or None if language not supported
        """
        return cls.DEFAULT_VARIANTS.get(language)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["VariantMappingsConfig"]
