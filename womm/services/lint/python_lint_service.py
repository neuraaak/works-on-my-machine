#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PYTHON LINTING SERVICE - Python Linting Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Python Linting Service - Singleton service for Python-specific linting.

Handles ruff, black, isort, and bandit with their specific configurations.
Provides comprehensive Python linting capabilities with structured results.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.lint import (
    LintServiceError,
    ToolAvailabilityServiceError,
    ToolExecutionServiceError,
)
from ...shared.configs.lint.python_linting_config import PythonLintingConfig
from ...shared.result_models import ToolResult
from .core_service import LintService

# ///////////////////////////////////////////////////////////////
# PYTHON LINTING SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class PythonLintService:
    """Singleton service for Python-specific linting tools (ruff, black, isort, bandit)."""

    _instance: ClassVar[PythonLintService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> PythonLintService:
        """Create or return the singleton instance.

        Returns:
            PythonLintingService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize Python linting service (only once)."""
        if PythonLintService._initialized:
            return

        self.logger = logging.getLogger(__name__)
        self.lint_service = LintService()
        self._available_tools: dict[str, bool] | None = None
        PythonLintService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def get_available_tools(self) -> dict[str, bool]:
        """Get dictionary of available Python linting tools.

        Returns:
            dict[str, bool]: Tool name -> availability status

        Raises:
            LintServiceError: If tool availability check fails
        """
        try:
            if self._available_tools is None:
                self._available_tools = {}
                for tool_name in PythonLintingConfig.TOOLS_CONFIG:
                    try:
                        self._available_tools[tool_name] = (
                            self.lint_service.check_tool_available(tool_name)
                        )
                        if self._available_tools[tool_name]:
                            self.logger.debug(f"✓ {tool_name} is available")
                        else:
                            self.logger.debug(f"✗ {tool_name} is not available")
                    except Exception as e:
                        # Log but don't raise - this is a helper method
                        self.logger.warning(
                            f"Error checking availability for {tool_name}: {e}"
                        )
                        self._available_tools[tool_name] = False

            return self._available_tools

        except Exception as e:
            # Wrap unexpected external exceptions
            raise LintServiceError(
                message=f"Failed to get available tools: {e}",
                operation="get_available_tools",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def check_python_code(
        self, target_dirs: list[str], cwd: Path, tools: list[str] | None = None
    ) -> dict[str, ToolResult]:
        """Run Python linting tools in check mode.

        Args:
            target_dirs: List of directories/files to lint
            cwd: Working directory
            tools: Specific tools to run (if None, run all available)

        Returns:
            dict[str, ToolResult]: Tool name -> result mapping

        Raises:
            LintServiceError: If input validation fails
            ToolExecutionError: If tool execution fails
            ToolAvailabilityError: If required tools are not available
        """
        try:
            # Input validation
            if not target_dirs:
                raise LintServiceError(
                    message="Target directories cannot be empty",
                    operation="check_python_code",
                    details="No directories provided for Python code checking",
                )

            if not cwd or not cwd.exists():
                raise LintServiceError(
                    message="Working directory does not exist",
                    operation="check_python_code",
                    details=f"Invalid working directory: {cwd}",
                )

            available_tools = self.get_available_tools()
            tools_to_run = tools or [
                t for t, available in available_tools.items() if available
            ]

            if not tools_to_run:
                raise ToolAvailabilityServiceError(
                    message="No Python linting tools are available",
                    tool_name="python_linting_tools",
                    reason="No Python linting tools are available",
                    details="All configured tools are unavailable",
                )

            results: dict[str, ToolResult] = {}
            for tool_name in tools_to_run:
                if not available_tools.get(tool_name, False):
                    self.logger.warning(f"Tool {tool_name} is not available, skipping")
                    continue

                config = PythonLintingConfig.TOOLS_CONFIG[tool_name]
                try:
                    result = self.lint_service.run_tool_check(
                        tool_name=tool_name,
                        args=config["check_args"],
                        target_dirs=target_dirs,
                        cwd=cwd,
                        json_output=config["json_support"],
                    )
                    results[tool_name] = result
                    self.logger.debug(f"✓ {tool_name} check completed")
                except (LintServiceError, ToolExecutionServiceError):
                    # Re-raise specialized exceptions as-is
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise ToolExecutionServiceError(
                        message=f"Failed to run {tool_name}: {e}",
                        tool_name=tool_name,
                        operation="check",
                        reason=f"Failed to run {tool_name}: {e}",
                        details=f"Exception type: {type(e).__name__}, Tool: {tool_name}",
                    ) from e

            return results

        except (
            LintServiceError,
            ToolExecutionServiceError,
            ToolAvailabilityServiceError,
        ):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise LintServiceError(
                message=f"Unexpected error during Python code checking: {e}",
                operation="check_python_code",
                details=f"Exception type: {type(e).__name__}, Target dirs: {target_dirs}",
            ) from e

    def fix_python_code(
        self, target_dirs: list[str], cwd: Path, tools: list[str] | None = None
    ) -> dict[str, ToolResult]:
        """Run Python linting tools in fix mode.

        Args:
            target_dirs: List of directories/files to fix
            cwd: Working directory
            tools: Specific tools to run (if None, run all available fixable tools)

        Returns:
            dict[str, ToolResult]: Tool name -> result mapping

        Raises:
            LintServiceError: If input validation fails
            ToolExecutionError: If tool execution fails
            ToolAvailabilityError: If required tools are not available
        """
        try:
            # Input validation
            if not target_dirs:
                raise LintServiceError(
                    message="Target directories cannot be empty",
                    operation="fix_python_code",
                    details="No directories provided for Python code fixing",
                )

            if not cwd or not cwd.exists():
                raise LintServiceError(
                    message="Working directory does not exist",
                    operation="fix_python_code",
                    details=f"Invalid working directory: {cwd}",
                )

            available_tools = self.get_available_tools()
            fixable_tools = [
                t
                for t, config in PythonLintingConfig.TOOLS_CONFIG.items()
                if config["fix_args"] or t in PythonLintingConfig.FIXABLE_TOOLS
            ]
            tools_to_run = tools or [
                t for t in fixable_tools if available_tools.get(t, False)
            ]

            if not tools_to_run:
                raise ToolAvailabilityServiceError(
                    message="No fixable Python linting tools are available",
                    tool_name="python_linting_tools",
                    reason="No fixable Python linting tools are available",
                    details="All configured fixable tools are unavailable",
                )

            results: dict[str, ToolResult] = {}
            for tool_name in tools_to_run:
                if not available_tools.get(tool_name, False):
                    self.logger.warning(f"Tool {tool_name} is not available, skipping")
                    continue

                config = PythonLintingConfig.TOOLS_CONFIG[tool_name]
                fix_args = config["fix_args"]

                # For tools that fix by default (black, isort), use empty args
                if not fix_args and tool_name in PythonLintingConfig.FIXABLE_TOOLS:
                    fix_args = []

                if tool_name == "bandit":
                    # Bandit doesn't have fix mode, skip
                    self.logger.info(f"Skipping {tool_name} - no fix mode available")
                    continue

                try:
                    result = self.lint_service.run_tool_fix(
                        tool_name=tool_name,
                        args=fix_args,
                        target_dirs=target_dirs,
                        cwd=cwd,
                    )
                    results[tool_name] = result
                    self.logger.debug(f"✓ {tool_name} fix completed")
                except (LintServiceError, ToolExecutionServiceError):
                    # Re-raise specialized exceptions as-is
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise ToolExecutionServiceError(
                        message=f"Failed to run {tool_name}: {e}",
                        tool_name=tool_name,
                        operation="fix",
                        reason=f"Failed to run {tool_name}: {e}",
                        details=f"Exception type: {type(e).__name__}, Tool: {tool_name}",
                    ) from e

            return results

        except (
            LintServiceError,
            ToolExecutionServiceError,
            ToolAvailabilityServiceError,
        ):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise LintServiceError(
                message=f"Unexpected error during Python code fixing: {e}",
                operation="fix_python_code",
                details=f"Exception type: {type(e).__name__}, Target dirs: {target_dirs}",
            ) from e

    def get_tool_summary(self) -> dict[str, str]:
        """Get summary of tool availability and versions.

        Returns:
            dict[str, str]: Tool name -> status/version string

        Raises:
            LintServiceError: If tool summary generation fails
        """
        try:
            available_tools = self.get_available_tools()
            summary: dict[str, str] = {}

            for tool_name, is_available in available_tools.items():
                if is_available:
                    try:
                        version = self.lint_service.get_tool_version(tool_name)
                        summary[tool_name] = (
                            f"Available: {version}"
                            if version
                            else "Available (version unknown)"
                        )
                    except Exception as e:
                        # Log but don't raise - this is a helper method
                        self.logger.warning(
                            f"Error getting version for {tool_name}: {e}"
                        )
                        summary[tool_name] = "Available (version unknown)"
                else:
                    summary[tool_name] = "Not available"

            return summary

        except Exception as e:
            # Wrap unexpected external exceptions
            raise LintServiceError(
                message=f"Failed to get tool summary: {e}",
                operation="get_tool_summary",
                details=f"Exception type: {type(e).__name__}",
            ) from e
