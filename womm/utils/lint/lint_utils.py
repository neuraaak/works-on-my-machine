#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# LINT UTILS - Pure Linting Utility Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for linting operations.

This module contains stateless utility functions for:
- Lint output parsing
- Result validation
- Tool detection and version extraction
- Exporting lint results to JSON
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import shutil
from datetime import datetime
from pathlib import Path

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.lint import (
    LintServiceError,
    ToolAvailabilityServiceError,
    ToolExecutionServiceError,
)
from ...services import CommandRunnerService
from ...shared.results.lint_results import ToolResult

# ///////////////////////////////////////////////////////////////
# TOOL DETECTION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def check_tool_availability(
    tool_name: str, command_runner: CommandRunnerService
) -> bool:
    """Check if a linting tool is available.

    Args:
        tool_name: Name of the tool to check
        command_runner: CommandRunnerService instance

    Returns:
        bool: True if tool is available, False otherwise
    """
    try:
        if not tool_name:
            return False

        # First check if command exists in PATH
        if not shutil.which(tool_name):
            return False

        # Try to run --version with a timeout
        result = command_runner.run_silent(
            [tool_name, "--version"],
        )

        return bool(result)

    except Exception:
        return False


def get_tool_version(tool_name: str, command_runner: CommandRunnerService) -> str:
    """Get version of a linting tool.

    Args:
        tool_name: Name of the tool
        command_runner: CommandRunnerService instance

    Returns:
        str: Version string or empty string if not available

    Raises:
        ToolAvailabilityError: If tool is not available
        ToolExecutionError: If version check fails
    """
    try:
        if not tool_name:
            raise ToolAvailabilityServiceError(
                message="Tool name cannot be empty",
                tool_name="",
                details="Empty tool name provided for version check",
            )

        # Check if tool is available first
        if not check_tool_availability(tool_name, command_runner):
            raise ToolAvailabilityServiceError(
                message=f"Tool '{tool_name}' not available",
                tool_name=tool_name,
                details=f"Tool '{tool_name}' not available in system PATH",
            )

        # Get version
        result = command_runner.run_silent(
            [tool_name, "--version"],
        )

        if not bool(result):
            raise ToolExecutionServiceError(
                message=f"Version check failed for {tool_name}",
                tool_name=tool_name,
                operation="version_check",
                details=f"Command output: {result.stderr or result.stdout}",
            )

        # Extract version from output
        output = result.stdout.strip()
        if output:
            # Special handling for isort which has ASCII art in output
            if tool_name == "isort":
                # Look for "VERSION X.X.X" line
                for line in output.split("\n"):
                    if "VERSION" in line.upper():
                        return line.strip()

            # Default: take first line which usually contains version
            first_line = output.split("\n")[0]
            return first_line

        return ""

    except (ToolAvailabilityServiceError, ToolExecutionServiceError):
        raise
    except Exception as e:
        raise LintServiceError(
            message=f"Unexpected error during tool version check: {e}",
            operation="get_tool_version",
            details=f"Exception type: {type(e).__name__}, Tool: {tool_name}",
        ) from e


# ///////////////////////////////////////////////////////////////
# OUTPUT PARSING FUNCTIONS
# ///////////////////////////////////////////////////////////////


def parse_lint_output(output: str, tool_name: str) -> dict[str, object]:
    """Parse linting tool output into structured format.

    Args:
        output: Raw output from linting tool
        tool_name: Name of the tool that generated the output

    Returns:
        dict: Parsed output with issues and metadata

    Raises:
        LintValidationError: If output parsing fails
    """
    try:
        if not output:
            return {
                "issues": [],
                "metadata": {"tool": tool_name, "total_issues": 0},
            }

        # Try to parse as JSON first
        try:
            data = json.loads(output)
            if isinstance(data, list):
                return {
                    "issues": data,
                    "metadata": {"tool": tool_name, "total_issues": len(data)},
                }
            elif isinstance(data, dict):
                issues = data.get("results", [])
                return {
                    "issues": issues,
                    "metadata": {"tool": tool_name, "total_issues": len(issues)},
                }
        except json.JSONDecodeError:
            pass

        # Parse as text output
        lines = output.splitlines()
        issues = []
        for line in lines:
            stripped_line = line.strip()
            if stripped_line and ":" in stripped_line:
                parts = stripped_line.split(":", 2)
                if len(parts) >= 3:
                    issues.append(
                        {
                            "file": parts[0],
                            "line": int(parts[1]) if parts[1].isdigit() else 0,
                            "message": parts[2],
                        }
                    )

        return {
            "issues": issues,
            "metadata": {"tool": tool_name, "total_issues": len(issues)},
        }

    except Exception as e:
        raise ValidationServiceError(
            message=f"Failed to parse {tool_name} output: {e}",
            validation_type="output_parsing",
            file_path="output",
            details=f"Raw output: {output[:200]}...",
        ) from e


# ///////////////////////////////////////////////////////////////
# VALIDATION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def validate_lint_result(result: ToolResult) -> bool:
    """Validate a linting tool result.

    Args:
        result: ToolResult to validate

    Returns:
        bool: True if result is valid

    Raises:
        LintValidationError: If result validation fails
    """
    try:
        if not result:
            raise ValidationServiceError(
                message="Tool result is None or empty",
                validation_type="result_validation",
                file_path="result",
                details="No result provided for validation",
            )

        if not hasattr(result, "tool_name") or not result.tool_name:
            raise ValidationServiceError(
                message="Tool result missing tool name",
                validation_type="result_validation",
                file_path="result",
                details="ToolResult must have a valid tool_name attribute",
            )
        if not hasattr(result, "success"):
            raise ValidationServiceError(
                message="Tool result missing success status",
                validation_type="result_validation",
                file_path="result",
                details="ToolResult must have a valid success attribute",
            )
        return True

    except ValidationServiceError:
        raise
    except Exception as e:
        raise ValidationServiceError(
            message=f"Unexpected error during result validation: {e}",
            validation_type="result_validation",
            file_path="result",
            details=f"Exception type: {type(e).__name__}",
        ) from e


# ///////////////////////////////////////////////////////////////
# EXPORT FUNCTIONS
# ///////////////////////////////////////////////////////////////


def export_lint_results_to_json(
    tool_results: dict[str, ToolResult],
    output_dir: Path,
    mode: str = "check",
) -> list[Path]:
    """Export linting tool results to JSON files.

    Args:
        tool_results: Results from linting tools
        output_dir: Directory to save output files
        mode: Operation mode ("check" or "fix")

    Returns:
        list[Path]: List of paths to exported JSON files

    Raises:
        LintServiceError: If export fails
    """
    try:
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        exported_files: list[Path] = []

        for tool_name, result in tool_results.items():
            # Create filename with tool name, mode, and timestamp
            filename = f"{tool_name}_{mode}_{timestamp}.json"
            filepath = output_dir / filename

            # Prepare output data
            output_data = {
                "tool": tool_name,
                "mode": mode,
                "timestamp": datetime.now().isoformat(),
                "success": result.success,
                "files_checked": result.files_checked,
                "issues_found": getattr(result, "issues_found", 0),
                "fixed_issues": getattr(result, "fixed_issues", 0),
                "message": result.message,
                "data": result.data,
                "raw_result": {
                    "tool_name": result.tool_name,
                    "success": result.success,
                    "message": result.message,
                    "files_checked": result.files_checked,
                    "issues_found": getattr(result, "issues_found", 0),
                    "fixed_issues": getattr(result, "fixed_issues", 0),
                    "data": result.data,
                },
            }

            # Write to file
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            exported_files.append(filepath)

        return exported_files

    except Exception as e:
        raise LintServiceError(
            message=f"Failed to export lint results to JSON: {e}",
            operation="export_results",
            details=f"Exception type: {type(e).__name__}",
        ) from e


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "check_tool_availability",
    "export_lint_results_to_json",
    "get_tool_version",
    "parse_lint_output",
    "validate_lint_result",
]
