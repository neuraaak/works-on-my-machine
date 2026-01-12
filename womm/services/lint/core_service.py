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
from ...exceptions.common import TimeoutError, ValidationServiceError
from ...exceptions.lint import (
    LintServiceError,
    ToolAvailabilityServiceError,
    ToolExecutionServiceError,
)
from ...shared.result_models import ToolResult
from ...utils.lint import get_tool_version as get_tool_version_util
from ...utils.lint import parse_lint_output, validate_lint_result
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

        Uses DevToolsService to centralize dependency checking.

        Args:
            tool_name: Name of the tool to check

        Returns:
            bool: True if tool is available, False otherwise
        """
        try:
            # Import here to avoid circular imports
            from ..dependencies.devtools_dependencies_service import DevToolsService

            service = DevToolsService()
            result = service.check_tool_availability(tool_name)
            return result.is_available
        except Exception as e:
            self.logger.debug(f"Error checking tool availability for {tool_name}: {e}")
            return False

    def get_tool_version(self, tool_name: str) -> str:
        """Get version of a linting tool.

        First checks if tool is available via DevToolsService (centralized),
        then gets version using command execution.

        Args:
            tool_name: Name of the tool

        Returns:
            str: Version string or empty string if not available

        Raises:
            ToolAvailabilityError: If tool is not available
            ToolExecutionError: If version check fails
        """
        try:
            # First, check if tool is available via DevToolsService
            # This centralizes dependency checking at service layer
            if not self.check_tool_available(tool_name):
                raise ToolAvailabilityServiceError(
                    message=f"Tool '{tool_name}' not available",
                    tool_name=tool_name,
                    details=f"Tool '{tool_name}' not available in system PATH",
                )

            # Now get the version using the utility function
            return get_tool_version_util(tool_name, self.command_runner)

        except ToolAvailabilityServiceError:
            raise
        except Exception as e:
            self.logger.error(f"Error getting tool version for {tool_name}: {e}")
            raise ToolExecutionServiceError(
                message=f"Version check failed for {tool_name}",
                tool_name=tool_name,
                operation="version_check",
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
            LintServiceError: If input validation fails
            ToolExecutionError: If tool execution fails or times out
            LintValidationError: If JSON parsing fails
        """
        try:
            # Input validation
            if not tool_name:
                raise LintServiceError(
                    message="Tool name cannot be empty",
                    operation="run_tool_check",
                    details="Empty tool name provided for linting operation",
                )

            if not target_dirs:
                raise LintServiceError(
                    message="Target directories cannot be empty",
                    operation="run_tool_check",
                    details="Empty target directories list provided for linting operation",
                )

            # Convert absolute paths to relative paths from cwd
            cwd_path = Path(cwd)
            relative_targets = []
            for target in target_dirs:
                target_path = Path(target)
                try:
                    # Convert to relative path from cwd
                    relative_path = target_path.relative_to(cwd_path)
                    relative_targets.append(str(relative_path))
                except ValueError:
                    # If path is not relative to cwd, use absolute path
                    relative_targets.append(str(target_path))

            full_command = [tool_name, *args, *relative_targets]

            try:
                result = self.command_runner.run_silent(
                    full_command,
                    cwd=cwd_path,
                )

                # Parse output
                text = result.stdout or result.stderr or ""
                issues = 0
                parsed_data = None

                # Try to parse JSON if requested and available
                if json_output and result.stdout:
                    try:
                        # Filter out log lines that are not JSON (common with bandit)
                        stdout_lines = result.stdout.strip().split("\n")
                        json_lines = []
                        json_started = False

                        for line in stdout_lines:
                            stripped_line = line.strip()
                            if stripped_line.startswith(("{", "[")):
                                json_started = True
                            if json_started:
                                json_lines.append(stripped_line)

                        if json_lines:
                            json_content = "\n".join(json_lines)
                            parsed_data = json.loads(json_content)
                            if isinstance(parsed_data, list):
                                issues = len(parsed_data)
                            elif isinstance(parsed_data, dict):
                                issues = len(parsed_data.get("results", []))
                        else:
                            # No valid JSON found, treat as no issues
                            parsed_data = {"results": []}
                            issues = 0

                    except json.JSONDecodeError as e:
                        raise ValidationServiceError(
                            message=f"Failed to parse {tool_name} JSON output: {e}",
                            validation_type="json_parsing",
                            file_path=str(cwd),
                            reason=f"Failed to parse {tool_name} JSON output: {e}",
                            details=f"Raw output: {result.stdout[:200]}...",
                        ) from e
                elif json_output and not result.stdout:
                    # No output means no issues found (common with bandit)
                    parsed_data = {"results": []}
                    issues = 0

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

            except TimeoutError as e:
                raise ToolExecutionServiceError(
                    message="Tool execution timed out after 5 minutes",
                    tool_name=tool_name,
                    operation="check",
                    reason="Tool execution timed out after 5 minutes",
                    details=f"Command: {' '.join(full_command)}",
                ) from e
            except Exception as e:
                raise ToolExecutionServiceError(
                    message=f"Tool execution failed: {e}",
                    tool_name=tool_name,
                    operation="check",
                    reason=f"Tool execution failed: {e}",
                    details=f"Command: {' '.join(full_command)}",
                ) from e

        except (
            LintServiceError,
            ToolExecutionServiceError,
            ValidationServiceError,
        ):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise LintServiceError(
                message=f"Unexpected error during tool check execution: {e}",
                operation="run_tool_check",
                details=f"Exception type: {type(e).__name__}, Tool: {tool_name}",
            ) from e

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
            LintServiceError: If input validation fails
            ToolExecutionError: If tool execution fails or times out
        """
        try:
            # Input validation
            if not tool_name:
                raise LintServiceError(
                    message="Tool name cannot be empty",
                    operation="run_tool_fix",
                    details="Empty tool name provided for fix operation",
                )

            if not target_dirs:
                raise LintServiceError(
                    message="Target directories cannot be empty",
                    operation="run_tool_fix",
                    details="Empty target directories list provided for fix operation",
                )

            # Convert absolute paths to relative paths from cwd
            cwd_path = Path(cwd)
            relative_targets = []
            for target in target_dirs:
                target_path = Path(target)
                try:
                    # Convert to relative path from cwd
                    relative_path = target_path.relative_to(cwd_path)
                    relative_targets.append(str(relative_path))
                except ValueError:
                    # If path is not relative to cwd, use absolute path
                    relative_targets.append(str(target_path))

            full_command = [tool_name, *args, *relative_targets]

            try:
                result = self.command_runner.run_silent(
                    full_command,
                    cwd=cwd_path,
                )

                text = result.stdout or result.stderr or ""

                # For fix operations, we assume all found issues were fixed if successful
                fixed_issues = 0
                if bool(result) and text:
                    # Try to extract number of fixed issues from output
                    # This is tool-specific and might need refinement
                    lines = text.splitlines()
                    for line in lines:
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

            except TimeoutError as e:
                raise ToolExecutionServiceError(
                    message="Tool execution timed out after 5 minutes",
                    tool_name=tool_name,
                    operation="fix",
                    reason="Tool execution timed out after 5 minutes",
                    details=f"Command: {' '.join(full_command)}",
                ) from e
            except Exception as e:
                raise ToolExecutionServiceError(
                    message=f"Tool execution failed: {e}",
                    tool_name=tool_name,
                    operation="fix",
                    reason=f"Tool execution failed: {e}",
                    details=f"Command: {' '.join(full_command)}",
                ) from e

        except (LintServiceError, ToolExecutionServiceError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise LintServiceError(
                message=f"Unexpected error during tool fix execution: {e}",
                operation="run_tool_fix",
                details=f"Exception type: {type(e).__name__}, Tool: {tool_name}",
            ) from e

    def parse_output(self, output: str, tool_name: str) -> dict[str, object]:
        """Parse linting tool output into structured format.

        Args:
            output: Raw output from linting tool
            tool_name: Name of the tool that generated the output

        Returns:
            dict: Parsed output with issues and metadata

        Raises:
            LintValidationError: If output parsing fails
        """
        return parse_lint_output(output, tool_name)

    def validate_result(self, result: ToolResult) -> bool:
        """Validate a linting tool result.

        Args:
            result: ToolResult to validate

        Returns:
            bool: True if result is valid

        Raises:
            LintValidationError: If result validation fails
        """
        return validate_lint_result(result)
