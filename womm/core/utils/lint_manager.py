#!/usr/bin/env python3
"""
Linting manager for WOMM projects.
Centralizes linting logic and provides structured results.
Refactored to use modular utilities and follow architectural patterns.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

from ..tools.file_scanner import FileScanner
from ..tools.python_linting import PythonLintingTools
from ..ui.progress import create_spinner_with_status
from .results import BaseResult

if TYPE_CHECKING:
    from ..tools.lint_utils import ToolResult


@dataclass
class LintSummary(BaseResult):
    """Summary of all linting operations."""

    total_files: int = 0
    total_issues: int = 0
    total_fixed: int = 0
    tool_results: Dict[str, "ToolResult"] = field(default_factory=dict)
    scan_summary: Optional[dict] = None


class LintManager:
    """
    Manages linting operations for different languages and tools.
    Refactored to use modular utilities and follow architectural patterns.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize lint manager.

        Args:
            project_root: Root directory of the project (defaults to current directory)
        """
        self.project_root = project_root or Path.cwd()
        self.file_scanner = FileScanner()
        self.python_tools = PythonLintingTools()

    def check_python_code(
        self,
        target_paths: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
    ) -> LintSummary:
        """
        Run Python linting tools in check mode.

        Args:
            target_paths: Specific paths to check (if None, scan entire project)
            tools: Specific tools to run (if None, run all available)

        Returns:
            LintSummary: Summary of linting results
        """
        with create_spinner_with_status("🔍 Scanning Python files...") as (
            progress,
            task,
        ):
            # Get files to check
            python_files = self._get_target_files(target_paths)
            if not python_files:
                return LintSummary(
                    success=False, message="No Python files found to check"
                )

            scan_summary = self.file_scanner.get_scan_summary(python_files)
            progress.update(task, status=f"📊 Found {len(python_files)} Python files")

        # Convert Path objects to strings for tools
        target_dirs = [str(f) for f in python_files]

        with create_spinner_with_status("🔧 Running linting tools...") as (
            progress,
            task,
        ):
            tool_results = self.python_tools.check_python_code(
                target_dirs=target_dirs, cwd=self.project_root, tools=tools
            )

            progress.update(task, status="✅ Linting complete")

        # Calculate totals
        total_issues = sum(result.issues_found for result in tool_results.values())

        summary = LintSummary(
            success=all(result.success for result in tool_results.values()),
            message=f"Checked {len(python_files)} files with {len(tool_results)} tools",
            total_files=len(python_files),
            total_issues=total_issues,
            tool_results=tool_results,
            scan_summary=scan_summary,
        )

        self._display_check_results(summary)
        return summary

    def fix_python_code(
        self,
        target_paths: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
    ) -> LintSummary:
        """
        Run Python linting tools in fix mode.

        Args:
            target_paths: Specific paths to fix (if None, scan entire project)
            tools: Specific tools to run (if None, run all available fixable tools)

        Returns:
            LintSummary: Summary of fixing results
        """
        with create_spinner_with_status("🔍 Scanning Python files...") as (
            progress,
            task,
        ):
            # Get files to fix
            python_files = self._get_target_files(target_paths)
            if not python_files:
                return LintSummary(
                    success=False, message="No Python files found to fix"
                )

            scan_summary = self.file_scanner.get_scan_summary(python_files)
            progress.update(task, status=f"📊 Found {len(python_files)} Python files")

        # Convert Path objects to strings for tools
        target_dirs = [str(f) for f in python_files]

        with create_spinner_with_status("🔧 Running fixing tools...") as (
            progress,
            task,
        ):
            tool_results = self.python_tools.fix_python_code(
                target_dirs=target_dirs, cwd=self.project_root, tools=tools
            )

            progress.update(task, status="✅ Fixing complete")

        # Calculate totals
        total_fixed = sum(result.fixed_issues for result in tool_results.values())

        summary = LintSummary(
            success=all(result.success for result in tool_results.values()),
            message=f"Processed {len(python_files)} files with {len(tool_results)} tools",
            total_files=len(python_files),
            total_fixed=total_fixed,
            tool_results=tool_results,
            scan_summary=scan_summary,
        )

        self._display_fix_results(summary)
        return summary

    def get_tool_status(self) -> dict:
        """
        Get status of all available linting tools.

        Returns:
            dict: Tool availability and version information
        """
        return self.python_tools.get_tool_summary()

    def _get_target_files(self, target_paths: Optional[List[str]]) -> List[Path]:
        """
        Get list of Python files to process.

        Args:
            target_paths: Specific paths to check (if None, scan entire project)

        Returns:
            List[Path]: List of Python files to process
        """
        if not target_paths:
            # Scan entire project
            return self.file_scanner.get_project_python_files(self.project_root)

        # Process specific paths
        python_files = []
        for path_str in target_paths:
            path = Path(path_str)
            # Don't modify the path if it's already absolute
            # If it's relative, resolve it from current working directory, not project_root
            if not path.is_absolute():
                path = Path.cwd() / path

            python_files.extend(
                self.file_scanner.find_python_files(path, recursive=True)
            )

        return python_files

    def _display_check_results(self, summary: LintSummary):
        """Display check results to user."""
        from ..ui.lint import display_lint_summary

        display_lint_summary(summary, mode="check")

    def _display_fix_results(self, summary: LintSummary):
        """Display fix results to user."""
        from ..ui.lint import display_lint_summary

        display_lint_summary(summary, mode="fix")
