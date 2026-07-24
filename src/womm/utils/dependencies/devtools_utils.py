#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEV TOOLS UTILS - Pure Dev Tools Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for development tools operations.

This module provides stateless functions for:
- Tool categorization
- Installation method detection
- Tool path resolution
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import shutil

# ///////////////////////////////////////////////////////////////
# TOOL CATEGORIZATION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def get_tool_type_for_language(
    language: str, tool: str, tools_config: dict[str, dict[str, list[str]]]
) -> str | None:
    """
    Get tool type for a tool in a language.

    Args:
        language: Programming language
        tool: Tool name
        tools_config: Development tools configuration

    Returns:
        str | None: Tool type (formatting, linting, etc.) or None
    """
    if language not in tools_config:
        return None

    language_tools = tools_config[language]
    for tool_type, tools in language_tools.items():
        if tool in tools:
            return tool_type

    return None


def get_all_tools_for_language(
    language: str, tools_config: dict[str, dict[str, list[str]]]
) -> list[str]:
    """
    Get all tools for a language.

    Args:
        language: Programming language
        tools_config: Development tools configuration

    Returns:
        list[str]: List of tool names
    """
    if language not in tools_config:
        return []

    tools = []
    for tool_list in tools_config[language].values():
        tools.extend(tool_list)

    return tools


# ///////////////////////////////////////////////////////////////
# INSTALLATION METHOD FUNCTIONS
# ///////////////////////////////////////////////////////////////


def detect_installation_method(
    tool: str,
    language: str,
    tool_configs: dict[str, dict[str, str]] | None = None,
    installation_methods: dict[str, str] | None = None,
) -> str:
    """
    Detect installation method for a tool.

    Args:
        tool: Tool name
        language: Programming language
        tool_configs: Special tool configurations
        installation_methods: Language installation methods

    Returns:
        str: Installation method (pip, npm, auto)
    """
    # Check special tool configs first
    if tool_configs and tool in tool_configs:
        return tool_configs[tool].get("install_method", "auto")

    # Check language installation methods
    if installation_methods and language in installation_methods:
        return installation_methods[language]

    return "auto"


def resolve_tool_path(tool: str, check_method: str = "standard") -> str | None:
    """
    Resolve path to a tool executable.

    Args:
        tool: Tool name
        check_method: Method to check tool (standard, npx)

    Returns:
        str | None: Path to tool or None if not found
    """
    if check_method == "standard":
        return shutil.which(tool)

    # For npx tools, we can't resolve the path directly
    # but we can check if npx is available
    if check_method == "npx":
        if shutil.which("npx"):
            return f"npx {tool}"
        return None

    return None
