#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# VSCODE CONFIG - VSCode Configuration Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Cross-Platform VSCode Configuration.
Automatically generates VSCode configurations adapted to the OS.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import logging
import platform
from pathlib import Path

# Local imports
from ...exceptions.project import ProjectUtilityError, VSCodeConfigError


def get_python_interpreter_paths() -> str:
    """
    Returns Python interpreter paths according to the OS.

    Returns:
        str: Python interpreter path for the current platform

    Raises:
        ProjectUtilityError: If platform detection fails
    """
    try:
        system = platform.system().lower()

        paths = {
            "windows": "./venv/Scripts/python.exe",
            "linux": "./venv/bin/python",
            "darwin": "./venv/bin/python",  # macOS
        }

        return paths.get(system, "./venv/bin/python")

    except Exception as e:
        # Wrap unexpected external exceptions
        raise ProjectUtilityError(
            message=f"Failed to get Python interpreter paths: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def get_platform_specific_settings(
    language: str = "python",
) -> dict[str, str | bool | int | list | dict]:
    """
    Generate platform-specific VSCode settings.

    Args:
        language: Programming language for configuration (default: "python")

    Returns:
        Dict[str, Any]: Platform-specific VSCode settings

    Raises:
        ProjectUtilityError: If settings generation fails
    """
    try:
        if not language:
            raise ProjectUtilityError(
                message="Language parameter cannot be empty",
                details="Empty or None language provided for VSCode settings",
            )

        system = platform.system().lower()

        if language == "python":
            base_settings = {
                # Base configuration (common)
                "editor.formatOnSave": True,
                "editor.formatOnPaste": True,
                "editor.codeActionsOnSave": {"source.organizeImports": "explicit"},
                "editor.rulers": [88],
                "editor.tabSize": 4,
                "editor.insertSpaces": True,
                "files.trimTrailingWhitespace": True,
                "files.insertFinalNewline": True,
                "files.trimFinalNewlines": True,
                # Configuration Python
                "python.terminal.activateEnvironment": True,
                "python.linting.enabled": True,
                "python.linting.flake8Enabled": True,
                "python.linting.flake8Args": ["--config=.flake8"],
                "python.formatting.provider": "black",
                "python.formatting.blackArgs": [
                    "--line-length=88",
                    "--target-version=py39",
                ],
                "python.sortImports.args": ["--profile=black", "--line-length=88"],
                "[python]": {
                    "editor.defaultFormatter": "ms-python.black-formatter",
                    "editor.formatOnSave": True,
                    "editor.codeActionsOnSave": {
                        "source.organizeImports": "explicit",
                    },
                },
                "python.testing.pytestEnabled": True,
                "python.testing.pytestArgs": [
                    "tests",
                    "--tb=short",
                    "--strict-markers",
                ],
                "python.testing.autoTestDiscoverOnSaveEnabled": True,
                "python.analysis.extraPaths": ["./src"],
                "python.analysis.autoSearchPaths": True,
                "python.analysis.typeCheckingMode": "basic",
                # Common exclusions
                "files.exclude": {
                    "**/__pycache__": True,
                    "**/*.pyc": True,
                    "**/.pytest_cache": True,
                    "**/htmlcov": True,
                    "**/.coverage": True,
                    "**/build": True,
                    "**/dist": True,
                    "**/*.egg-info": True,
                    "**/.mypy_cache": True,
                    "**/.tox": True,
                    "**/venv": True,
                    "**/.venv": True,
                    "**/.env*": True,
                    "**/.secret*": True,
                    "**/*password*": True,
                    "**/*secret*": True,
                    "**/*.key": True,
                    "**/*.pem": True,
                    "**/*.crt": True,
                    "**/credentials": True,
                },
                "files.watcherExclude": {
                    "**/.git/objects/**": True,
                    "**/.git/subtree-cache/**": True,
                    "**/venv/**": True,
                    "**/.venv/**": True,
                    "**/__pycache__/**": True,
                    "**/.pytest_cache/**": True,
                    "**/htmlcov/**": True,
                    "**/.env*": True,
                    "**/.secret*": True,
                    "**/*password*": True,
                    "**/*secret*": True,
                    "**/*.key": True,
                    "**/*.pem": True,
                    "**/*.crt": True,
                    "**/credentials/**": True,
                },
                "git.ignoreLimitWarning": True,
            }

            # Add OS-specific interpreter path
            python_path = get_python_interpreter_paths()
            base_settings["python.defaultInterpreterPath"] = python_path

            # OS-specific terminal environment configuration
            if system == "windows":
                base_settings["terminal.integrated.env.windows"] = {
                    "PYTHONPATH": "${workspaceFolder}/src"
                }
            elif system == "darwin":  # macOS
                base_settings["terminal.integrated.env.osx"] = {
                    "PYTHONPATH": "${workspaceFolder}/src"
                }
            else:  # Linux et autres Unix
                base_settings["terminal.integrated.env.linux"] = {
                    "PYTHONPATH": "${workspaceFolder}/src"
                }

            return base_settings

        elif language == "javascript":
            return {
                "editor.formatOnSave": True,
                "editor.formatOnPaste": True,
                "editor.codeActionsOnSave": {
                    "source.organizeImports": "explicit",
                    "source.fixAll.eslint": "explicit",
                },
                "editor.rulers": [80],
                "editor.tabSize": 2,
                "editor.insertSpaces": True,
                "files.trimTrailingWhitespace": True,
                "files.insertFinalNewline": True,
                "files.trimFinalNewlines": True,
                # Configuration JavaScript/TypeScript
                "javascript.preferences.includePackageJsonAutoImports": "auto",
                "typescript.preferences.includePackageJsonAutoImports": "auto",
                "javascript.updateImportsOnFileMove.enabled": "always",
                "typescript.updateImportsOnFileMove.enabled": "always",
                # ESLint
                "eslint.enable": True,
                "eslint.format.enable": True,
                "eslint.lintTask.enable": True,
                # Prettier
                "[javascript]": {
                    "editor.defaultFormatter": "esbenp.prettier-vscode",
                    "editor.formatOnSave": True,
                },
                "[typescript]": {
                    "editor.defaultFormatter": "esbenp.prettier-vscode",
                    "editor.formatOnSave": True,
                },
                "[json]": {"editor.defaultFormatter": "esbenp.prettier-vscode"},
                # Exclusions
                "files.exclude": {
                    "**/node_modules": True,
                    "**/dist": True,
                    "**/build": True,
                    "**/.next": True,
                    "**/coverage": True,
                    "**/.nyc_output": True,
                },
                "files.watcherExclude": {
                    "**/node_modules/**": True,
                    "**/dist/**": True,
                    "**/build/**": True,
                    "**/.next/**": True,
                },
            }

        return {}

    except (VSCodeConfigError, ProjectUtilityError):
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise ProjectUtilityError(
            message=f"Failed to generate platform-specific settings: {e}",
            details=f"Exception type: {type(e).__name__}, Language: {language}",
        ) from e


def generate_vscode_config(target_dir: Path, language: str = "python") -> None:
    """
    Generates VSCode configuration for a project.

    Args:
        target_dir: Target directory for VSCode configuration
        language: Programming language for configuration (default: "python")

    Raises:
        VSCodeConfigError: If VSCode configuration generation fails
    """
    try:
        # Input validation
        if not target_dir:
            raise VSCodeConfigError(
                operation="generate_vscode_config",
                config_path="None",
                reason="Target directory cannot be None",
                details="Empty or None target directory provided",
            )

        if not target_dir.exists():
            raise VSCodeConfigError(
                operation="generate_vscode_config",
                config_path=str(target_dir),
                reason="Target directory does not exist",
                details=f"Directory: {target_dir}",
            )

        if not target_dir.is_dir():
            raise VSCodeConfigError(
                operation="generate_vscode_config",
                config_path=str(target_dir),
                reason="Target path is not a directory",
                details=f"Path: {target_dir}",
            )

        vscode_dir = target_dir / ".vscode"

        try:
            vscode_dir.mkdir(exist_ok=True)
        except (PermissionError, OSError) as e:
            raise VSCodeConfigError(
                operation="generate_vscode_config",
                config_path=str(vscode_dir),
                reason="Cannot create VSCode directory",
                details=f"Directory: {vscode_dir}, Error: {e}",
            ) from e

        # Generate settings.json
        settings = get_platform_specific_settings(language)
        settings_file = vscode_dir / "settings.json"

        try:
            with open(settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except (PermissionError, OSError) as e:
            raise VSCodeConfigError(
                operation="generate_vscode_config",
                config_path=str(settings_file),
                reason="Cannot write VSCode settings file",
                details=f"File: {settings_file}, Error: {e}",
            ) from e
        except (TypeError, ValueError) as e:
            raise VSCodeConfigError(
                operation="generate_vscode_config",
                config_path=str(settings_file),
                reason="Invalid settings data for JSON serialization",
                details=f"Error: {e}",
            ) from e

        logging.info(
            f"✅ VSCode configuration generated for {language} in {vscode_dir}"
        )
        logging.info(f"🖥️  Detected platform: {platform.system()}")

        if language == "python":
            python_path = get_python_interpreter_paths()
            logging.info(f"🐍 Python path configured: {python_path}")

    except (VSCodeConfigError, ProjectUtilityError):
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise ProjectUtilityError(
            message=f"Unexpected error during VSCode configuration generation: {e}",
            details=f"Exception type: {type(e).__name__}, Target dir: {target_dir}, Language: {language}",
        ) from e
