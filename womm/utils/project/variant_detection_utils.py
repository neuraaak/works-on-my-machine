#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# VARIANT DETECTION UTILS - Project Variant Detection
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Utility functions for automatic project variant detection.

This module provides detection logic for:
- JavaScript variants (js, ts, react, vue, react-ts, vue-ts)
- Python variants (py, django)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
from pathlib import Path

# Local imports
from ...shared.configs.project import VariantMappingsConfig

# ///////////////////////////////////////////////////////////////
# VARIANT DETECTION CLASS
# ///////////////////////////////////////////////////////////////


class VariantDetectionUtils:
    """Utility class for automatic project variant detection."""

    # ///////////////////////////////////////////////////////////
    # MAIN DETECTION METHOD
    # ///////////////////////////////////////////////////////////

    @staticmethod
    def detect_variant(
        project_path: Path, language: str, user_variant: str | None = None
    ) -> str:
        """Detect project variant automatically or use user-specified variant.

        Args:
            project_path: Path to the project directory
            language: Project language (javascript, python)
            user_variant: User-specified variant (overrides auto-detection)

        Returns:
            str: Detected or specified variant

        Raises:
            ValueError: If language is not supported or variant is invalid
        """
        # If user specified a variant, validate and use it
        if user_variant:
            if language not in VariantMappingsConfig.SUPPORTED_VARIANTS:
                raise ValueError(f"Unsupported language: {language}")

            if user_variant not in VariantMappingsConfig.SUPPORTED_VARIANTS[language]:
                supported = ", ".join(
                    VariantMappingsConfig.SUPPORTED_VARIANTS[language]
                )
                raise ValueError(
                    f"Variant '{user_variant}' not supported for language '{language}'. "
                    f"Supported variants: {supported}"
                )
            return user_variant

        # Auto-detect variant
        if language == "javascript":
            return VariantDetectionUtils._detect_javascript_variant(project_path)
        elif language == "python":
            return VariantDetectionUtils._detect_python_variant(project_path)
        else:
            raise ValueError(f"Auto-detection not supported for language: {language}")

    # ///////////////////////////////////////////////////////////
    # JAVASCRIPT DETECTION
    # ///////////////////////////////////////////////////////////

    @staticmethod
    def _detect_javascript_variant(project_path: Path) -> str:
        """Detect JavaScript project variant.

        Args:
            project_path: Path to the project directory

        Returns:
            str: Detected variant (js, ts, react, vue, react-ts, vue-ts)
        """
        default = VariantMappingsConfig.DEFAULT_VARIANTS["javascript"]

        # Check for package.json
        package_json_path = project_path / "package.json"
        if not package_json_path.exists():
            return default

        try:
            with open(package_json_path, encoding="utf-8") as f:
                package_data = json.load(f)
        except (json.JSONDecodeError, OSError):
            return default

        # Check for TypeScript
        has_tsconfig = (project_path / "tsconfig.json").exists()
        dependencies = package_data.get("dependencies", {})
        dev_dependencies = package_data.get("devDependencies", {})

        all_deps = {**dependencies, **dev_dependencies}

        # Check for React
        has_react = any(
            dep.startswith("react") for dep in all_deps if isinstance(dep, str)
        )

        # Check for Vue
        has_vue = "vue" in all_deps

        # Determine variant based on combinations
        if has_react and has_tsconfig:
            return "react-ts"
        elif has_vue and has_tsconfig:
            return "vue-ts"
        elif has_react:
            return "react"
        elif has_vue:
            return "vue"
        elif has_tsconfig:
            return "ts"
        else:
            return "js"

    # ///////////////////////////////////////////////////////////
    # PYTHON DETECTION
    # ///////////////////////////////////////////////////////////

    @staticmethod
    def _detect_python_variant(project_path: Path) -> str:
        """Detect Python project variant.

        Args:
            project_path: Path to the project directory

        Returns:
            str: Detected variant (py, django)
        """
        default = VariantMappingsConfig.DEFAULT_VARIANTS["python"]

        # Check for Django-specific files
        if (project_path / "manage.py").exists():
            return "django"

        # Check pyproject.toml for Django dependency
        pyproject_path = project_path / "pyproject.toml"
        if pyproject_path.exists() and VariantDetectionUtils._check_django_in_pyproject(
            pyproject_path
        ):
            return "django"

        # Check requirements.txt
        requirements_path = project_path / "requirements.txt"
        if requirements_path.exists():
            try:
                with open(requirements_path, encoding="utf-8") as f:
                    content = f.read().lower()
                    if "django" in content:
                        return "django"
            except OSError:
                pass

        return default

    @staticmethod
    def _check_django_in_pyproject(pyproject_path: Path) -> bool:
        """Check if Django is listed in pyproject.toml dependencies.

        Args:
            pyproject_path: Path to pyproject.toml

        Returns:
            bool: True if Django is found in dependencies
        """
        try:
            # Try tomllib first (Python 3.11+ stdlib)
            try:
                import tomllib  # Python 3.11+ stdlib
            except ImportError:
                # Fallback to tomli for older Python versions
                try:
                    import tomli as tomllib  # type: ignore[import-untyped]
                except ImportError:
                    # Final fallback: simple string search
                    with open(pyproject_path, encoding="utf-8") as f:
                        content = f.read().lower()
                        return "django" in content

            with open(pyproject_path, "rb") as f:
                pyproject_data = tomllib.load(f)

            dependencies = pyproject_data.get("project", {}).get("dependencies", [])
            return any("django" in dep.lower() for dep in dependencies)
        except (OSError, KeyError, AttributeError):
            return False


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["VariantDetectionUtils"]
