#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# LINT UTILS - Linting Utility Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Lint Utils - Common utility functions for linting operations.

Pure utility functions without UI - used by LintManager.
Handles generic tool execution and result processing with proper error handling
and timeout management for various linting tools.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import re
import shutil
import subprocess
from pathlib import Path

# Local imports
from ....common.results import ToolResult
from ....common.security import run_silent

# Import specialized exceptions
from ...exceptions.lint import (
    LintUtilityError,
    LintValidationError,
    ToolAvailabilityError,
    ToolExecutionError,
)

# ///////////////////////////////////////////////////////////////
# LINTING UTILITIES
# ///////////////////////////////////////////////////////////////


def run_tool_check(
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
        LintUtilityError: If input validation fails
        ToolExecutionError: If tool execution fails or times out
        LintValidationError: If JSON parsing fails
    """
    try:
        # Input validation
        if not tool_name:
            raise LintUtilityError(
                message="Tool name cannot be empty",
                details="Empty tool name provided for linting operation",
            )

        if not target_dirs:
            raise LintUtilityError(
                message="Target directories cannot be empty",
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

        full_command = [tool_name] + args + relative_targets

        try:
            result = run_silent(
                full_command,
                cwd=str(cwd),  # Convert Path to string
                timeout=300,  # 5 minute timeout
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
                        line = line.strip()
                        if line.startswith(("{", "[")):
                            json_started = True
                        if json_started:
                            json_lines.append(line)

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
                    # Seulement transformer les erreurs JSON qu'on comprend
                    raise LintValidationError(
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
                success=result.returncode == 0,
                tool_name=tool_name,
                message=text or f"{tool_name} check completed",
                files_checked=len(target_dirs),
                issues_found=issues,
                data=parsed_data,
            )

        except subprocess.TimeoutExpired as e:
            raise ToolExecutionError(
                tool_name=tool_name,
                operation="check",
                reason="Tool execution timed out after 5 minutes",
                details=f"Command: {' '.join(full_command)}",
            ) from e

        except subprocess.SubprocessError as e:
            raise ToolExecutionError(
                tool_name=tool_name,
                operation="check",
                reason=f"Tool execution failed: {e}",
                details=f"Command: {' '.join(full_command)}",
            ) from e

    except (LintUtilityError, ToolExecutionError, LintValidationError):
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise LintUtilityError(
            message=f"Unexpected error during tool check execution: {e}",
            details=f"Exception type: {type(e).__name__}, Tool: {tool_name}",
        ) from e


def run_tool_fix(
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
        LintUtilityError: If input validation fails
        ToolExecutionError: If tool execution fails or times out
    """
    try:
        # Input validation
        if not tool_name:
            raise LintUtilityError(
                message="Tool name cannot be empty",
                details="Empty tool name provided for fix operation",
            )

        if not target_dirs:
            raise LintUtilityError(
                message="Target directories cannot be empty",
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

        full_command = [tool_name] + args + relative_targets

        try:
            result = run_silent(
                full_command,
                cwd=str(cwd),  # Convert Path to string
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

        except subprocess.TimeoutExpired as e:
            raise ToolExecutionError(
                tool_name=tool_name,
                operation="fix",
                reason="Tool execution timed out after 5 minutes",
                details=f"Command: {' '.join(full_command)}",
            ) from e

        except subprocess.SubprocessError as e:
            raise ToolExecutionError(
                tool_name=tool_name,
                operation="fix",
                reason=f"Tool execution failed: {e}",
                details=f"Command: {' '.join(full_command)}",
            ) from e

    except (LintUtilityError, ToolExecutionError):
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise LintUtilityError(
            message=f"Unexpected error during tool fix execution: {e}",
            details=f"Exception type: {type(e).__name__}, Tool: {tool_name}",
        ) from e


def check_tool_availability(tool_name: str) -> bool:
    """Check if a linting tool is available.

    Args:
        tool_name: Name of the tool to check

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
        result = run_silent(
            [tool_name, "--version"],
            timeout=10,  # Short timeout for version check
        )

        return result.success

    except Exception:
        # Log but don't raise - this is a helper function
        return False


def get_tool_version(tool_name: str) -> str:
    """Get version of a linting tool.

    Args:
        tool_name: Name of the tool

    Returns:
        str: Version string or empty string if not available

    Raises:
        ToolAvailabilityError: If tool is not available
        ToolExecutionError: If version check fails
    """
    try:
        if not tool_name:
            raise ToolAvailabilityError(
                tool_name="",
                reason="Tool name cannot be empty",
                details="Empty tool name provided for version check",
            )

        # Check if tool is available first
        if not check_tool_availability(tool_name):
            raise ToolAvailabilityError(
                tool_name=tool_name,
                reason="Tool not found in PATH",
                details=f"Tool '{tool_name}' not available in system PATH",
            )

        # Get version
        result = run_silent(
            [tool_name, "--version"],
            timeout=10,  # Short timeout for version check
        )

        if not result.success:
            raise ToolExecutionError(
                tool_name=tool_name,
                operation="version_check",
                reason=f"Version check failed with return code {result.returncode}",
                details=f"Command output: {result.stderr or result.stdout}",
            )

        # Extract version from output
        output = result.stdout.strip()
        if output:
            # Take first line which usually contains version
            first_line = output.split("\n")[0]
            return first_line

        return ""

    except (ToolAvailabilityError, ToolExecutionError):
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise LintUtilityError(
            message=f"Unexpected error during tool version check: {e}",
            details=f"Exception type: {type(e).__name__}, Tool: {tool_name}",
        ) from e


def parse_lint_output(output: str, tool_name: str) -> dict:
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
            return {"issues": [], "metadata": {"tool": tool_name, "total_issues": 0}}

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
            # Not JSON, parse as text
            pass

        # Parse as text output
        lines = output.splitlines()
        issues = []
        for line in lines:
            line = line.strip()
            if line and ":" in line:
                # Simple parsing: assume format is "file:line:message"
                parts = line.split(":", 2)
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
        raise LintValidationError(
            validation_type="output_parsing",
            file_path="output",
            reason=f"Failed to parse {tool_name} output: {e}",
            details=f"Raw output: {output[:200]}...",
        ) from e


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
            raise LintValidationError(
                validation_type="result_validation",
                file_path="result",
                reason="Tool result is None or empty",
                details="No result provided for validation",
            )

        if not hasattr(result, "tool_name") or not result.tool_name:
            raise LintValidationError(
                validation_type="result_validation",
                file_path="result",
                reason="Tool result missing tool name",
                details="ToolResult must have a valid tool_name attribute",
            )

        if not hasattr(result, "success"):
            raise LintValidationError(
                validation_type="result_validation",
                file_path="result",
                reason="Tool result missing success status",
                details="ToolResult must have a valid success attribute",
            )

        return True

    except LintValidationError:
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise LintValidationError(
            validation_type="result_validation",
            file_path="result",
            reason=f"Unexpected error during result validation: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e
