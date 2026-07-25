#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEMPLATE UTILS - Pure Template Utility Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for template processing.

This module provides stateless functions for:
- Replacing platform placeholders
- Validating template placeholders
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import re
from pathlib import Path

# Local imports
from .platform_utils import (
    get_node_paths,
    get_platform_info,
    get_python_paths,
    get_shell_commands,
)

# ///////////////////////////////////////////////////////////////
# TEMPLATE PROCESSING FUNCTIONS
# ///////////////////////////////////////////////////////////////


def replace_platform_placeholders(text: str, **extra_vars: str) -> str:
    r"""Replace platform-specific placeholders in a text.

    Supported placeholders:
    - {{PYTHON_PATH}} - Path to Python executable
    - {{VENV_ACTIVATE}} - Virtual environment activation command
    - {{SHELL_EXT}} - Shell script extension (.bat or .sh)
    - {{PATH_SEP}} - Path separator (/ or \\)
    - {{LINE_ENDING}} - Line ending (\r\n or \n)

    Args:
        text: Text containing placeholders to replace
        **extra_vars: Additional variables for replacement

    Returns:
        str: Text with placeholders replaced
    """
    if not text:
        return text

    platform_info = get_platform_info()
    python_paths = get_python_paths()
    node_paths = get_node_paths()
    shell_commands = get_shell_commands()

    # Replacement dictionary
    replacements = {
        # Platform information
        "PLATFORM_SYSTEM": platform_info["system"],
        "PLATFORM_SYSTEM_LOWER": platform_info["system_lower"],
        "IS_WINDOWS": str(platform_info["is_windows"]).lower(),
        "IS_LINUX": str(platform_info["is_linux"]).lower(),
        "IS_MACOS": str(platform_info["is_macos"]).lower(),
        "PATH_SEP": platform_info["path_separator"],
        "LINE_ENDING": platform_info["line_ending"],
        # Python paths
        "PYTHON_PATH": python_paths["venv_python"],
        "VENV_ACTIVATE": python_paths["venv_activate"],
        "VENV_PIP": python_paths["venv_pip"],
        "PYTHON_EXECUTABLE": python_paths["python_executable"],
        # Node.js paths
        "NPM_EXECUTABLE": node_paths["npm_executable"],
        "NODE_EXECUTABLE": node_paths["node_executable"],
        "NPX_EXECUTABLE": node_paths["npx_executable"],
        # Shell commands
        "SHELL": shell_commands["shell"],
        "SHELL_EXT": shell_commands["shell_extension"],
        "REMOVE_DIR": shell_commands["remove_dir"],
        "COPY_FILE": shell_commands["copy_file"],
        "MOVE_FILE": shell_commands["move_file"],
        "MAKE_EXECUTABLE": shell_commands["make_executable"],
        "WHICH": shell_commands["which"],
        # Additional variables
        **extra_vars,
    }

    # Replace placeholders
    result = text
    for key, value in replacements.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))

    return result


def validate_template_placeholders(
    template_path: Path,
) -> dict[str, str | bool | int | list]:
    """Validate placeholders in a template and return statistics.

    Args:
        template_path: Path to the template to validate

    Returns:
        dict[str, str | bool | int | list]: A dictionary containing validation statistics

    Raises:
        ValueError: If the template path is missing
        FileNotFoundError: If the template file does not exist
        IsADirectoryError: If the template path is not a file
        OSError: If the template file cannot be read
        UnicodeDecodeError: If the template file has an encoding error
    """
    if not template_path:
        raise ValueError("Template path cannot be None")

    if not template_path.exists():
        raise FileNotFoundError(f"Template file does not exist: {template_path}")

    if not template_path.is_file():
        raise IsADirectoryError(f"Template path is not a file: {template_path}")

    with open(template_path, encoding="utf-8") as f:
        content = f.read()

    # Search for placeholders
    placeholder_pattern = r"\{\{([A-Z_]+)\}\}"
    placeholders = re.findall(placeholder_pattern, content)

    # Supported placeholders
    supported_placeholders = {
        "PLATFORM_SYSTEM",
        "PLATFORM_SYSTEM_LOWER",
        "IS_WINDOWS",
        "IS_LINUX",
        "IS_MACOS",
        "PATH_SEP",
        "LINE_ENDING",
        "PYTHON_PATH",
        "VENV_ACTIVATE",
        "VENV_PIP",
        "PYTHON_EXECUTABLE",
        "NPM_EXECUTABLE",
        "NODE_EXECUTABLE",
        "NPX_EXECUTABLE",
        "SHELL",
        "SHELL_EXT",
        "REMOVE_DIR",
        "COPY_FILE",
        "MOVE_FILE",
        "MAKE_EXECUTABLE",
        "WHICH",
        # Standard project placeholders
        "PROJECT_NAME",
        "PROJECT_DESCRIPTION",
        "AUTHOR_NAME",
        "AUTHOR_EMAIL",
        "PROJECT_URL",
        "PROJECT_REPOSITORY",
        "PROJECT_DOCS_URL",
        "PROJECT_KEYWORDS",
    }

    # Classify placeholders
    found_placeholders = set(placeholders)
    supported_found = found_placeholders & supported_placeholders
    unsupported_found = found_placeholders - supported_placeholders

    return {
        "total_placeholders": len(found_placeholders),
        "supported_placeholders": list(supported_found),
        "unsupported_placeholders": list(unsupported_found),
        "is_valid": len(unsupported_found) == 0,
        "template_path": str(template_path),
    }


def generate_cross_platform_template(
    template_path: Path,
    output_path: Path,
    template_vars: dict[str, str] | None = None,
) -> None:
    """Generate a file from a template by replacing placeholders.

    Args:
        template_path: Path to the template to use
        output_path: Path to the output file
        template_vars: Variables to replace in the template

    Raises:
        ValueError: If the template or output path is missing
        FileNotFoundError: If the template file does not exist
        IsADirectoryError: If the template path is not a file
        OSError: If the template cannot be read or the output cannot be written
        UnicodeDecodeError: If the template file has an encoding error
    """
    if not template_path:
        raise ValueError("Template path cannot be None")

    if not template_path.exists():
        raise FileNotFoundError(f"Template file does not exist: {template_path}")

    if not template_path.is_file():
        raise IsADirectoryError(f"Template path is not a file: {template_path}")

    if not output_path:
        raise ValueError("Output path cannot be None")

    if template_vars is None:
        template_vars = {}

    # Read template
    with open(template_path, encoding="utf-8") as f:
        template_content = f.read()

    # Replace placeholders
    result_content = replace_platform_placeholders(template_content, **template_vars)

    # Create output directory if necessary
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result_content)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "generate_cross_platform_template",
    "replace_platform_placeholders",
    "validate_template_placeholders",
]
