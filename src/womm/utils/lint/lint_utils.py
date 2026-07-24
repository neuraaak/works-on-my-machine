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
import subprocess
from datetime import datetime
from pathlib import Path

# Local imports
from ...services import CommandRunnerService
from ...shared.results import ToolResult

# ///////////////////////////////////////////////////////////////
# TOOL DETECTION FUNCTIONS
# ///////////////////////////////////////////////////////////////


def get_tool_version(tool_name: str, command_runner: CommandRunnerService) -> str:
    """Get version of a linting tool.

    Args:
        tool_name: Name of the tool
        command_runner: CommandRunnerService instance

    Returns:
        str: Version string, or an empty string if the tool printed nothing

    Raises:
        ValueError: If the tool name is empty
        subprocess.CalledProcessError: If the version command fails
    """
    if not tool_name:
        raise ValueError("Tool name cannot be empty")

    command = [tool_name, "--version"]
    result = command_runner.run_silent(command)

    if not result:
        raise subprocess.CalledProcessError(
            result.returncode,
            command,
            output=result.stdout,
            stderr=result.stderr,
        )

    output = result.stdout.strip()
    if not output:
        return ""

    # Special handling for isort which has ASCII art in output
    if tool_name == "isort":
        # Look for "VERSION X.X.X" line
        for line in output.split("\n"):
            if "VERSION" in line.upper():
                return line.strip()

    # Default: take first line which usually contains version
    return output.split("\n")[0]


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
    """
    if not output:
        return {
            "issues": [],
            "metadata": {"tool": tool_name, "total_issues": 0},
        }

    # Try to parse as JSON first
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        pass
    else:
        if isinstance(data, list):
            return {
                "issues": data,
                "metadata": {"tool": tool_name, "total_issues": len(data)},
            }
        if isinstance(data, dict):
            issues = data.get("results", [])
            return {
                "issues": issues,
                "metadata": {"tool": tool_name, "total_issues": len(issues)},
            }

    # Parse as text output
    issues = []
    for line in output.splitlines():
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
        ValueError: If the result is missing or lacks a required attribute
    """
    if not result:
        raise ValueError("Tool result is None or empty")

    if not getattr(result, "tool_name", ""):
        raise ValueError("Tool result is missing a tool name")

    if not hasattr(result, "success"):
        raise ValueError("Tool result is missing a success status")

    return True


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
        OSError: If the output directory or a result file cannot be written
        TypeError: If a tool result holds non-serializable data
    """
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


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "export_lint_results_to_json",
    "get_tool_version",
    "parse_lint_output",
    "validate_lint_result",
]
