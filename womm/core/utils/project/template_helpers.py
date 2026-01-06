#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEMPLATE HELPERS - Template Generation Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Template Helpers - Utilities for cross-platform template generation.
Generates cross-platform templates.
Validates placeholders in a template.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import os
import platform
import re
from pathlib import Path

# Local imports
from ...exceptions.project import ProjectUtilityError, TemplateError


def get_platform_info() -> dict[str, str | bool]:
    """
    Returns platform information.

    Returns:
        Dict[str, str]: Platform information dictionary

    Raises:
        ProjectUtilityError: If platform detection fails
    """
    try:
        system = platform.system()
        return {
            "system": system,
            "system_lower": system.lower(),
            "is_windows": system == "Windows",
            "is_linux": system == "Linux",
            "is_macos": system == "Darwin",
            "path_separator": os.sep,
            "line_ending": "\r\n" if system == "Windows" else "\n",
        }
    except Exception as e:
        # Wrap unexpected external exceptions
        raise ProjectUtilityError(
            message=f"Failed to get platform information: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def get_python_paths() -> dict[str, str]:
    """
    Returns Python paths according to OS.

    Returns:
        Dict[str, str]: Python paths dictionary

    Raises:
        ProjectUtilityError: If Python paths detection fails
    """
    try:
        platform_info = get_platform_info()

        if platform_info["is_windows"]:
            return {
                "venv_python": "./venv/Scripts/python.exe",
                "venv_activate": "./venv/Scripts/activate.bat",
                "venv_pip": "./venv/Scripts/pip.exe",
                "python_executable": "python.exe",
            }
        else:  # Linux/macOS
            return {
                "venv_python": "./venv/bin/python",
                "venv_activate": "source ./venv/bin/activate",
                "venv_pip": "./venv/bin/pip",
                "python_executable": "python3",
            }
    except (TemplateError, ProjectUtilityError):
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise ProjectUtilityError(
            message=f"Failed to get Python paths: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def get_node_paths() -> dict[str, str]:
    """
    Returns Node.js paths according to OS.

    Returns:
        Dict[str, str]: Node.js paths dictionary

    Raises:
        ProjectUtilityError: If Node.js paths detection fails
    """
    try:
        platform_info = get_platform_info()

        if platform_info["is_windows"]:
            return {
                "npm_executable": "npm.cmd",
                "node_executable": "node.exe",
                "npx_executable": "npx.cmd",
            }
        else:  # Linux/macOS
            return {
                "npm_executable": "npm",
                "node_executable": "node",
                "npx_executable": "npx",
            }
    except (TemplateError, ProjectUtilityError):
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise ProjectUtilityError(
            message=f"Failed to get Node.js paths: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def get_shell_commands() -> dict[str, str]:
    """
    Returns shell commands according to OS.

    Returns:
        Dict[str, str]: Shell commands dictionary

    Raises:
        ProjectUtilityError: If shell commands detection fails
    """
    try:
        platform_info = get_platform_info()

        if platform_info["is_windows"]:
            return {
                "shell": "cmd",
                "shell_extension": ".bat",
                "remove_dir": "rmdir /s /q",
                "copy_file": "copy",
                "move_file": "move",
                "make_executable": "rem",  # Not needed on Windows
                "which": "where",
            }
        else:  # Linux/macOS
            return {
                "shell": "bash",
                "shell_extension": ".sh",
                "remove_dir": "rm -rf",
                "copy_file": "cp",
                "move_file": "mv",
                "make_executable": "chmod +x",
                "which": "which",
            }
    except (TemplateError, ProjectUtilityError):
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise ProjectUtilityError(
            message=f"Failed to get shell commands: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def replace_platform_placeholders(text: str, **extra_vars) -> str:
    r"""
    Replace platform-specific placeholders in a text.

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

    Raises:
        ProjectUtilityError: If placeholder replacement fails
    """
    try:
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

    except (TemplateError, ProjectUtilityError):
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise ProjectUtilityError(
            message=f"Failed to replace platform placeholders: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def generate_cross_platform_template(
    template_path: Path,
    output_path: Path,
    template_vars: dict[str, str] | None = None,
) -> None:
    """
    Generates a file from a template by replacing placeholders.

    Args:
        template_path: Path to the template to use
        output_path: Path to the output file
        template_vars: Variables to replace in the template

    Raises:
        TemplateError: If template generation fails
    """
    try:
        # Input validation
        if not template_path:
            raise TemplateError(
                operation="generate_cross_platform_template",
                template_path="None",
                reason="Template path cannot be None",
                details="Empty or None template path provided",
            )

        if not template_path.exists():
            raise TemplateError(
                operation="generate_cross_platform_template",
                template_path=str(template_path),
                reason="Template file does not exist",
                details=f"Template: {template_path}",
            )

        if not template_path.is_file():
            raise TemplateError(
                operation="generate_cross_platform_template",
                template_path=str(template_path),
                reason="Template path is not a file",
                details=f"Path: {template_path}",
            )

        if not output_path:
            raise TemplateError(
                operation="generate_cross_platform_template",
                template_path=str(template_path),
                reason="Output path cannot be None",
                details="Empty or None output path provided",
            )

        if template_vars is None:
            template_vars = {}

        # Read template
        try:
            with open(template_path, encoding="utf-8") as f:
                template_content = f.read()
        except (PermissionError, OSError) as e:
            raise TemplateError(
                operation="generate_cross_platform_template",
                template_path=str(template_path),
                reason="Cannot read template file",
                details=f"File: {template_path}, Error: {e}",
            ) from e
        except UnicodeDecodeError as e:
            raise TemplateError(
                operation="generate_cross_platform_template",
                template_path=str(template_path),
                reason="Template file encoding error",
                details=f"File: {template_path}, Error: {e}",
            ) from e

        # Replace placeholders
        result_content = replace_platform_placeholders(
            template_content, **template_vars
        )

        # Create output directory if necessary
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            raise TemplateError(
                operation="generate_cross_platform_template",
                template_path=str(template_path),
                reason="Cannot create output directory",
                details=f"Directory: {output_path.parent}, Error: {e}",
            ) from e

        # Write output file
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(result_content)
        except (PermissionError, OSError) as e:
            raise TemplateError(
                operation="generate_cross_platform_template",
                template_path=str(template_path),
                reason="Cannot write output file",
                details=f"File: {output_path}, Error: {e}",
            ) from e

        logging.info(f"✅ Template generated: {output_path}")

    except (TemplateError, ProjectUtilityError):
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise ProjectUtilityError(
            message=f"Unexpected error during template generation: {e}",
            details=f"Exception type: {type(e).__name__}, Template: {template_path}, Output: {output_path}",
        ) from e


def validate_template_placeholders(
    template_path: Path,
) -> dict[str, str | bool | int | list]:
    """
    Validate placeholders in a template and return statistics.

    Args:
        template_path: Path to the template to validate

    Returns:
        Dict[str, Any]: A dictionary containing validation statistics

    Raises:
        TemplateError: If template validation fails
    """
    try:
        # Input validation
        if not template_path:
            raise TemplateError(
                operation="validate_template_placeholders",
                template_path="None",
                reason="Template path cannot be None",
                details="Empty or None template path provided",
            )

        if not template_path.exists():
            raise TemplateError(
                operation="validate_template_placeholders",
                template_path=str(template_path),
                reason="Template file does not exist",
                details=f"Template: {template_path}",
            )

        if not template_path.is_file():
            raise TemplateError(
                operation="validate_template_placeholders",
                template_path=str(template_path),
                reason="Template path is not a file",
                details=f"Path: {template_path}",
            )

        # Read template content
        try:
            with open(template_path, encoding="utf-8") as f:
                content = f.read()
        except (PermissionError, OSError) as e:
            raise TemplateError(
                operation="validate_template_placeholders",
                template_path=str(template_path),
                reason="Cannot read template file",
                details=f"File: {template_path}, Error: {e}",
            ) from e
        except UnicodeDecodeError as e:
            raise TemplateError(
                operation="validate_template_placeholders",
                template_path=str(template_path),
                reason="Template file encoding error",
                details=f"File: {template_path}, Error: {e}",
            ) from e

        # Search for placeholders
        try:
            placeholder_pattern = r"\{\{([A-Z_]+)\}\}"
            placeholders = re.findall(placeholder_pattern, content)
        except re.error as e:
            raise TemplateError(
                operation="validate_template_placeholders",
                template_path=str(template_path),
                reason="Invalid placeholder pattern",
                details=f"Regex error: {e}",
            ) from e

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

    except (TemplateError, ProjectUtilityError):
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise ProjectUtilityError(
            message=f"Unexpected error during template validation: {e}",
            details=f"Exception type: {type(e).__name__}, Template: {template_path}",
        ) from e
