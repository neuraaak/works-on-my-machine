#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PYTHON LINT INTERFACE - Python Linting Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Python Linting Interface for Works On My Machine.

Handles Python code linting and fixing with integrated UI.
Provides comprehensive linting capabilities with structured results.

This interface orchestrates PythonLintService and FileScannerService
and converts service exceptions to interface exceptions following the MEF pattern.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path

from ...exceptions.common import ValidationServiceError
from ...exceptions.lint import (
    LintServiceError,
    PythonLintInterfaceError,
    ToolAvailabilityServiceError,
    ToolExecutionServiceError,
)
from ...services import FileScannerService, PythonLintService
from ...shared.results.lint_results import LintSummaryResult, ToolStatusResult

# Local imports
from ...ui.common.ezpl_bridge import ezprinter
from ...utils.lint import export_lint_results_to_json

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class PythonLintInterface:
    """
    Manages Python linting operations for different tools.

    This interface orchestrates PythonLintService and FileScannerService
    and converts service exceptions to interface exceptions following the MEF pattern.
    """

    def __init__(self, project_root: Path | None = None) -> None:
        """
        Initialize Python lint interface.

        Args:
            project_root: Root directory of the project (defaults to current directory)

        Raises:
            PythonLintInterfaceError: If interface initialization fails
        """
        try:
            # Input validation
            if project_root is not None and not isinstance(project_root, Path):
                raise PythonLintInterfaceError(
                    message="Project root must be a Path object",
                    details=f"Received type: {type(project_root).__name__}",
                )

            self.project_root = project_root or Path.cwd()

            # Initialize services
            try:
                self._file_scanner: FileScannerService | None = None
                self._python_lint_service: PythonLintService | None = None
            except Exception as e:
                raise PythonLintInterfaceError(
                    message=f"Failed to initialize services: {e}",
                    details=f"Exception type: {type(e).__name__}",
                ) from e

        except PythonLintInterfaceError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(
                f"Failed to initialize PythonLintInterface: {e}", exc_info=True
            )
            raise PythonLintInterfaceError(
                message=f"Python lint interface initialization failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

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
        """
        Run Python linting tools in check mode.

        Args:
            target_paths: Specific paths to check (if None, scan entire project)
            tools: Specific tools to run (if None, run all available)
            output_dir: Output directory for detailed reports

        Returns:
            LintSummary: Summary of linting results

        Raises:
            LintCheckInterfaceError: If linting check fails
        """
        try:
            ezprinter.print_header("Checking Python Code")

            with ezprinter.create_spinner_with_status(
                "Scanning project for Python files..."
            ) as (progress, task):
                progress.update(
                    task,
                    description="Scanning project for Python files...",
                    status="Initializing...",
                )

                try:
                    python_files = self._get_target_files(target_paths)
                except (
                    LintServiceError,
                    ToolExecutionServiceError,
                    ToolAvailabilityServiceError,
                    ValidationServiceError,
                ) as e:
                    # Convert service exceptions to interface exceptions
                    raise PythonLintInterfaceError(
                        message=f"Failed to get target files: {e}",
                        operation="check_python_code",
                        target_path=str(self.project_root),
                        details=f"Service exception: {type(e).__name__}",
                    ) from e
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise PythonLintInterfaceError(
                        message=f"Failed to get target files: {e}",
                        operation="check_python_code",
                        target_path=str(self.project_root),
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                if not python_files:
                    progress.update(task, status="No Python files found to check")
                    return LintSummaryResult(
                        success=False, message="No Python files found to check"
                    )

                progress.update(task, status=f"Found {len(python_files)} Python files")

                try:
                    scan_result = self.file_scanner.get_scan_summary(python_files)
                    # Convert FileScanResult to dict for compatibility
                    scan_summary = {
                        "target_path": (
                            str(scan_result.target_path)
                            if scan_result.target_path
                            else ""
                        ),
                        "total_files": scan_result.total_files,
                        "file_extensions": scan_result.file_extensions or [],
                        "excluded_dirs": scan_result.excluded_dirs or [],
                        "scan_successful": scan_result.success,
                    }
                except Exception as e:
                    logger.warning(f"Failed to get scan summary: {e}")
                    scan_summary = {"total_files": len(python_files), "errors": []}

                progress.update(task, status="Running linting tools...")

                target_dirs = [str(f) for f in python_files]

                try:
                    tool_results = self.python_lint_service.check_python_code(
                        target_dirs=target_dirs, cwd=self.project_root, tools=tools
                    )
                except (
                    LintServiceError,
                    ToolExecutionServiceError,
                    ToolAvailabilityServiceError,
                    ValidationServiceError,
                ) as e:
                    # Convert service exceptions to interface exceptions
                    raise PythonLintInterfaceError(
                        message=f"Failed to execute Python linting tools: {e}",
                        operation="check_python_code",
                        target_path=str(self.project_root),
                        details=f"Service exception: {type(e).__name__}",
                    ) from e
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise PythonLintInterfaceError(
                        message=f"Failed to execute Python linting tools: {e}",
                        operation="check_python_code",
                        target_path=str(self.project_root),
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                progress.update(task, status="Analysis completed")

            # Calculate totals
            total_issues = sum(result.issues_found for result in tool_results.values())

            summary = LintSummaryResult(
                success=all(result.success for result in tool_results.values()),
                message=f"Checked {len(python_files)} files with {len(tool_results)} tools",
                total_files=len(python_files),
                total_issues=total_issues,
                tool_results=tool_results,
                scan_summary=scan_summary,
            )

            # Generate output files if requested
            if output_dir:
                try:
                    export_lint_results_to_json(
                        tool_results, Path(output_dir), mode="check"
                    )
                except Exception as e:
                    logger.warning(f"Failed to generate output files: {e}")

            return summary

        except PythonLintInterfaceError:
            # Re-raise interface exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in check_python_code: {e}", exc_info=True)
            raise PythonLintInterfaceError(
                message=f"Python code checking failed: {e}",
                operation="check_python_code",
                target_path=str(self.project_root),
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def fix_python_code(
        self,
        target_paths: list[str] | None = None,
        tools: list[str] | None = None,
        output_dir: str | None = None,
    ) -> LintSummaryResult:
        """
        Run Python linting tools in fix mode.

        Args:
            target_paths: Specific paths to fix (if None, scan entire project)
            tools: Specific tools to run (if None, run all available fixable tools)
            output_dir: Output directory for detailed reports

        Returns:
            LintSummary: Summary of fixing results

        Raises:
            LintFixInterfaceError: If linting fix fails
        """
        try:
            ezprinter.print_header("Fixing Python Code")

            with ezprinter.create_spinner_with_status(
                "Scanning project for Python files..."
            ) as (progress, task):
                progress.update(
                    task,
                    description="Scanning project for Python files...",
                    status="Initializing...",
                )

                try:
                    python_files = self._get_target_files(target_paths)
                except (
                    LintServiceError,
                    ToolExecutionServiceError,
                    ToolAvailabilityServiceError,
                    ValidationServiceError,
                ) as e:
                    # Convert service exceptions to interface exceptions
                    raise PythonLintInterfaceError(
                        message=f"Failed to get target files: {e}",
                        operation="fix_python_code",
                        target_path=str(self.project_root),
                        details=f"Service exception: {type(e).__name__}",
                    ) from e
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise PythonLintInterfaceError(
                        message=f"Failed to get target files: {e}",
                        operation="fix_python_code",
                        target_path=str(self.project_root),
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                if not python_files:
                    progress.update(task, status="No Python files found to fix")
                    return LintSummaryResult(
                        success=False, message="No Python files found to fix"
                    )

                progress.update(task, status=f"Found {len(python_files)} Python files")

                try:
                    scan_result = self.file_scanner.get_scan_summary(python_files)
                    # Convert FileScanResult to dict for compatibility
                    scan_summary = {
                        "target_path": (
                            str(scan_result.target_path)
                            if scan_result.target_path
                            else ""
                        ),
                        "total_files": scan_result.total_files,
                        "file_extensions": scan_result.file_extensions or [],
                        "excluded_dirs": scan_result.excluded_dirs or [],
                        "scan_successful": scan_result.success,
                    }
                except Exception as e:
                    logger.warning(f"Failed to get scan summary: {e}")
                    scan_summary = {"total_files": len(python_files), "errors": []}

                progress.update(task, status="Running fixing tools...")

                target_dirs = [str(f) for f in python_files]

                try:
                    tool_results = self.python_lint_service.fix_python_code(
                        target_dirs=target_dirs, cwd=self.project_root, tools=tools
                    )
                except (
                    LintServiceError,
                    ToolExecutionServiceError,
                    ToolAvailabilityServiceError,
                    ValidationServiceError,
                ) as e:
                    # Convert service exceptions to interface exceptions
                    raise PythonLintInterfaceError(
                        message=f"Failed to execute Python fixing tools: {e}",
                        operation="fix_python_code",
                        target_path=str(self.project_root),
                        details=f"Service exception: {type(e).__name__}",
                    ) from e
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise PythonLintInterfaceError(
                        message=f"Failed to execute Python fixing tools: {e}",
                        operation="fix_python_code",
                        target_path=str(self.project_root),
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                progress.update(task, status="Analysis completed")

            # Calculate totals
            total_fixed = sum(result.fixed_issues for result in tool_results.values())

            summary = LintSummaryResult(
                success=all(result.success for result in tool_results.values()),
                message=f"Processed {len(python_files)} files with {len(tool_results)} tools",
                total_files=len(python_files),
                total_fixed=total_fixed,
                tool_results=tool_results,
                scan_summary=scan_summary,
            )

            # Generate output files if requested
            if output_dir:
                try:
                    export_lint_results_to_json(
                        tool_results, Path(output_dir), mode="fix"
                    )
                except Exception as e:
                    logger.warning(f"Failed to generate output files: {e}")

            return summary

        except PythonLintInterfaceError:
            # Re-raise interface exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in fix_python_code: {e}", exc_info=True)
            raise PythonLintInterfaceError(
                message=f"Python code fixing failed: {e}",
                operation="fix_python_code",
                target_path=str(self.project_root),
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_tool_status(self) -> ToolStatusResult:
        """
        Get status of all available linting tools.

        Returns:
            ToolStatusResult: Tool availability and version information

        Raises:
            LintToolStatusInterfaceError: If tool status retrieval fails
        """
        try:
            ezprinter.print_header("Linting Tools Status")

            try:
                tool_summary = self.python_lint_service.get_tool_summary()
                return ToolStatusResult(
                    success=True,
                    message="Tool status retrieved successfully",
                    tool_summary=tool_summary,
                )
            except (LintServiceError, ToolAvailabilityServiceError) as e:
                # Convert service exceptions to interface exceptions
                raise PythonLintInterfaceError(
                    message=f"Failed to get tool summary: {e}",
                    operation="get_tool_status",
                    details=f"Service exception: {type(e).__name__}",
                ) from e
            except Exception as e:
                # Wrap unexpected external exceptions
                raise PythonLintInterfaceError(
                    message=f"Failed to get tool summary: {e}",
                    operation="get_tool_status",
                    details=f"Exception type: {type(e).__name__}",
                ) from e

        except PythonLintInterfaceError:
            # Re-raise interface exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in get_tool_status: {e}", exc_info=True)
            raise PythonLintInterfaceError(
                message=f"Tool status retrieval failed: {e}",
                operation="get_tool_status",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _get_target_files(self, target_paths: list[str] | None) -> list[Path]:
        """
        Get list of Python files to process.

        Args:
            target_paths: Specific paths to check (if None, scan entire project)

        Returns:
            list[Path]: List of Python files to process

        Raises:
            PythonLintInterfaceError: If file scanning fails
        """
        try:
            if not target_paths:
                # Scan entire project
                try:
                    search_result = self.file_scanner.get_project_python_files(
                        self.project_root
                    )
                    if not search_result.success:
                        raise PythonLintInterfaceError(
                            message=f"Failed to scan project: {search_result.error}",
                            operation="_get_target_files",
                            details="File search failed",
                        )
                    return search_result.files_found or []
                except (
                    LintServiceError,
                    ToolExecutionServiceError,
                    ToolAvailabilityServiceError,
                    ValidationServiceError,
                ) as e:
                    # Convert service exceptions to interface exceptions
                    raise PythonLintInterfaceError(
                        message=f"Failed to scan project for Python files: {e}",
                        operation="_get_target_files",
                        details=f"Service exception: {type(e).__name__}",
                    ) from e
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise PythonLintInterfaceError(
                        message=f"Failed to scan project for Python files: {e}",
                        operation="_get_target_files",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

            # Process specific paths
            python_files: list[Path] = []
            for path_str in target_paths:
                try:
                    path = Path(path_str)
                    # Don't modify the path if it's already absolute
                    # If it's relative, resolve it from current working directory, not project_root
                    if not path.is_absolute():
                        path = Path.cwd() / path

                    try:
                        search_result = self.file_scanner.find_python_files(
                            path, recursive=True
                        )
                        if search_result.success and search_result.files_found:
                            python_files.extend(search_result.files_found)
                    except (
                        LintServiceError,
                        ToolExecutionServiceError,
                        ToolAvailabilityServiceError,
                        ValidationServiceError,
                    ) as e:
                        # Convert service exceptions to interface exceptions
                        raise PythonLintInterfaceError(
                            message=f"Failed to find Python files in {path_str}: {e}",
                            operation="_get_target_files",
                            details=f"Service exception: {type(e).__name__}",
                        ) from e
                    except Exception as e:
                        # Wrap unexpected external exceptions
                        logger.warning(
                            f"Failed to find Python files in {path_str}: {e}"
                        )
                        # Continue with other paths
                        continue

                except Exception as e:
                    logger.warning(f"Failed to process path {path_str}: {e}")
                    # Continue with other paths
                    continue

            return python_files

        except PythonLintInterfaceError:
            # Re-raise interface exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _get_target_files: {e}", exc_info=True)
            raise PythonLintInterfaceError(
                message=f"Target files retrieval failed: {e}",
                operation="_get_target_files",
                details=f"Exception type: {type(e).__name__}",
            ) from e
