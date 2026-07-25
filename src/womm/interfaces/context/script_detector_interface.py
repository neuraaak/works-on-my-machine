#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SCRIPT DETECTOR INTERFACE - Context Script Detection
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Script type detection and configuration for context menu entries.

This module provides automatic detection of script types and appropriate
configuration including icons and command building.

This interface never raises: :meth:`get_script_info` returns a typed Result.
The lookup helpers it composes are total functions over ``ScriptConfig``.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import os
import shutil
from pathlib import Path
from typing import ClassVar

# Local imports
from ...exceptions.common import CommandServiceError
from ...services import CommandRunnerService
from ...shared.configs.context import ScriptConfig
from ...shared.results import ScriptInfoResult

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class ScriptType:
    """Script type enumeration and configuration."""

    PYTHON = ScriptConfig.TYPE_PYTHON
    POWERSHELL = ScriptConfig.TYPE_POWERSHELL
    BATCH = ScriptConfig.TYPE_BATCH
    EXECUTABLE = ScriptConfig.TYPE_EXECUTABLE
    UNKNOWN = ScriptConfig.TYPE_UNKNOWN


class ContextScriptDetectorInterface:
    """Detect script types and provide appropriate configuration."""

    # Use configuration from ScriptConfig
    EXTENSIONS: ClassVar[dict[str, str]] = ScriptConfig.EXTENSION_TO_TYPE
    DEFAULT_ICONS: ClassVar[dict[str, str | None]] = ScriptConfig.DEFAULT_ICONS
    CONTEXT_PARAMS: ClassVar[dict[str, str]] = ScriptConfig.CONTEXT_PARAMETERS

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    @classmethod
    def detect_type(cls, file_path: str) -> str:
        """
        Detect script type from file extension.

        Total function: an empty or unrecognized path yields ``ScriptType.UNKNOWN``.

        Args:
            file_path: Path to the script file

        Returns:
            Script type string
        """
        if not file_path:
            return ScriptType.UNKNOWN

        ext = Path(file_path).suffix.lower()
        return cls.EXTENSIONS.get(ext, ScriptType.UNKNOWN)

    @classmethod
    def get_default_icon(cls, script_type: str) -> str | None:
        """
        Get default icon for script type.

        Args:
            script_type: Type of script

        Returns:
            Default icon path, or None when the type has no default
        """
        return cls.DEFAULT_ICONS.get(script_type)

    @classmethod
    def get_context_params(cls, script_type: str) -> str:
        """
        Get context parameters for script type.

        Args:
            script_type: Type of script

        Returns:
            Context parameters string (``%V`` when the type is unknown)
        """
        return cls.CONTEXT_PARAMS.get(script_type, "%V")

    @classmethod
    def get_script_info(cls, file_path: str) -> ScriptInfoResult:
        """
        Get comprehensive script information.

        Args:
            file_path: Path to the script file

        Returns:
            ScriptInfoResult: detected type, icon, context params and the
            execution command; failure carries the error.
        """
        if not file_path:
            return ScriptInfoResult(
                success=False, error="File path cannot be None or empty"
            )

        script_type = cls.detect_type(file_path)
        context_params = cls.get_context_params(script_type)

        try:
            command = cls._build_command(script_type, file_path, context_params)
        except OSError as e:
            return ScriptInfoResult(
                success=False,
                script_path=file_path,
                script_type=script_type,
                error=f"Could not resolve script path: {e}",
            )

        return ScriptInfoResult(
            success=True,
            message=f"Detected {script_type} script",
            script_path=file_path,
            script_type=script_type,
            extension=Path(file_path).suffix.lower(),
            default_icon=cls.get_default_icon(script_type),
            context_params=context_params,
            command=command,
        )

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    @classmethod
    def _resolve_python_interpreter(cls) -> str | None:
        """Return the first configured interpreter meeting the minimum version."""
        command_runner = CommandRunnerService()

        for cmd in ScriptConfig.PYTHON_INTERPRETERS:
            try:
                if not command_runner.check_command_available(cmd).is_available:
                    continue
                result = command_runner.run([cmd, "--version"])
                if result.returncode != 0 or not result.stdout.strip():
                    continue
                version = result.stdout.strip().split()[1]
                version_parts = [int(x) for x in version.split(".")]
            except (CommandServiceError, IndexError, ValueError) as e:
                logging.getLogger(__name__).warning(
                    f"Failed to probe Python interpreter {cmd}: {e}"
                )
                continue

            if version_parts >= ScriptConfig.MINIMUM_PYTHON_VERSION:
                python_exe = shutil.which(cmd)
                if python_exe:
                    return python_exe

        return None

    @classmethod
    def _build_command(
        cls, script_type: str, script_path: str, context_params: str
    ) -> str:
        """
        Build the execution command for a script type.

        Raises:
            OSError: If the script path cannot be resolved to an absolute path.
        """
        script_abs_path = os.path.abspath(script_path)

        if script_type == ScriptType.PYTHON:
            python_exe = cls._resolve_python_interpreter()
            if python_exe:
                return f'"{python_exe}" "{script_abs_path}" "{context_params}"'
            # Fallback: try py launcher directly
            return (
                f"{ScriptConfig.PYTHON_LAUNCHER_FALLBACK} "
                f'"{script_abs_path}" "{context_params}"'
            )

        if script_type == ScriptType.POWERSHELL:
            return (
                f"{ScriptConfig.POWERSHELL_COMMAND_TEMPLATE} "
                f'"{script_abs_path}" "{context_params}"'
            )

        # Batch, executable, and unknown types are executed directly
        return f'"{script_abs_path}" "{context_params}"'
