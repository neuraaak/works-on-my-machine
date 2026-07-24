#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PYTHON LINT INTERFACE - Python Linting Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Python Linting Interface for Works On My Machine.

Orchestrates PythonLintService and FileScannerService, and converts the lint
service exception into a result object. The interface owns no presentation:
rendering and exit codes belong to the command layer.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path
from typing import Any

# Local imports
from ...exceptions.lint import LintServiceError
from ...services import FileScannerService, PythonLintService
from ...shared.results.lint_results import LintSummaryResult, ToolStatusResult
from ...utils.lint import export_lint_results_to_json

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class PythonLintInterface:
    """Manages Python linting operations for different tools.

    Every public method returns a result object: a failure of the lint service
    is translated into ``success=False`` plus a message, never re-raised.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        """Initialize Python lint interface.

        Args:
            project_root: Root directory of the project (defaults to current directory)
        """
        self.project_root = project_root or Path.cwd()
        self._file_scanner: FileScannerService | None = None
        self._python_lint_service: PythonLintService | None = None

    @property
    def file_scanner(self) -> FileScannerService:
        """Lazy load FileScannerService when needed."""
        if self._file_scanner is None:
            self._file_scanner = FileScannerService()
        return self._file_scanner

    @property
    def python_lint_service(self) -> PythonLintService:
        """Lazy load PythonLintService when needed."""
        if self._python_lint_service is None:
            self._python_lint_service = PythonLintService()
        return self._python_lint_service

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def check_python_code(
        self,
        target_paths: list[str] | None = None,
        tools: list[str] | None = None,
        output_dir: str | None = None,
    ) -> LintSummaryResult:
        """Run Python linting tools in check mode.

        Args:
            target_paths: Specific paths to check (if None, scan entire project)
            tools: Specific tools to run (if None, run all available)
            output_dir: Output directory for detailed reports

        Returns:
            LintSummaryResult: Summary of the run; on failure, ``success`` is
                False and ``message`` carries the reason
        """
        return self._run("check", target_paths, tools, output_dir)

    def fix_python_code(
        self,
        target_paths: list[str] | None = None,
        tools: list[str] | None = None,
        output_dir: str | None = None,
    ) -> LintSummaryResult:
        """Run Python linting tools in fix mode.

        Args:
            target_paths: Specific paths to fix (if None, scan entire project)
            tools: Specific tools to run (if None, run all available fixable tools)
            output_dir: Output directory for detailed reports

        Returns:
            LintSummaryResult: Summary of the run; on failure, ``success`` is
                False and ``message`` carries the reason
        """
        return self._run("fix", target_paths, tools, output_dir)

    def get_tool_status(self) -> ToolStatusResult:
        """Get status of all available linting tools.

        Returns:
            ToolStatusResult: Tool availability and version information
        """
        return ToolStatusResult(
            success=True,
            message="Tool status retrieved successfully",
            tool_summary=self.python_lint_service.get_tool_summary(),
        )

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _run(
        self,
        mode: str,
        target_paths: list[str] | None,
        tools: list[str] | None,
        output_dir: str | None,
    ) -> LintSummaryResult:
        """Run the linting tools in check or fix mode.

        Args:
            mode: Either "check" or "fix"
            target_paths: Specific paths to process (if None, scan entire project)
            tools: Specific tools to run (if None, run all available)
            output_dir: Output directory for detailed reports

        Returns:
            LintSummaryResult: Summary of the run
        """
        python_files, scan_error = self._get_target_files(target_paths)
        if scan_error:
            return LintSummaryResult(success=False, message=scan_error)

        if not python_files:
            return LintSummaryResult(
                success=False, message=f"No Python files found to {mode}"
            )

        target_dirs = [str(f) for f in python_files]
        try:
            if mode == "check":
                tool_results = self.python_lint_service.check_python_code(
                    target_dirs=target_dirs, cwd=self.project_root, tools=tools
                )
            else:
                tool_results = self.python_lint_service.fix_python_code(
                    target_dirs=target_dirs, cwd=self.project_root, tools=tools
                )
        except LintServiceError as e:
            return LintSummaryResult(
                success=False,
                message=f"Failed to execute Python {mode} tools: {e}",
            )

        verb = "Checked" if mode == "check" else "Processed"
        summary = LintSummaryResult(
            success=all(result.success for result in tool_results.values()),
            message=f"{verb} {len(python_files)} files with {len(tool_results)} tools",
            total_files=len(python_files),
            total_issues=sum(r.issues_found for r in tool_results.values()),
            total_fixed=sum(r.fixed_issues for r in tool_results.values()),
            tool_results=tool_results,
            scan_summary=self._get_scan_summary(python_files),
        )

        # Generate output files if requested
        if output_dir:
            try:
                export_lint_results_to_json(tool_results, Path(output_dir), mode=mode)
            except (OSError, TypeError) as e:
                logger.warning(f"Failed to generate output files: {e}")

        return summary

    def _get_target_files(
        self, target_paths: list[str] | None
    ) -> tuple[list[Path], str]:
        """Collect the Python files to process.

        ``FileScannerService`` reports its failures through its result object,
        so no exception has to be handled here.

        Args:
            target_paths: Specific paths to scan (if None, scan entire project)

        Returns:
            tuple[list[Path], str]: Files found, and an error message that is
                empty when the scan succeeded
        """
        if not target_paths:
            # Scan entire project
            search_result = self.file_scanner.get_project_python_files(
                self.project_root
            )
            if not search_result.success:
                return [], f"Failed to scan project: {search_result.error}"
            return search_result.files_found or [], ""

        # Process specific paths
        python_files: list[Path] = []
        for path_str in target_paths:
            path = Path(path_str)
            # Don't modify the path if it's already absolute
            # If it's relative, resolve it from current working directory, not project_root
            if not path.is_absolute():
                path = Path.cwd() / path

            search_result = self.file_scanner.find_python_files(path, recursive=True)
            if not search_result.success:
                # Continue with other paths
                logger.warning(
                    f"Failed to find Python files in {path_str}: {search_result.error}"
                )
            elif search_result.files_found:
                python_files.extend(search_result.files_found)

        return python_files, ""

    def _get_scan_summary(self, python_files: list[Path]) -> dict[str, Any]:
        """Build the scan summary attached to the lint result.

        Args:
            python_files: Files that will be processed

        Returns:
            dict[str, Any]: Scan metadata, degraded to a file count if the
                scanner cannot produce a summary
        """
        scan_result = self.file_scanner.get_scan_summary(python_files)
        if not scan_result.success:
            logger.warning(f"Failed to get scan summary: {scan_result.error}")
            return {"total_files": len(python_files), "errors": []}

        return {
            "target_path": (
                str(scan_result.target_path) if scan_result.target_path else ""
            ),
            "total_files": scan_result.total_files,
            "file_extensions": scan_result.file_extensions or [],
            "excluded_dirs": scan_result.excluded_dirs or [],
            "scan_successful": scan_result.success,
        }
