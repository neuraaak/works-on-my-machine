#!/usr/bin/env python3
"""
Linting manager for WOMM projects.
Centralizes linting logic and provides structured results.
Refactored to use modular utilities and follow architectural patterns.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from ....common.results import LintSummary, ToolResult
from ...exceptions.lint import (
    LintManagerError,
    LintUtilityError,
    LintValidationError,
    ToolAvailabilityError,
    ToolExecutionError,
)
from ...ui.common.console import print_header
from ...ui.common.extended import ProgressAnimations, create_dynamic_layered_progress
from ...utils.file_scanner import FileScanner
from ...utils.lint.python_linting import PythonLintingTools

# =============================================================================
# LOGGER SETUP
# =============================================================================

logger = logging.getLogger(__name__)

# =============================================================================
# MAIN CLASS
# =============================================================================


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

        Raises:
            LintManagerError: If lint manager initialization fails
        """
        try:
            # Input validation
            if project_root is not None and not isinstance(project_root, Path):
                raise LintManagerError(
                    message="Project root must be a Path object",
                    details=f"Received type: {type(project_root).__name__}",
                )

            self.project_root = project_root or Path.cwd()

            # Initialize utility modules
            try:
                self.file_scanner = FileScanner()
                self.python_tools = PythonLintingTools()
            except Exception as e:
                raise LintManagerError(
                    message=f"Failed to initialize utility modules: {e}",
                    details=f"Exception type: {type(e).__name__}",
                ) from e

        except LintManagerError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Failed to initialize LintManager: {e}")
            raise LintManagerError(
                message=f"Lint manager initialization failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def check_python_code(
        self,
        target_paths: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        dry_run: bool = False,
        output_dir: Optional[str] = None,
    ) -> LintSummary:
        """
        Run Python linting tools in check mode.

        Args:
            target_paths: Specific paths to check (if None, scan entire project)
            tools: Specific tools to run (if None, run all available)
            dry_run: Show what would be done without making changes

        Returns:
            LintSummary: Summary of linting results

        Raises:
            LintManagerError: If linting check fails
            LintUtilityError: If utility operations fail
            ToolExecutionError: If tool execution fails
            ToolAvailabilityError: If required tools are not available
            LintValidationError: If validation fails
        """
        try:
            if dry_run:
                from ...ui.common.console import (
                    print_dry_run_message,
                    print_dry_run_success,
                    print_dry_run_warning,
                )

                print_dry_run_warning()
                print_header("🔍 Checking Python Code (DRY RUN)")

                # Simulate file scanning
                print_dry_run_message("scan project", "for Python files to check")
                print_dry_run_message(
                    "run linting tools", f"tools: {tools or 'all available'}"
                )
                print_dry_run_message("analyze results", "generate linting report")
                print_dry_run_success()

                return LintSummary(
                    success=True,
                    message="Dry run completed - no actual linting performed",
                    total_files=0,
                    total_issues=0,
                    tool_results={},
                )

            print_header("🔍 Checking Python Code")
            stages = [
                {
                    "name": "main_linting",
                    "type": "main",
                    "steps": ["File Scan", "Tool Execution", "Analysis"],
                    "description": "Python Linting Progress",
                    "style": "bold bright_white",
                },
                {
                    "name": "file_scan",
                    "type": "spinner",
                    "description": "Scanning Python files...",
                    "style": "bright_cyan",
                },
                {
                    "name": "tool_execution",
                    "type": "spinner",
                    "description": "Running linting tools...",
                    "style": "bright_yellow",
                },
                {
                    "name": "analysis",
                    "type": "spinner",
                    "description": "Analyzing results...",
                    "style": "bright_green",
                },
            ]

            with create_dynamic_layered_progress(stages) as progress:
                animations = ProgressAnimations(progress.progress)

                # Stage 1: File Scan
                progress.update_layer(
                    "file_scan", 0, "Scanning project for Python files..."
                )

                try:
                    python_files = self._get_target_files(target_paths)
                except (
                    LintUtilityError,
                    ToolExecutionError,
                    ToolAvailabilityError,
                    LintValidationError,
                ):
                    # Re-raise our custom exceptions
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise LintManagerError(
                        message=f"Failed to get target files: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                if not python_files:
                    # Apply error pulse animation before emergency stop
                    file_scan_task_id = progress._get_task_id_by_name("file_scan")
                    if file_scan_task_id:
                        animations.error_pulse(file_scan_task_id)
                    progress.emergency_stop("No Python files found to check")
                    return LintSummary(
                        success=False, message="No Python files found to check"
                    )

                try:
                    scan_summary = self.file_scanner.get_scan_summary(python_files)
                except Exception as e:
                    logger.warning(f"Failed to get scan summary: {e}")
                    scan_summary = {"total_files": len(python_files), "errors": []}

                progress.update_layer(
                    "file_scan", 50, f"Found {len(python_files)} Python files"
                )
                progress.update_layer("file_scan", 100, "File scan completed")
                progress.complete_layer("file_scan")
                # Apply success flash animation when file scan completes
                file_scan_task_id = progress._get_task_id_by_name("file_scan")
                if file_scan_task_id:
                    animations.success_flash(file_scan_task_id)
                progress.update_layer("main_linting", 0, "File scan completed")

                # Stage 2: Tool Execution
                progress.update_layer("tool_execution", 0, "Preparing tools...")
                target_dirs = [str(f) for f in python_files]

                try:
                    available_tools = self.python_tools.get_available_tools()
                except (LintUtilityError, ToolAvailabilityError):
                    # Re-raise our custom exceptions
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise LintManagerError(
                        message=f"Failed to get available tools: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                tools_to_run = tools or [
                    t for t, available in available_tools.items() if available
                ]

                progress.update_layer(
                    "tool_execution", 25, f"Running {len(tools_to_run)} tools..."
                )

                # Apply smooth progress animation during tool execution
                tool_exec_task_id = progress._get_task_id_by_name("tool_execution")
                if tool_exec_task_id:
                    animations.smooth_progress(tool_exec_task_id, 75, duration=2.0)

                try:
                    tool_results = self.python_tools.check_python_code(
                        target_dirs=target_dirs, cwd=self.project_root, tools=tools
                    )
                except (
                    LintUtilityError,
                    ToolExecutionError,
                    ToolAvailabilityError,
                    LintValidationError,
                ):
                    # Re-raise our custom exceptions
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise LintManagerError(
                        message=f"Failed to execute Python linting tools: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                progress.update_layer("tool_execution", 100, "Tool execution completed")
                progress.complete_layer("tool_execution")
                # Apply success flash animation when tool execution completes
                tool_exec_task_id = progress._get_task_id_by_name("tool_execution")
                if tool_exec_task_id:
                    animations.success_flash(tool_exec_task_id)
                progress.update_layer("main_linting", 1, "Tool execution completed")

                # Stage 3: Analysis
                progress.update_layer("analysis", 0, "Calculating results...")
                total_issues = sum(
                    result.issues_found for result in tool_results.values()
                )
                progress.update_layer("analysis", 100, f"Found {total_issues} issues")
                progress.complete_layer("analysis")
                # Apply success flash animation when analysis completes
                analysis_task_id = progress._get_task_id_by_name("analysis")
                if analysis_task_id:
                    animations.success_flash(analysis_task_id)
                progress.update_layer("main_linting", 2, "Analysis completed")

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

            # Generate output files if requested
            if output_dir and not dry_run:
                self._generate_output_files(tool_results, output_dir, mode="check")

            return summary

        except (
            LintManagerError,
            LintUtilityError,
            ToolExecutionError,
            ToolAvailabilityError,
            LintValidationError,
        ):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in check_python_code: {e}")
            raise LintManagerError(
                message=f"Python code checking failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def fix_python_code(
        self,
        target_paths: Optional[List[str]] = None,
        tools: Optional[List[str]] = None,
        dry_run: bool = False,
        output_dir: Optional[str] = None,
    ) -> LintSummary:
        """
        Run Python linting tools in fix mode.

        Args:
            target_paths: Specific paths to fix (if None, scan entire project)
            tools: Specific tools to run (if None, run all available fixable tools)
            dry_run: Show what would be done without making changes

        Returns:
            LintSummary: Summary of fixing results

        Raises:
            LintManagerError: If linting fix fails
            LintUtilityError: If utility operations fail
            ToolExecutionError: If tool execution fails
            ToolAvailabilityError: If required tools are not available
            LintValidationError: If validation fails
        """
        try:
            if dry_run:
                from ...ui.common.console import (
                    print_dry_run_message,
                    print_dry_run_success,
                    print_dry_run_warning,
                )

                print_dry_run_warning()
                print_header("🔍 Fixing Python Code (DRY RUN)")

                # Simulate file scanning and fixing
                print_dry_run_message("scan project", "for Python files to fix")
                print_dry_run_message(
                    "run fixing tools", f"tools: {tools or 'all available'}"
                )
                print_dry_run_message(
                    "apply fixes", "to code formatting and style issues"
                )
                print_dry_run_message("analyze results", "generate fixing report")
                print_dry_run_success()

                return LintSummary(
                    success=True,
                    message="Dry run completed - no actual fixes applied",
                    total_files=0,
                    total_fixed=0,
                    tool_results={},
                )

            print_header("🔍 Fixing Python Code")

            # Define stages for dynamic progress
            stages = [
                {
                    "name": "main_fixing",
                    "type": "main",
                    "steps": ["File Scan", "Tool Execution", "Analysis"],
                    "description": "Python Code Fixing Progress",
                    "style": "bold bright_white",
                },
                {
                    "name": "file_scan",
                    "type": "spinner",
                    "description": "Scanning Python files...",
                    "style": "bright_cyan",
                },
                {
                    "name": "tool_execution",
                    "type": "spinner",
                    "description": "Running fixing tools...",
                    "style": "bright_yellow",
                },
                {
                    "name": "analysis",
                    "type": "spinner",
                    "description": "Analyzing results...",
                    "style": "bright_green",
                },
            ]

            with create_dynamic_layered_progress(stages) as progress:
                animations = ProgressAnimations(progress.progress)

                # Stage 1: File Scan
                progress.update_layer(
                    "file_scan", 0, "Scanning project for Python files..."
                )

                try:
                    python_files = self._get_target_files(target_paths)
                except (
                    LintUtilityError,
                    ToolExecutionError,
                    ToolAvailabilityError,
                    LintValidationError,
                ):
                    # Re-raise our custom exceptions
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise LintManagerError(
                        message=f"Failed to get target files: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                if not python_files:
                    # Apply error pulse animation before emergency stop
                    file_scan_task_id = progress._get_task_id_by_name("file_scan")
                    if file_scan_task_id:
                        animations.error_pulse(file_scan_task_id)
                    progress.emergency_stop("No Python files found to fix")
                    return LintSummary(
                        success=False, message="No Python files found to fix"
                    )

                try:
                    scan_summary = self.file_scanner.get_scan_summary(python_files)
                except Exception as e:
                    logger.warning(f"Failed to get scan summary: {e}")
                    scan_summary = {"total_files": len(python_files), "errors": []}

                progress.update_layer(
                    "file_scan", 50, f"Found {len(python_files)} Python files"
                )
                progress.update_layer("file_scan", 100, "File scan completed")
                progress.complete_layer("file_scan")
                # Apply success flash animation when file scan completes
                file_scan_task_id = progress._get_task_id_by_name("file_scan")
                if file_scan_task_id:
                    animations.success_flash(file_scan_task_id)
                progress.update_layer("main_fixing", 0, "File scan completed")

                # Stage 2: Tool Execution
                progress.update_layer("tool_execution", 0, "Preparing fixing tools...")
                target_dirs = [str(f) for f in python_files]

                try:
                    available_tools = self.python_tools.get_available_tools()
                except (LintUtilityError, ToolAvailabilityError):
                    # Re-raise our custom exceptions
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise LintManagerError(
                        message=f"Failed to get available tools: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                tools_to_run = tools or [
                    t for t, available in available_tools.items() if available
                ]

                progress.update_layer(
                    "tool_execution", 25, f"Running {len(tools_to_run)} fixing tools..."
                )

                # Apply smooth progress animation during tool execution
                tool_exec_task_id = progress._get_task_id_by_name("tool_execution")
                if tool_exec_task_id:
                    animations.smooth_progress(tool_exec_task_id, 75, duration=2.0)

                try:
                    tool_results = self.python_tools.fix_python_code(
                        target_dirs=target_dirs, cwd=self.project_root, tools=tools
                    )
                except (
                    LintUtilityError,
                    ToolExecutionError,
                    ToolAvailabilityError,
                    LintValidationError,
                ):
                    # Re-raise our custom exceptions
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise LintManagerError(
                        message=f"Failed to execute Python fixing tools: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

                progress.update_layer("tool_execution", 100, "Tool execution completed")
                progress.complete_layer("tool_execution")
                # Apply success flash animation when tool execution completes
                tool_exec_task_id = progress._get_task_id_by_name("tool_execution")
                if tool_exec_task_id:
                    animations.success_flash(tool_exec_task_id)
                progress.update_layer("main_fixing", 1, "Tool execution completed")

                # Stage 3: Analysis
                progress.update_layer("analysis", 0, "Calculating results...")
                total_fixed = sum(
                    result.fixed_issues for result in tool_results.values()
                )
                progress.update_layer("analysis", 100, f"Fixed {total_fixed} issues")
                progress.complete_layer("analysis")
                # Apply success flash animation when analysis completes
                analysis_task_id = progress._get_task_id_by_name("analysis")
                if analysis_task_id:
                    animations.success_flash(analysis_task_id)
                progress.update_layer("main_fixing", 2, "Analysis completed")

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

            # Generate output files if requested
            if output_dir and not dry_run:
                self._generate_output_files(tool_results, output_dir, mode="fix")

            return summary

        except (
            LintManagerError,
            LintUtilityError,
            ToolExecutionError,
            ToolAvailabilityError,
            LintValidationError,
        ):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in fix_python_code: {e}")
            raise LintManagerError(
                message=f"Python code fixing failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_tool_status(self) -> dict:
        """
        Get status of all available linting tools.

        Returns:
            dict: Tool availability and version information

        Raises:
            LintManagerError: If tool status retrieval fails
            LintUtilityError: If utility operations fail
            ToolAvailabilityError: If tool availability check fails
        """
        try:
            print_header("🔍 Linting Tools Status")

            try:
                return self.python_tools.get_tool_summary()
            except (LintUtilityError, ToolAvailabilityError):
                # Re-raise our custom exceptions
                raise
            except Exception as e:
                # Wrap unexpected external exceptions
                raise LintManagerError(
                    message=f"Failed to get tool summary: {e}",
                    details=f"Exception type: {type(e).__name__}",
                ) from e

        except (LintManagerError, LintUtilityError, ToolAvailabilityError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in get_tool_status: {e}")
            raise LintManagerError(
                message=f"Tool status retrieval failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _get_target_files(self, target_paths: Optional[List[str]]) -> List[Path]:
        """
        Get list of Python files to process.

        Args:
            target_paths: Specific paths to check (if None, scan entire project)

        Returns:
            List[Path]: List of Python files to process

        Raises:
            LintUtilityError: If file scanning fails
            ToolExecutionError: If tool execution fails
            ToolAvailabilityError: If required tools are not available
            LintValidationError: If validation fails
        """
        try:
            if not target_paths:
                # Scan entire project
                try:
                    return self.file_scanner.get_project_python_files(self.project_root)
                except (
                    LintUtilityError,
                    ToolExecutionError,
                    ToolAvailabilityError,
                    LintValidationError,
                ):
                    # Re-raise our custom exceptions
                    raise
                except Exception as e:
                    # Wrap unexpected external exceptions
                    raise LintUtilityError(
                        message=f"Failed to scan project for Python files: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

            # Process specific paths
            python_files = []
            for path_str in target_paths:
                try:
                    path = Path(path_str)
                    # Don't modify the path if it's already absolute
                    # If it's relative, resolve it from current working directory, not project_root
                    if not path.is_absolute():
                        path = Path.cwd() / path

                    try:
                        files = self.file_scanner.find_python_files(
                            path, recursive=True
                        )
                        python_files.extend(files)
                    except (
                        LintUtilityError,
                        ToolExecutionError,
                        ToolAvailabilityError,
                        LintValidationError,
                    ):
                        # Re-raise our custom exceptions
                        raise
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

        except (
            LintUtilityError,
            ToolExecutionError,
            ToolAvailabilityError,
            LintValidationError,
        ):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            logger.error(f"Unexpected error in _get_target_files: {e}")
            raise LintUtilityError(
                message=f"Target files retrieval failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def _generate_output_files(
        self, tool_results: Dict[str, ToolResult], output_dir: str, mode: str = "check"
    ) -> None:
        """
        Generate detailed output files for each tool.

        Args:
            tool_results: Results from linting tools
            output_dir: Directory to save output files
            mode: Operation mode ("check" or "fix")
        """
        try:
            import json
            from datetime import datetime
            from pathlib import Path

            # Create output directory if it doesn't exist
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Generate timestamp for unique filenames
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            for tool_name, result in tool_results.items():
                # Create filename with tool name, mode, and timestamp
                filename = f"{tool_name}_{mode}_{timestamp}.json"
                filepath = output_path / filename

                # Prepare output data
                output_data = {
                    "tool": tool_name,
                    "mode": mode,
                    "timestamp": datetime.now().isoformat(),
                    "success": result.success,
                    "files_checked": result.files_checked,
                    "issues_found": getattr(result, "issues_found", 0),
                    "fixed_issues": getattr(result, "issues_found", 0),
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

                logger.info(f"Generated output file: {filepath}")

        except Exception as e:
            logger.warning(f"Failed to generate output files: {e}")
            # Don't raise - this is a non-critical feature
