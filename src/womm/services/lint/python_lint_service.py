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
from ...exceptions.lint import LintServiceError
from ...shared.configs.lint import PythonLintingConfig
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
        """
        if self._available_tools is None:
            self._available_tools = {}
            for tool_name in PythonLintingConfig.TOOLS_CONFIG:
                available = self.lint_service.check_tool_available(tool_name)
                self._available_tools[tool_name] = available
                if available:
                    self.logger.debug(f"✓ {tool_name} is available")
                else:
                    self.logger.debug(f"✗ {tool_name} is not available")

        return self._available_tools

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
            LintServiceError: If input validation fails, no tool is available,
                or a tool fails to run
        """
        available_tools = self._validate_run(target_dirs, cwd, "check_python_code")
        tools_to_run = tools or [
            t for t, available in available_tools.items() if available
        ]

        if not tools_to_run:
            raise LintServiceError(
                operation="check_python_code",
                reason="No Python linting tools are available",
                details="All configured tools are unavailable",
            )

        results: dict[str, ToolResult] = {}
        for tool_name in tools_to_run:
            if not available_tools.get(tool_name, False):
                self.logger.warning(f"Tool {tool_name} is not available, skipping")
                continue

            config = PythonLintingConfig.TOOLS_CONFIG[tool_name]
            check_args = config.get("check_args", [])
            if not isinstance(check_args, list):
                check_args = []
            json_support = config.get("json_support", False)
            if not isinstance(json_support, bool):
                json_support = False

            results[tool_name] = self.lint_service.run_tool_check(
                tool_name=tool_name,
                args=check_args,
                target_dirs=target_dirs,
                cwd=cwd,
                json_output=json_support,
            )
            self.logger.debug(f"✓ {tool_name} check completed")

        return results

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
            LintServiceError: If input validation fails, no fixable tool is
                available, or a tool fails to run
        """
        available_tools = self._validate_run(target_dirs, cwd, "fix_python_code")
        fixable_tools = [
            t
            for t, config in PythonLintingConfig.TOOLS_CONFIG.items()
            if config["fix_args"] or t in PythonLintingConfig.FIXABLE_TOOLS
        ]
        tools_to_run = tools or [
            t for t in fixable_tools if available_tools.get(t, False)
        ]

        if not tools_to_run:
            raise LintServiceError(
                operation="fix_python_code",
                reason="No fixable Python linting tools are available",
                details="All configured fixable tools are unavailable",
            )

        results: dict[str, ToolResult] = {}
        for tool_name in tools_to_run:
            if not available_tools.get(tool_name, False):
                self.logger.warning(f"Tool {tool_name} is not available, skipping")
                continue

            if tool_name == "bandit":
                # Bandit doesn't have fix mode, skip
                self.logger.info(f"Skipping {tool_name} - no fix mode available")
                continue

            config = PythonLintingConfig.TOOLS_CONFIG[tool_name]
            fix_args = config.get("fix_args", [])
            if not isinstance(fix_args, list):
                fix_args = []

            results[tool_name] = self.lint_service.run_tool_fix(
                tool_name=tool_name,
                args=fix_args,
                target_dirs=target_dirs,
                cwd=cwd,
            )
            self.logger.debug(f"✓ {tool_name} fix completed")

        return results

    def get_tool_summary(self) -> dict[str, str]:
        """Get summary of tool availability and versions.

        Returns:
            dict[str, str]: Tool name -> status/version string
        """
        summary: dict[str, str] = {}

        for tool_name, is_available in self.get_available_tools().items():
            if not is_available:
                summary[tool_name] = "Not available"
                continue

            try:
                version = self.lint_service.get_tool_version(tool_name)
            except LintServiceError as e:
                # Log but don't raise - a missing version is not fatal here
                self.logger.warning(f"Error getting version for {tool_name}: {e}")
                summary[tool_name] = "Available (version unknown)"
                continue

            summary[tool_name] = (
                f"Available: {version}" if version else "Available (version unknown)"
            )

        return summary

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _validate_run(
        self, target_dirs: list[str], cwd: Path, operation: str
    ) -> dict[str, bool]:
        """Validate the inputs shared by the check and fix runs.

        Args:
            target_dirs: List of directories/files to process
            cwd: Working directory
            operation: Calling operation, reported on failure

        Returns:
            dict[str, bool]: Tool name -> availability status

        Raises:
            LintServiceError: If the target directories are empty or the
                working directory does not exist
        """
        if not target_dirs:
            raise LintServiceError(
                operation=operation,
                reason="Target directories cannot be empty",
            )

        if not cwd or not cwd.exists():
            raise LintServiceError(
                operation=operation,
                reason="Working directory does not exist",
                details=f"Invalid working directory: {cwd}",
            )

        return self.get_available_tools()
