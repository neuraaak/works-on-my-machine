#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PYTHON LINTING TOOLS - Python-specific linting functionality.
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Python Linting Tools - Python-specific linting functionality.
Handles ruff, black, isort, bandit with their specific configurations.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path

# Local imports
from ....common.results import ToolResult
from ...exceptions.lint import (
    LintUtilityError,
    ToolAvailabilityError,
    ToolExecutionError,
)
from .lint_utils import check_tool_availability, run_tool_check, run_tool_fix


class PythonLintingTools:
    """Manages Python-specific linting tools (ruff, black, isort, bandit)."""

    TOOLS_CONFIG = {
        "ruff": {
            "check_args": ["check", "--no-fix", "--output-format", "json"],
            "fix_args": ["check", "--fix"],
            "json_support": True,
        },
        "black": {
            "check_args": ["--check", "--diff"],
            "fix_args": [],
            "json_support": False,
        },
        "isort": {
            "check_args": ["--check-only", "--diff"],
            "fix_args": [],
            "json_support": False,
        },
        "bandit": {
            "check_args": ["-r", "-f", "json"],
            "fix_args": [],  # bandit doesn't have fix mode
            "json_support": True,
        },
    }

    def __init__(self):
        """Initialize Python linting tools manager."""
        self._available_tools: dict[str, bool] | None = None
        self.logger = logging.getLogger(__name__)

    def get_available_tools(self) -> dict[str, bool]:
        """
        Get dictionary of available Python linting tools.

        Returns:
            Dict[str, bool]: Tool name -> availability status

        Raises:
            LintUtilityError: If tool availability check fails
        """
        try:
            if self._available_tools is None:
                self._available_tools = {}
                for tool_name in self.TOOLS_CONFIG:
                    try:
                        self._available_tools[tool_name] = check_tool_availability(
                            tool_name
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
            raise LintUtilityError(
                message=f"Failed to get available tools: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def check_python_code(
        self, target_dirs: list[str], cwd: Path, tools: list[str] | None = None
    ) -> dict[str, ToolResult]:
        """
        Run Python linting tools in check mode.

        Args:
            target_dirs: List of directories/files to lint
            cwd: Working directory
            tools: Specific tools to run (if None, run all available)

        Returns:
            Dict[str, ToolResult]: Tool name -> result mapping

        Raises:
            LintUtilityError: If input validation fails
            ToolExecutionError: If tool execution fails
        """
        try:
            # Input validation
            if not target_dirs:
                raise LintUtilityError(
                    message="Target directories cannot be empty",
                    details="No directories provided for Python code checking",
                )

            if not cwd or not cwd.exists():
                raise LintUtilityError(
                    message="Working directory does not exist",
                    details=f"Invalid working directory: {cwd}",
                )

            available_tools = self.get_available_tools()
            tools_to_run = tools or [
                t for t, available in available_tools.items() if available
            ]

            if not tools_to_run:
                raise ToolAvailabilityError(
                    tool_name="python_linting_tools",
                    reason="No Python linting tools are available",
                    details="All configured tools are unavailable",
                )

            results = {}
            for tool_name in tools_to_run:
                if not available_tools.get(tool_name, False):
                    self.logger.warning(f"Tool {tool_name} is not available, skipping")
                    continue

                config = self.TOOLS_CONFIG[tool_name]
                try:
                    result = run_tool_check(
                        tool_name=tool_name,
                        args=config["check_args"],
                        target_dirs=target_dirs,
                        cwd=cwd,
                        json_output=config["json_support"],
                    )
                    results[tool_name] = result
                    self.logger.debug(f"✓ {tool_name} check completed")
                except (LintUtilityError, ToolExecutionError):
                    # Re-raise specialized exceptions as-is
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise ToolExecutionError(
                        tool_name=tool_name,
                        operation="check",
                        reason=f"Failed to run {tool_name}: {e}",
                        details=f"Exception type: {type(e).__name__}, Tool: {tool_name}",
                    ) from e

            return results

        except (LintUtilityError, ToolExecutionError, ToolAvailabilityError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise LintUtilityError(
                message=f"Unexpected error during Python code checking: {e}",
                details=f"Exception type: {type(e).__name__}, Target dirs: {target_dirs}",
            ) from e

    def fix_python_code(
        self, target_dirs: list[str], cwd: Path, tools: list[str] | None = None
    ) -> dict[str, ToolResult]:
        """
        Run Python linting tools in fix mode.

        Args:
            target_dirs: List of directories/files to fix
            cwd: Working directory
            tools: Specific tools to run (if None, run all available fixable tools)

        Returns:
            Dict[str, ToolResult]: Tool name -> result mapping

        Raises:
            LintUtilityError: If input validation fails
            ToolExecutionError: If tool execution fails
        """
        try:
            # Input validation
            if not target_dirs:
                raise LintUtilityError(
                    message="Target directories cannot be empty",
                    details="No directories provided for Python code fixing",
                )

            if not cwd or not cwd.exists():
                raise LintUtilityError(
                    message="Working directory does not exist",
                    details=f"Invalid working directory: {cwd}",
                )

            available_tools = self.get_available_tools()
            fixable_tools = [
                t
                for t, config in self.TOOLS_CONFIG.items()
                if config["fix_args"]
                or t in ["black", "isort"]  # these tools fix by default
            ]
            tools_to_run = tools or [
                t for t in fixable_tools if available_tools.get(t, False)
            ]

            if not tools_to_run:
                raise ToolAvailabilityError(
                    tool_name="python_linting_tools",
                    reason="No fixable Python linting tools are available",
                    details="All configured fixable tools are unavailable",
                )

            results = {}
            for tool_name in tools_to_run:
                if not available_tools.get(tool_name, False):
                    self.logger.warning(f"Tool {tool_name} is not available, skipping")
                    continue

                config = self.TOOLS_CONFIG[tool_name]
                fix_args = config["fix_args"]

                # For tools that fix by default (black, isort), use empty args
                if not fix_args and tool_name in ["black", "isort"]:
                    fix_args = []

                if tool_name == "bandit":
                    # Bandit doesn't have fix mode, skip
                    self.logger.info(f"Skipping {tool_name} - no fix mode available")
                    continue

                try:
                    result = run_tool_fix(
                        tool_name=tool_name,
                        args=fix_args,
                        target_dirs=target_dirs,
                        cwd=cwd,
                    )
                    results[tool_name] = result
                    self.logger.debug(f"✓ {tool_name} fix completed")
                except (LintUtilityError, ToolExecutionError):
                    # Re-raise specialized exceptions as-is
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise ToolExecutionError(
                        tool_name=tool_name,
                        operation="fix",
                        reason=f"Failed to run {tool_name}: {e}",
                        details=f"Exception type: {type(e).__name__}, Tool: {tool_name}",
                    ) from e

            return results

        except (LintUtilityError, ToolExecutionError, ToolAvailabilityError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise LintUtilityError(
                message=f"Unexpected error during Python code fixing: {e}",
                details=f"Exception type: {type(e).__name__}, Target dirs: {target_dirs}",
            ) from e

    def get_tool_summary(self) -> dict[str, str]:
        """
        Get summary of tool availability and versions.

        Returns:
            Dict[str, str]: Tool name -> status/version string

        Raises:
            LintUtilityError: If tool summary generation fails
        """
        try:
            from ..cli_utils import get_tool_version

            available_tools = self.get_available_tools()
            summary = {}

            for tool_name, is_available in available_tools.items():
                if is_available:
                    try:
                        version = get_tool_version(tool_name)
                        summary[tool_name] = version or "Available (version unknown)"
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
            raise LintUtilityError(
                message=f"Failed to get tool summary: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e
