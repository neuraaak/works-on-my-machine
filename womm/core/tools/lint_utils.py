#!/usr/bin/env python3
"""
Lint Utils - Common utility functions for linting operations.
Pure utility functions without UI - used by LintManager.
Handles generic tool execution and result processing.
"""

import json
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ..utils.results import BaseResult


@dataclass
class ToolResult(BaseResult):
    """Result of a tool execution."""

    tool_name: str = ""
    files_checked: int = 0
    issues_found: int = 0
    fixed_issues: int = 0
    data: object = None


def run_tool_check(
    tool_name: str,
    args: List[str],
    target_dirs: List[str],
    cwd: Path,
    json_output: bool = False,
) -> ToolResult:
    """
    Run a linting tool in check mode.

    Args:
        tool_name: Name of the tool (ruff, black, isort, etc.)
        args: Additional arguments for the tool
        target_dirs: List of directories/files to process
        cwd: Working directory
        json_output: Whether to parse JSON output

    Returns:
        ToolResult: Result of the tool execution
    """
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

    full_command = [tool_name] + args + relative_targets

    try:
        result = subprocess.run(
            full_command,
            cwd=str(cwd),  # Convert Path to string
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        # Parse output
        text = result.stdout or result.stderr or ""
        issues = 0
        parsed_data = None

        # Try to parse JSON if requested and available
        if json_output and result.stdout:
            try:
                parsed_data = json.loads(result.stdout)
                if isinstance(parsed_data, list):
                    issues = len(parsed_data)
                elif isinstance(parsed_data, dict):
                    issues = len(parsed_data.get("results", []))
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logging.debug(f"Failed to parse {tool_name} JSON output: {e}")
                parsed_data = None

        # Count issues from text output if no JSON
        if not json_output and result.returncode != 0 and text:
            # Simple heuristic: count lines with ":" which usually indicate issues
            issues = sum(
                1 for line in text.splitlines() if ":" in line and line.strip()
            )

        return ToolResult(
            success=result.returncode == 0,
            tool_name=tool_name,
            message=text or f"{tool_name} check completed",
            files_checked=len(target_dirs),
            issues_found=issues,
            data=parsed_data,
        )

    except subprocess.TimeoutExpired:
        return ToolResult(
            success=False,
            tool_name=tool_name,
            message=f"{tool_name} timed out after 5 minutes",
            files_checked=len(target_dirs),
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            tool_name=tool_name,
            message=f"Failed to execute {tool_name}: {str(exc)}",
            files_checked=len(target_dirs),
        )


def run_tool_fix(
    tool_name: str, args: List[str], target_dirs: List[str], cwd: Path
) -> ToolResult:
    """
    Run a linting tool in fix mode.

    Args:
        tool_name: Name of the tool (ruff, black, isort, etc.)
        args: Additional arguments for the tool (should include --fix or equivalent)
        target_dirs: List of directories/files to process
        cwd: Working directory

    Returns:
        ToolResult: Result of the tool execution
    """
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

    full_command = [tool_name] + args + relative_targets

    try:
        result = subprocess.run(
            full_command,
            cwd=str(cwd),  # Convert Path to string
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        text = result.stdout or result.stderr or ""

        # For fix operations, we assume all found issues were fixed if successful
        fixed_issues = 0
        if result.returncode == 0 and text:
            # Try to extract number of fixed issues from output
            # This is tool-specific and might need refinement
            lines = text.splitlines()
            for line in lines:
                if "fixed" in line.lower() or "formatted" in line.lower():
                    # Try to extract numbers from the line
                    import re

                    numbers = re.findall(r"\d+", line)
                    if numbers:
                        fixed_issues = int(numbers[0])
                        break

        return ToolResult(
            success=result.returncode == 0,
            tool_name=tool_name,
            message=text or f"{tool_name} fix completed",
            files_checked=len(target_dirs),
            fixed_issues=fixed_issues,
        )

    except subprocess.TimeoutExpired:
        return ToolResult(
            success=False,
            tool_name=tool_name,
            message=f"{tool_name} timed out after 5 minutes",
            files_checked=len(target_dirs),
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            tool_name=tool_name,
            message=f"Failed to execute {tool_name}: {str(exc)}",
            files_checked=len(target_dirs),
        )


def check_tool_availability(tool_name: str) -> bool:
    """
    Check if a linting tool is available.

    Args:
        tool_name: Name of the tool to check

    Returns:
        bool: True if tool is available, False otherwise
    """
    import shutil
    import subprocess

    try:
        # First check if command exists in PATH
        if not shutil.which(tool_name):
            return False

        # Try to run --version with a timeout
        result = subprocess.run(
            [tool_name, "--version"],
            capture_output=True,
            text=True,
            timeout=5,  # 5 second timeout
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
        return False
    except Exception:
        return False


def get_tool_version(tool_name: str) -> Optional[str]:
    """
    Get version of a linting tool.

    Args:
        tool_name: Name of the tool

    Returns:
        Optional[str]: Version string if available, None otherwise
    """
    import subprocess

    try:
        result = subprocess.run(
            [tool_name, "--version"],
            capture_output=True,
            text=True,
            timeout=5,  # 5 second timeout
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError) as exc:
        logging.debug(f"Failed to get {tool_name} version: {exc}")
    except Exception as exc:
        logging.debug(f"Failed to get {tool_name} version: {exc}")

    return None
