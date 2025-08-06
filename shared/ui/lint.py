#!/usr/bin/env python3
"""
UI functions for linting operations.
Provides consistent display of linting results.
"""

# IMPORTS
########################################################
# Standard library imports
# (None for this file)

# Third-party imports
from rich.console import Console
from rich.table import Table

# Local imports
from ..core.lint_manager import LintResult, LintSummary

# CONFIGURATION
########################################################
# Global variables and settings

console = Console()


# MAIN FUNCTIONS
########################################################
# Core linting display functionality


def print_lint_progress(step: str, description: str):
    """Print linting progress step."""
    console.print(f"[INFO]:[PROCESS] :: Step: {step} - {description}")


def print_lint_result(result: LintResult):
    """Print individual linting tool result."""
    if result.success:
        console.print(f"[INFO]:[SUCCESS] :: {result.tool_name}: {result.message}")
    else:
        console.print(f"[ERROR]:[{result.tool_name}] :: {result.message}", style="red")


def print_lint_summary(summary: LintSummary):
    """Print comprehensive linting summary."""
    if summary.success:
        console.print(f"[INFO]:[SUCCESS] :: {summary.message}")
        console.print(f"[INFO]:[DETAILS] :: {summary.error}")

        # Create summary table
        table = Table(title="Linting Summary")
        table.add_column("Tool", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Files", justify="right")
        table.add_column("Issues", justify="right")

        for result in summary.tool_results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            table.add_row(
                result.tool_name,
                status,
                str(result.files_checked),
                str(result.issues_found),
            )

        console.print(table)

        # Overall summary
        console.print(
            f"\n[SUCCESS] All checks passed! ({summary.total_files} files checked)"
        )

    else:
        console.print(f"[ERROR]:[LINTING] :: {summary.message}", style="red")
        if summary.error:
            console.print(f"[ERROR]:[DETAILS] :: {summary.error}", style="red")

        # Show failed tools
        failed_tools = [r.tool_name for r in summary.tool_results if not r.success]
        if failed_tools:
            console.print(
                f"[ERROR]:[FAILED] :: Tools: {', '.join(failed_tools)}", style="red"
            )


# UTILITY FUNCTIONS
########################################################
# Helper functions for linting operations


def print_lint_error(tool: str, error: str):
    """Print linting error."""
    console.print(f"[ERROR]:[{tool}] :: {error}", style="red")


def print_lint_fix_suggestions(target_dir: str, target_dirs: list):
    """Print suggestions for fixing linting issues."""
    console.print("\n[INFO]:[SUGGESTIONS] :: To fix issues, run:")
    console.print(f"   cd {target_dir}")
    console.print(f"   ruff check --fix {' '.join(target_dirs)}")
    console.print(f"   ruff format {' '.join(target_dirs)}")
    console.print(f"   isort {' '.join(target_dirs)}")


def print_lint_start(lint_type: str, target_path: str):
    """Print linting start message."""
    console.print(f"[INFO]:[LINT] :: Starting {lint_type} linting")
    console.print(f"[INFO]:[TARGET] :: Path: {target_path}")


def print_tool_check_result(tool: str, available: bool):
    """Print tool availability check result."""
    if available:
        console.print(f"[INFO]:[TOOL] :: {tool}: Available")
    else:
        console.print(f"[ERROR]:[TOOL] :: {tool}: Not available", style="red")
