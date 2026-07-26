#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# LINT SERVICE - Linting Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Lint Service - Singleton service for linting operations.

Handles linting tool execution, result parsing, and validation.
Provides comprehensive linting capabilities with structured results.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import logging
import re
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.common import CommandTimeoutError
from ...exceptions.lint import LintServiceError
from ...shared.results import CommandResult, ToolResult
from ...utils.lint import get_tool_version as get_tool_version_util
from ..common.command_runner_service import CommandRunnerService

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# LINT SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class LintService:
    """Singleton service for linting tool operations."""

    _instance: ClassVar[LintService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> LintService:
        """Create or return the singleton instance.

        Returns:
            LintService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize lint service (only once)."""
        if LintService._initialized:
            return

        self.logger = logging.getLogger(__name__)
        self.command_runner = CommandRunnerService()
        LintService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def check_tool_available(self, tool_name: str) -> bool:
        """Check if a linting tool is available.

        Uses the lightweight probe to centralize dependency checking.

        Args:
            tool_name: Name of the tool to check

        Returns:
            bool: True if tool is available, False otherwise
        """
        try:
            from ...utils.dependencies import probe

            return probe(tool_name, detect_version=False).available
        except Exception as e:
            self.logger.debug(f"Error checking tool availability for {tool_name}: {e}")
            return False

    def get_tool_version(self, tool_name: str) -> str:
        """Get version of a linting tool.

        First checks if tool is available via the probe (centralized),
        then gets version using command execution.

        Args:
            tool_name: Name of the tool

        Returns:
            str: Version string or empty string if not available

        Raises:
            LintServiceError: If the tool is unavailable or the version check fails
        """
        # First, check if tool is available via the probe
        # This centralizes dependency checking at service layer
        if not self.check_tool_available(tool_name):
            raise LintServiceError(
                operation="get_tool_version",
                reason=f"Tool '{tool_name}' not available",
                details=f"Tool '{tool_name}' not available in system PATH",
            )

        # Now get the version using the utility function
        try:
            return get_tool_version_util(tool_name, self.command_runner)
        except Exception as e:
            self.logger.error(f"Error getting tool version for {tool_name}: {e}")
            raise LintServiceError(
                operation="get_tool_version",
                reason=f"Version check failed for {tool_name}",
                details=str(e),
            ) from e

    def run_tool_check(
        self,
        tool_name: str,
        args: list[str],
        target_dirs: list[str],
        cwd: Path,
        json_output: bool = False,
    ) -> ToolResult:
        """Run a linting tool in check mode.

        Args:
            tool_name: Name of the tool (ruff, black, isort, etc.)
            args: Additional arguments for the tool
            target_dirs: List of directories/files to process
            cwd: Working directory
            json_output: Whether to parse JSON output

        Returns:
            ToolResult: Result of the tool execution

        Raises:
            LintServiceError: If input validation, tool execution or JSON
                parsing fails
        """
        cwd_path, full_command = self._build_command(
            tool_name, args, target_dirs, cwd, operation="run_tool_check"
        )
        result = self._run_command(full_command, cwd_path, "run_tool_check", tool_name)

        text = result.stdout or result.stderr or ""
        issues = 0
        parsed_data = None

        if json_output and result.stdout:
            parsed_data, issues = self._extract_json_payload(
                result.stdout, tool_name, "run_tool_check"
            )
        elif json_output:
            # No output means no issues found (common with bandit)
            parsed_data = {"results": []}

        # Count issues from text output if no JSON
        if not json_output and result.returncode != 0 and text:
            # Simple heuristic: count lines with ":" which usually indicate issues
            issues = sum(
                1 for line in text.splitlines() if ":" in line and line.strip()
            )

        return ToolResult(
            success=bool(result),
            tool_name=tool_name,
            message=text or f"{tool_name} check completed",
            files_checked=len(target_dirs),
            issues_found=issues,
            data=parsed_data,
        )

    def run_tool_fix(
        self,
        tool_name: str,
        args: list[str],
        target_dirs: list[str],
        cwd: Path,
    ) -> ToolResult:
        """Run a linting tool in fix mode.

        Args:
            tool_name: Name of the tool (ruff, black, isort, etc.)
            args: Additional arguments for the tool (should include --fix or equivalent)
            target_dirs: List of directories/files to process
            cwd: Working directory

        Returns:
            ToolResult: Result of the tool execution

        Raises:
            LintServiceError: If input validation or tool execution fails
        """
        cwd_path, full_command = self._build_command(
            tool_name, args, target_dirs, cwd, operation="run_tool_fix"
        )
        result = self._run_command(full_command, cwd_path, "run_tool_fix", tool_name)

        text = result.stdout or result.stderr or ""

        # For fix operations, we assume all found issues were fixed if successful
        fixed_issues = 0
        if bool(result) and text:
            # Try to extract number of fixed issues from output
            # This is tool-specific and might need refinement
            for line in text.splitlines():
                if "fixed" in line.lower() or "formatted" in line.lower():
                    # Try to extract numbers from the line
                    numbers = re.findall(r"\d+", line)
                    if numbers:
                        fixed_issues = int(numbers[0])
                        break

        return ToolResult(
            success=bool(result),
            tool_name=tool_name,
            message=text or f"{tool_name} fix completed",
            files_checked=len(target_dirs),
            fixed_issues=fixed_issues,
        )

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _build_command(
        self,
        tool_name: str,
        args: list[str],
        target_dirs: list[str],
        cwd: Path,
        operation: str,
    ) -> tuple[Path, list[str]]:
        """Validate the inputs and build the tool command line.

        Args:
            tool_name: Name of the tool
            args: Additional arguments for the tool
            target_dirs: List of directories/files to process
            cwd: Working directory
            operation: Calling operation, reported on failure

        Returns:
            tuple[Path, list[str]]: Working directory and full command

        Raises:
            LintServiceError: If the tool name or the target directories are empty
        """
        if not tool_name:
            raise LintServiceError(
                operation=operation,
                reason="Tool name cannot be empty",
            )

        if not target_dirs:
            raise LintServiceError(
                operation=operation,
                reason="Target directories cannot be empty",
            )

        # Convert absolute paths to relative paths from cwd
        cwd_path = Path(cwd)
        relative_targets = []
        for target in target_dirs:
            target_path = Path(target)
            try:
                relative_targets.append(str(target_path.relative_to(cwd_path)))
            except ValueError:
                # If path is not relative to cwd, use absolute path
                relative_targets.append(str(target_path))

        return cwd_path, [tool_name, *args, *relative_targets]

    def _run_command(
        self,
        full_command: list[str],
        cwd_path: Path,
        operation: str,
        tool_name: str,
    ) -> CommandResult:
        """Execute a tool command and normalize its failures.

        Args:
            full_command: Command to execute
            cwd_path: Working directory
            operation: Calling operation, reported on failure
            tool_name: Name of the tool, reported on failure

        Returns:
            CommandResult: Raw result of the execution

        Raises:
            LintServiceError: If the command times out or cannot be executed
        """
        try:
            return self.command_runner.run_silent(full_command, cwd=cwd_path)
        except CommandTimeoutError as e:
            raise LintServiceError(
                operation=operation,
                reason=f"{tool_name} execution timed out",
                details=f"Command: {' '.join(full_command)}",
            ) from e
        except Exception as e:
            raise LintServiceError(
                operation=operation,
                reason=f"{tool_name} execution failed: {e}",
                details=f"Command: {' '.join(full_command)}",
            ) from e

    def _extract_json_payload(
        self, stdout: str, tool_name: str, operation: str
    ) -> tuple[object, int]:
        """Extract the JSON payload from a tool's stdout.

        Tools such as bandit prepend log lines to their JSON output, so the
        payload starts at the first line opening a JSON document.

        Args:
            stdout: Raw standard output of the tool
            tool_name: Name of the tool, reported on failure
            operation: Calling operation, reported on failure

        Returns:
            tuple[object, int]: Parsed payload and number of issues found

        Raises:
            LintServiceError: If the payload is not valid JSON
        """
        json_lines = []
        json_started = False
        for line in stdout.strip().split("\n"):
            stripped_line = line.strip()
            if stripped_line.startswith(("{", "[")):
                json_started = True
            if json_started:
                json_lines.append(stripped_line)

        if not json_lines:
            # No valid JSON found, treat as no issues
            return {"results": []}, 0

        try:
            parsed_data = json.loads("\n".join(json_lines))
        except json.JSONDecodeError as e:
            raise LintServiceError(
                operation=operation,
                reason=f"Failed to parse {tool_name} JSON output: {e}",
                details=f"Raw output: {stdout[:200]}...",
            ) from e

        if isinstance(parsed_data, list):
            return parsed_data, len(parsed_data)
        if isinstance(parsed_data, dict):
            return parsed_data, len(parsed_data.get("results", []))
        return parsed_data, 0
