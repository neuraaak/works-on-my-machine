#!/usr/bin/env python3
"""
Script type detection and configuration for context menu entries.

This module provides automatic detection of script types and appropriate
configuration including icons and command building.
"""

import logging
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from ...exceptions.context.context_exceptions import (
    ContextUtilityError,
    ScriptError,
    ValidationError,
)
from ...utils.cli_utils import CLIUtils, run_silent


class ScriptType:
    """Script type enumeration and configuration."""

    PYTHON = "python"
    POWERSHELL = "powershell"
    BATCH = "batch"
    EXECUTABLE = "executable"
    UNKNOWN = "unknown"


class ScriptDetector:
    """Detect script types and provide appropriate configuration."""

    # Extension to script type mapping
    EXTENSIONS = {
        ".py": ScriptType.PYTHON,
        ".ps1": ScriptType.POWERSHELL,
        ".bat": ScriptType.BATCH,
        ".cmd": ScriptType.BATCH,
        ".exe": ScriptType.EXECUTABLE,
        ".msi": ScriptType.EXECUTABLE,
    }

    # Default icons for each script type
    DEFAULT_ICONS = {
        ScriptType.PYTHON: "python.exe,0",
        ScriptType.POWERSHELL: "powershell.exe,0",
        ScriptType.BATCH: "cmd.exe,0",
        ScriptType.EXECUTABLE: None,  # Use file's own icon
        ScriptType.UNKNOWN: None,
    }

    # Context parameters for each script type
    CONTEXT_PARAMS = {
        ScriptType.PYTHON: "%V",  # Directory context
        ScriptType.POWERSHELL: "%V",  # Directory context
        ScriptType.BATCH: "%V",  # Directory context
        ScriptType.EXECUTABLE: "%V",  # Directory context
        ScriptType.UNKNOWN: "%V",  # Default to directory
    }

    @classmethod
    def detect_type(cls, file_path: str) -> str:
        """
        Detect script type from file extension.

        Args:
            file_path: Path to the script file

        Returns:
            Script type string

        Raises:
            ValidationError: If file_path is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not file_path:
                raise ValidationError(
                    "script_detection", "file_path", "File path cannot be None or empty"
                )

            if not isinstance(file_path, str):
                raise ValidationError(
                    "script_detection",
                    "file_path",
                    f"File path must be a string, got {type(file_path).__name__}",
                )

            ext = Path(file_path).suffix.lower()
            return cls.EXTENSIONS.get(ext, ScriptType.UNKNOWN)

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error detecting script type: {e}",
                details=f"File path: {file_path}",
            ) from e

    @classmethod
    def get_default_icon(cls, script_type: str) -> Optional[str]:
        """
        Get default icon for script type.

        Args:
            script_type: Type of script

        Returns:
            Default icon path or None

        Raises:
            ValidationError: If script_type is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not script_type:
                raise ValidationError(
                    "script_icon", "script_type", "Script type cannot be None or empty"
                )

            if not isinstance(script_type, str):
                raise ValidationError(
                    "script_icon",
                    "script_type",
                    f"Script type must be a string, got {type(script_type).__name__}",
                )

            return cls.DEFAULT_ICONS.get(script_type)

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting default icon: {e}",
                details=f"Script type: {script_type}",
            ) from e

    @classmethod
    def get_context_params(cls, script_type: str) -> str:
        """
        Get context parameters for script type.

        Args:
            script_type: Type of script

        Returns:
            Context parameters string

        Raises:
            ValidationError: If script_type is invalid
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not script_type:
                raise ValidationError(
                    "script_params",
                    "script_type",
                    "Script type cannot be None or empty",
                )

            if not isinstance(script_type, str):
                raise ValidationError(
                    "script_params",
                    "script_type",
                    f"Script type must be a string, got {type(script_type).__name__}",
                )

            return cls.CONTEXT_PARAMS.get(script_type, "%V")

        except ValidationError:
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting context parameters: {e}",
                details=f"Script type: {script_type}",
            ) from e

    @classmethod
    def build_command(
        cls, script_type: str, script_path: str, context_params: str = None
    ) -> str:
        """
        Build appropriate command for script type.

        Args:
            script_type: Type of script
            script_path: Path to the script
            context_params: Context parameters (optional)

        Returns:
            Built command string

        Raises:
            ValidationError: If parameters are invalid
            ScriptError: If command building fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not script_type:
                raise ValidationError(
                    "command_building",
                    "script_type",
                    "Script type cannot be None or empty",
                )

            if not script_path:
                raise ValidationError(
                    "command_building",
                    "script_path",
                    "Script path cannot be None or empty",
                )

            if not isinstance(script_type, str):
                raise ValidationError(
                    "command_building",
                    "script_type",
                    f"Script type must be a string, got {type(script_type).__name__}",
                )

            if not isinstance(script_path, str):
                raise ValidationError(
                    "command_building",
                    "script_path",
                    f"Script path must be a string, got {type(script_path).__name__}",
                )

            if context_params is not None and not isinstance(context_params, str):
                raise ValidationError(
                    "command_building",
                    "context_params",
                    f"Context params must be a string, got {type(context_params).__name__}",
                )

            if context_params is None:
                context_params = cls.get_context_params(script_type)

            # Convert relative path to absolute path
            try:
                import os

                script_abs_path = os.path.abspath(script_path)
            except Exception as e:
                raise ScriptError(
                    "build_command",
                    script_path,
                    f"Failed to resolve absolute path: {e}",
                ) from e

            if script_type == ScriptType.PYTHON:
                # Use the same logic as RuntimeManager to find Python
                python_cmds = ["python3", "python", "py"]

                for cmd in python_cmds:
                    try:
                        if CLIUtils().check_command_available(cmd):
                            try:
                                result = run_silent([cmd, "--version"])
                                if result.success and result.stdout.strip():
                                    version = result.stdout.strip().split()[1]
                                    version_parts = [int(x) for x in version.split(".")]
                                    if version_parts >= [3, 8]:  # Minimum Python 3.8
                                        python_exe = shutil.which(cmd)
                                        if python_exe:
                                            return f'"{python_exe}" "{script_abs_path}" "{context_params}"'
                            except (IndexError, ValueError) as e:
                                logging.getLogger(__name__).warning(
                                    f"Failed to parse Python version for {cmd}: {e}"
                                )
                                continue
                    except Exception as e:
                        logging.getLogger(__name__).warning(
                            f"Failed to check command availability for {cmd}: {e}"
                        )
                        continue

                # Fallback: try py launcher directly
                return f'cmd.exe /k py "{script_abs_path}" "{context_params}"'

            elif script_type == ScriptType.POWERSHELL:
                return f'powershell.exe -ExecutionPolicy Bypass -File "{script_abs_path}" "{context_params}"'

            elif (
                script_type == ScriptType.BATCH or script_type == ScriptType.EXECUTABLE
            ):
                return f'"{script_abs_path}" "{context_params}"'

            else:
                # Unknown type, try to execute directly
                return f'"{script_abs_path}" "{context_params}"'

        except (ValidationError, ScriptError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error building command: {e}",
                details=f"Script type: {script_type}, Script path: {script_path}",
            ) from e

    @classmethod
    def get_script_info(cls, file_path: str) -> Dict[str, Any]:
        """
        Get comprehensive script information.

        Args:
            file_path: Path to the script file

        Returns:
            Dictionary containing script information

        Raises:
            ValidationError: If file_path is invalid
            ScriptError: If script info retrieval fails
            ContextUtilityError: For unexpected errors
        """
        try:
            # Input validation
            if not file_path:
                raise ValidationError(
                    "script_info", "file_path", "File path cannot be None or empty"
                )

            if not isinstance(file_path, str):
                raise ValidationError(
                    "script_info",
                    "file_path",
                    f"File path must be a string, got {type(file_path).__name__}",
                )

            # Detect script type
            try:
                script_type = cls.detect_type(file_path)
            except Exception as e:
                raise ScriptError(
                    "get_info", file_path, f"Failed to detect script type: {e}"
                ) from e

            # Get script information
            try:
                return {
                    "type": script_type,
                    "extension": Path(file_path).suffix.lower(),
                    "default_icon": cls.get_default_icon(script_type),
                    "context_params": cls.get_context_params(script_type),
                    "command": cls.build_command(script_type, file_path),
                }
            except Exception as e:
                raise ScriptError(
                    "get_info", file_path, f"Failed to build script information: {e}"
                ) from e

        except (ValidationError, ScriptError):
            raise
        except Exception as e:
            raise ContextUtilityError(
                f"Unexpected error getting script info: {e}",
                details=f"File path: {file_path}",
            ) from e
