#!/usr/bin/env python3
"""
Linting manager for WOMM projects.
Centralizes linting logic and provides structured results.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from ..ui.console import print_error, print_success, print_system
from ..ui.progress import create_spinner_with_status
from .cli_manager import run_command, run_silent
from .results import BaseResult as Result


@dataclass
class LintResult(Result):
    """Result of a linting operation."""

    tool_name: str = ""
    files_checked: int = 0
    issues_found: int = 0
    fixed_issues: int = 0
    data: object = None


@dataclass
class LintSummary(Result):
    """Summary of all linting operations."""

    total_files: int = 0
    total_issues: int = 0
    total_fixed: int = 0
    tool_results: List[LintResult] = None

    def __post_init__(self):
        if self.tool_results is None:
            self.tool_results = []


class LintManager:
    """Manages linting operations for different languages and tools."""

    def __init__(self):
        self.security_patterns = [
            ".env*",
            ".secret*",
            "*password*",
            "*secret*",
            "*.key",
            "*.pem",
            "*.crt",
            "credentials",
            "keys",
        ]

    def is_security_excluded(self, path: Path) -> bool:
        """Check if a file or directory is excluded for security reasons."""
        import fnmatch

        path_str = str(path).lower()
        name = path.name.lower()

        for pattern in self.security_patterns:
            if fnmatch.fnmatch(name, pattern) or pattern in path_str:
                return True
        return False

    def detect_python_dirs(self, base_path: Optional[Path] = None) -> List[str]:
        """Detect Python directories while excluding sensitive files."""
        current_dir = Path(base_path) if base_path else Path.cwd()
        target_dirs = []

        # Search for directories with Python files
        for item in current_dir.iterdir():
            if (
                item.is_dir()
                and not item.name.startswith(".")
                and item.name not in ["build", "dist", "__pycache__", "htmlcov"]
                and not self.is_security_excluded(item)
            ):
                # Check if it contains Python files (non-sensitive)
                has_python_files = False
                try:
                    for py_file in item.glob("*.py"):
                        if not self.is_security_excluded(py_file):
                            has_python_files = True
                            break
                    if not has_python_files:
                        for py_file in item.glob("**/*.py"):
                            if not self.is_security_excluded(py_file):
                                has_python_files = True
                                break
                    if has_python_files:
                        target_dirs.append(str(item))
                except OSError:
                    # Ignore file access errors
                    pass

        # Add 'tests' if it exists and is not excluded
        tests_dir = current_dir / "tests"
        if tests_dir.exists() and not self.is_security_excluded(tests_dir):
            target_dirs.append("tests")

        # Fallback: analyze current directory if it contains safe .py files
        if not target_dirs:
            has_safe_python_files = False
            try:
                for py_file in current_dir.glob("*.py"):
                    if not self.is_security_excluded(py_file):
                        has_safe_python_files = True
                        break
            except OSError:
                pass
            if has_safe_python_files:
                target_dirs.append(".")

        return target_dirs

    def detect_womm_dirs(self, base_path: Optional[Path] = None) -> List[str]:
        """Detect directories specific to the works-on-my-machine project."""
        current_dir = Path(base_path) if base_path else Path.cwd()
        target_dirs = []

        # Specific directories for the works-on-my-machine project
        project_dirs = ["shared", "languages"]

        for dir_name in project_dirs:
            dir_path = current_dir / dir_name
            if dir_path.exists() and dir_path.is_dir():
                # Check if it contains Python files (non-sensitive)
                has_python_files = False
                try:
                    for py_file in dir_path.glob("**/*.py"):
                        if not self.is_security_excluded(py_file):
                            has_python_files = True
                            break
                    if has_python_files:
                        target_dirs.append(str(dir_path))
                except OSError:
                    # Ignore file access errors
                    pass

        # Add Python files at the root (init.py, etc.)
        root_python_files = []
        try:
            for py_file in current_dir.glob("*.py"):
                if not self.is_security_excluded(py_file):
                    root_python_files.append(str(py_file))
        except OSError:
            pass

        if root_python_files:
            target_dirs.extend(root_python_files)

        return target_dirs

    def check_tool_availability(self, tools: List[str]) -> Result:
        """Check if required linting tools are available with UI feedback."""
        missing_tools = []

        with create_spinner_with_status("Checking linting tools availability...") as (
            progress,
            task,
        ):
            for i, tool in enumerate(tools, 1):
                progress.update(task, status=f"Checking {tool} ({i}/{len(tools)})...")
                try:
                    result = run_silent([tool, "--version"])
                    if result.returncode != 0:
                        raise Exception(f"Tool {tool} not available")
                    print_success(f"Tool {tool} is available")
                except Exception:
                    missing_tools.append(tool)
                    print_error(f"Tool {tool} is not available")

        if missing_tools:
            print_error(f"Missing tools: {', '.join(missing_tools)}")
            return Result(
                success=False,
                message=f"Missing tools: {', '.join(missing_tools)}",
                error="Install them with: pip install -e '.[dev]'",
            )

        print_success("All linting tools are available")
        return Result(success=True, message="All tools available")

    def run_python_lint(
        self,
        target_path: Optional[Path] = None,
        fix: bool = False,
        json_output: bool = False,
    ) -> LintSummary:
        """Run Python linting with ruff, black, and isort with UI feedback."""
        target_dir = Path(target_path) if target_path else Path.cwd()

        print_system(f"🎨 Starting Python linting for: {target_dir}")

        # Check tool availability
        tools = ["ruff", "black", "isort"]
        tool_check = self.check_tool_availability(tools)
        if not tool_check.success:
            return LintSummary(
                success=False, message=tool_check.message, error=tool_check.error
            )

        # Detect directories with spinner
        with create_spinner_with_status("Detecting Python directories...") as (
            progress,
            task,
        ):
            progress.update(task, status="Scanning for Python files...")
            target_dirs = self.detect_python_dirs(target_dir)
            progress.update(task, status=f"Found {len(target_dirs)} directories")

        if not target_dirs:
            print_error("No Python folders found")
            return LintSummary(
                success=False,
                message="No Python folders found",
                error=f"Target directory: {target_dir}",
            )

        print_success(f"Found {len(target_dirs)} Python directories to analyze")

        summary = LintSummary(
            success=False,  # Will be updated based on tool results
            message="Python linting in progress",
            error=f"Target directories: {', '.join(target_dirs)}",
        )

        # Run linting tools with progress tracking
        mode_text = "fix" if fix else "check"
        with create_spinner_with_status(
            f"Running Python linting ({mode_text} mode)..."
        ) as (
            progress,
            task,
        ):
            if fix:
                # Fix mode
                progress.update(task, status="Running ruff fix...")
                summary.tool_results.append(self._run_ruff_fix(target_dirs, target_dir))

                progress.update(task, status="Running black format...")
                summary.tool_results.append(
                    self._run_black_format(target_dirs, target_dir)
                )

                progress.update(task, status="Running isort fix...")
                summary.tool_results.append(
                    self._run_isort_fix(target_dirs, target_dir)
                )
            else:
                # Check mode
                progress.update(task, status="Running ruff check...")
                summary.tool_results.append(
                    self._run_ruff_check(
                        target_dirs, target_dir, json_output=json_output
                    )
                )

                progress.update(task, status="Running black check...")
                summary.tool_results.append(
                    self._run_black_check(target_dirs, target_dir)
                )

                progress.update(task, status="Running isort check...")
                summary.tool_results.append(
                    self._run_isort_check(target_dirs, target_dir)
                )

            progress.update(task, status="Compiling results...")

        # Update summary
        summary.total_files = len(target_dirs)
        summary.total_issues = sum(r.issues_found for r in summary.tool_results)
        summary.total_fixed = sum(r.fixed_issues for r in summary.tool_results)
        summary.success = all(r.success for r in summary.tool_results)

        # Final status
        if summary.success:
            print_success(
                f"✨ Python linting completed successfully! ({summary.total_files} directories checked)"
            )
        else:
            print_error(
                f"❌ Python linting found {summary.total_issues} issues in {summary.total_files} directories"
            )

        return summary

    def run_womm_lint(
        self,
        target_path: Optional[Path] = None,
        fix: bool = False,
        json_output: bool = False,
    ) -> LintSummary:
        """Run linting for the works-on-my-machine project with UI feedback."""
        target_dir = Path(target_path) if target_path else Path.cwd()

        print_system(f"🎨 Starting WOMM project linting for: {target_dir}")

        # Check tool availability
        tools = ["ruff", "bandit"]
        tool_check = self.check_tool_availability(tools)
        if not tool_check.success:
            return LintSummary(
                success=False, message=tool_check.message, error=tool_check.error
            )

        # Detect directories with spinner
        with create_spinner_with_status("Detecting WOMM project directories...") as (
            progress,
            task,
        ):
            progress.update(task, status="Scanning for WOMM Python files...")
            target_dirs = self.detect_womm_dirs(target_dir)
            progress.update(task, status=f"Found {len(target_dirs)} directories")

        if not target_dirs:
            print_error("No Python directory found")
            return LintSummary(
                success=False,
                message="No Python directory found",
                error=f"Target directory: {target_dir}",
            )

        print_success(f"Found {len(target_dirs)} WOMM directories to analyze")

        summary = LintSummary(
            success=False,  # Will be updated based on tool results
            message="WOMM linting in progress",
            error=f"Target directories: {', '.join(target_dirs)}",
        )

        # Run linting tools with progress tracking
        mode_text = "fix" if fix else "check"
        with create_spinner_with_status(
            f"Running WOMM linting ({mode_text} mode)..."
        ) as (
            progress,
            task,
        ):
            if fix:
                # Fix mode
                progress.update(task, status="Running ruff fix...")
                summary.tool_results.append(self._run_ruff_fix(target_dirs, target_dir))

                progress.update(task, status="Running ruff format...")
                summary.tool_results.append(
                    self._run_ruff_format(target_dirs, target_dir)
                )
            else:
                # Check mode
                progress.update(task, status="Running ruff check...")
                summary.tool_results.append(
                    self._run_ruff_check(
                        target_dirs, target_dir, json_output=json_output
                    )
                )

                progress.update(task, status="Running bandit security check...")
                summary.tool_results.append(
                    self._run_bandit_check(target_dirs, target_dir)
                )

            progress.update(task, status="Compiling results...")

        # Update summary
        summary.total_files = len(target_dirs)
        summary.total_issues = sum(r.issues_found for r in summary.tool_results)
        summary.total_fixed = sum(r.fixed_issues for r in summary.tool_results)
        summary.success = all(r.success for r in summary.tool_results)

        # Final status
        if summary.success:
            print_success(
                f"✨ WOMM linting completed successfully! ({summary.total_files} directories checked)"
            )
        else:
            print_error(
                f"❌ WOMM linting found {summary.total_issues} issues in {summary.total_files} directories"
            )

        return summary

    def _run_ruff_check(
        self, target_dirs: List[str], cwd: Path, json_output: bool = False
    ) -> LintResult:
        """Run ruff check."""
        if json_output:
            result = run_command(
                ["ruff", "check", "--output-format", "json"] + target_dirs,
                "Style check (ruff)",
                cwd=cwd,
            )
            if not (result.stdout):
                result = run_command(
                    ["ruff", "check", "--format", "json"] + target_dirs,
                    "Style check (ruff)",
                    cwd=cwd,
                )
        else:
            result = run_command(
                ["ruff", "check"] + target_dirs, "Style check (ruff)", cwd=cwd
            )

        text = result.stdout or result.stderr or ""
        issues = 0
        if json_output and result.stdout:
            try:
                import json

                parsed = json.loads(result.stdout)
                if isinstance(parsed, list):
                    issues = len(parsed)
                return LintResult(
                    success=result.success,
                    tool_name="ruff",
                    message=(text or "Ruff style check completed"),
                    files_checked=len(target_dirs),
                    issues_found=issues,
                    data=parsed,
                )
            except Exception as e:
                logging.debug(f"Failed to parse Ruff JSON output: {e}")
        if not result.success and text:
            issues = sum(1 for line in text.splitlines() if ":" in line)

        return LintResult(
            success=result.success,
            tool_name="ruff",
            message=(text or "Ruff style check completed"),
            files_checked=len(target_dirs),
            issues_found=issues,
        )

    def _run_ruff_fix(self, target_dirs: List[str], cwd: Path) -> LintResult:
        """Run ruff check --fix."""
        result = run_command(
            ["ruff", "check", "--fix"] + target_dirs, "Style fix (ruff)", cwd=cwd
        )
        return LintResult(
            success=result.success,
            tool_name="ruff",
            message=((result.stdout or result.stderr) or "Ruff style fix completed"),
            files_checked=len(target_dirs),
        )

    def _run_ruff_format(self, target_dirs: List[str], cwd: Path) -> LintResult:
        """Run ruff format."""
        result = run_command(["ruff", "format"] + target_dirs, "Format (ruff)", cwd=cwd)
        return LintResult(
            success=result.success,
            tool_name="ruff",
            message=((result.stdout or result.stderr) or "Ruff formatting completed"),
            files_checked=len(target_dirs),
        )

    def _run_black_check(self, target_dirs: List[str], cwd: Path) -> LintResult:
        """Run black --check."""
        result = run_command(
            ["black", "--check", "--diff"] + target_dirs,
            "Format check (black)",
            cwd=cwd,
        )
        return LintResult(
            success=result.success,
            tool_name="black",
            message=(
                (result.stdout or result.stderr) or "Black format check completed"
            ),
            files_checked=len(target_dirs),
        )

    def _run_black_format(self, target_dirs: List[str], cwd: Path) -> LintResult:
        """Run black format."""
        result = run_command(["black"] + target_dirs, "Format (black)", cwd=cwd)
        return LintResult(
            success=result.success,
            tool_name="black",
            message=((result.stdout or result.stderr) or "Black formatting completed"),
            files_checked=len(target_dirs),
        )

    def _run_isort_check(self, target_dirs: List[str], cwd: Path) -> LintResult:
        """Run isort --check-only."""
        result = run_command(
            ["isort", "--check-only", "--diff"] + target_dirs,
            "Import check (isort)",
            cwd=cwd,
        )
        return LintResult(
            success=result.success,
            tool_name="isort",
            message=(
                (result.stdout or result.stderr) or "Isort import check completed"
            ),
            files_checked=len(target_dirs),
        )

    def _run_isort_fix(self, target_dirs: List[str], cwd: Path) -> LintResult:
        """Run isort fix."""
        result = run_command(["isort"] + target_dirs, "Import fix (isort)", cwd=cwd)
        return LintResult(
            success=result.success,
            tool_name="isort",
            message=((result.stdout or result.stderr) or "Isort import fix completed"),
            files_checked=len(target_dirs),
        )

    def _run_bandit_check(self, target_dirs: List[str], cwd: Path) -> LintResult:
        """Run bandit security check."""
        result = run_command(
            ["bandit", "-r", "-f", "json"] + target_dirs,
            "Security check (bandit)",
            cwd=cwd,
        )
        issues = 0
        parsed = None
        if result.stdout:
            try:
                import json

                parsed = json.loads(result.stdout)
                issues = (
                    len(parsed.get("results", [])) if isinstance(parsed, dict) else 0
                )
            except Exception:
                parsed = None
                issues = 0
        return LintResult(
            success=result.success,
            tool_name="bandit",
            message=(
                (result.stdout or result.stderr) or "Bandit security check completed"
            ),
            files_checked=len(target_dirs),
            issues_found=issues,
            data=parsed,
        )
