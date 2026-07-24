#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# JAVASCRIPT PROJECT CONFIG - JavaScript Project Configuration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Configuration for JavaScript project creation and setup.

This module provides:
- JavaScript-specific directory structures
- Development dependencies by project type
- Default file templates
- JavaScript project conventions
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
class JavaScriptProjectConfig:
    """JavaScript project configuration (static, read-only)."""

    # ///////////////////////////////////////////////////////////
    # DIRECTORY STRUCTURE
    # ///////////////////////////////////////////////////////////

    # JavaScript-specific directories (in addition to common ones)
    JAVASCRIPT_DIRECTORIES: ClassVar[list[str]] = []

    # React-specific directories
    REACT_DIRECTORIES: ClassVar[list[str]] = ["public"]

    # Vue-specific directories
    VUE_DIRECTORIES: ClassVar[list[str]] = ["public"]

    # ///////////////////////////////////////////////////////////
    # DEVELOPMENT DEPENDENCIES
    # ///////////////////////////////////////////////////////////

    # Common dev dependencies for all JavaScript projects
    COMMON_DEV_DEPENDENCIES: ClassVar[list[str]] = [
        "eslint",
        "prettier",
        "husky",
        "lint-staged",
        "@types/node",
    ]

    # Node.js specific dev dependencies
    NODE_DEV_DEPENDENCIES: ClassVar[list[str]] = []

    # React specific dev dependencies
    REACT_DEV_DEPENDENCIES: ClassVar[list[str]] = [
        "@types/react",
        "@types/react-dom",
        "@testing-library/react",
        "@testing-library/jest-dom",
    ]

    # Vue specific dev dependencies
    VUE_DEV_DEPENDENCIES: ClassVar[list[str]] = [
        "@vue/cli-service",
        "@vue/compiler-sfc",
    ]

    # ///////////////////////////////////////////////////////////
    # RUNTIME DEPENDENCIES
    # ///////////////////////////////////////////////////////////

    # React runtime dependencies
    REACT_DEPENDENCIES: ClassVar[dict[str, str]] = {
        "react": "^18.2.0",
        "react-dom": "^18.2.0",
    }

    # Vue runtime dependencies
    VUE_DEPENDENCIES: ClassVar[dict[str, str]] = {
        "vue": "^3.3.0",
    }

    # Node.js runtime dependencies (empty by default)
    NODE_DEPENDENCIES: ClassVar[dict[str, str]] = {}

    # ///////////////////////////////////////////////////////////
    # FILE NAMES
    # ///////////////////////////////////////////////////////////

    # Package.json file name
    PACKAGE_JSON_FILE: ClassVar[str] = "package.json"

    # ESLint config file name
    ESLINT_CONFIG_FILE: ClassVar[str] = ".eslintrc.js"

    # Prettier config file name
    PRETTIER_CONFIG_FILE: ClassVar[str] = ".prettierrc"

    # Jest config file name
    JEST_CONFIG_FILE: ClassVar[str] = "jest.config.js"

    # ///////////////////////////////////////////////////////////
    # PROJECT TYPE MAPPING
    # ///////////////////////////////////////////////////////////

    # Mapping from project type to variant name
    PROJECT_TYPE_TO_VARIANT: ClassVar[dict[str, str]] = {
        "javascript": "js",
        "node": "js",
        "react": "react",
        "vue": "vue",
    }

    # ///////////////////////////////////////////////////////////
    # STATIC METHODS
    # ///////////////////////////////////////////////////////////

    @staticmethod
    def get_dev_dependencies(project_type: str) -> list[str]:
        """Get development dependencies for a project type.

        Args:
            project_type: Type of JavaScript project (node, react, vue)

        Returns:
            list[str]: List of development dependency names
        """
        deps = list(JavaScriptProjectConfig.COMMON_DEV_DEPENDENCIES)

        if project_type == "react":
            deps.extend(JavaScriptProjectConfig.REACT_DEV_DEPENDENCIES)
        elif project_type == "vue":
            deps.extend(JavaScriptProjectConfig.VUE_DEV_DEPENDENCIES)
        # node doesn't have additional deps

        return deps

    @staticmethod
    def get_runtime_dependencies(project_type: str) -> dict[str, str]:
        """Get runtime dependencies for a project type.

        Args:
            project_type: Type of JavaScript project (node, react, vue)

        Returns:
            dict[str, str]: Dictionary of package names to versions
        """
        if project_type == "react":
            return JavaScriptProjectConfig.REACT_DEPENDENCIES.copy()
        elif project_type == "vue":
            return JavaScriptProjectConfig.VUE_DEPENDENCIES.copy()
        else:
            return JavaScriptProjectConfig.NODE_DEPENDENCIES.copy()

    @staticmethod
    def get_directories(project_type: str) -> list[str]:
        """Get additional directories for a project type.

        Args:
            project_type: Type of JavaScript project (node, react, vue)

        Returns:
            list[str]: List of additional directory names
        """
        if project_type == "react":
            return list(JavaScriptProjectConfig.REACT_DIRECTORIES)
        elif project_type == "vue":
            return list(JavaScriptProjectConfig.VUE_DIRECTORIES)
        else:
            return list(JavaScriptProjectConfig.JAVASCRIPT_DIRECTORIES)

    @staticmethod
    def get_variant(project_type: str) -> str:
        """Get variant name for a project type.

        Args:
            project_type: Type of JavaScript project (javascript, node, react, vue)

        Returns:
            str: Variant name (js, react, vue)
        """
        return JavaScriptProjectConfig.PROJECT_TYPE_TO_VARIANT.get(project_type, "js")


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["JavaScriptProjectConfig"]
