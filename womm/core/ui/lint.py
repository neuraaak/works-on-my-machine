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
from rich.json import JSON
from rich.table import Table

# Local imports
from ..utils.lint_manager import LintResult, LintSummary
from .console import print_error, print_info, print_success

# CONFIGURATION
########################################################
# Global variables and settings

console = Console()


# MAIN FUNCTIONS
########################################################
# Core linting display functionality


def print_lint_progress(step: str, description: str):
    """Print linting progress step."""
    print_info(f"Step: {step} - {description}")


def print_lint_result(result: LintResult):
    """Print individual linting tool result."""
    if result.success:
        print_success(f"{result.tool_name}: {result.message}")
    else:
        print_error(f"{result.tool_name}: {result.message}")


def print_lint_summary(summary: LintSummary):
    """Print comprehensive linting summary with enhanced UI."""

    if summary.success:
        print_success(f"✅ {summary.message}")
        if summary.error:
            print_info(f"{summary.error}")

        # Create enhanced summary table
        table = Table(
            title="🎨 Linting Summary", show_header=True, header_style="bold magenta"
        )
        table.add_column("Tool", style="cyan", no_wrap=True)
        table.add_column("Status", justify="center")
        table.add_column("Files", justify="right", style="blue")
        table.add_column("Issues", justify="right", style="yellow")
        table.add_column("Fixed", justify="right", style="green")

        for result in summary.tool_results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            status_style = "green" if result.success else "red"

            table.add_row(
                result.tool_name,
                f"[{status_style}]{status}[/{status_style}]",
                str(result.files_checked),
                str(result.issues_found) if result.issues_found > 0 else "-",
                str(result.fixed_issues) if result.fixed_issues > 0 else "-",
            )

        print_info("")  # Empty line
        console.print(table)

        # Overall summary with emojis
        total_issues = summary.total_issues
        total_fixed = summary.total_fixed

        if total_issues == 0:
            print_success(
                f"🎉 Perfect! All checks passed! ({summary.total_files} directories checked)"
            )
        elif total_fixed > 0:
            print_success(
                f"✨ Fixed {total_fixed} issues! ({summary.total_files} directories processed)"
            )
        else:
            print_info(
                f"⚠️  Found {total_issues} issues in {summary.total_files} directories"
            )

    else:
        print_error(f"❌ {summary.message}")
        if summary.error:
            print_error(f"{summary.error}")

        # Show failed tools with enhanced display
        failed = [r for r in summary.tool_results if not r.success]
        if failed:
            print_error(f"💥 Failed tools: {', '.join(r.tool_name for r in failed)}")

            # Show detailed results for failed tools
            for r in failed:
                print_error(f"🔍 {r.tool_name} details:")
                if r.message:
                    print_info(f"{r.message}")
                if r.data is not None:
                    console.print(JSON.from_data(r.data))


# UTILITY FUNCTIONS
########################################################
# Helper functions for linting operations


def print_lint_error(tool: str, error: str):
    """Print linting error."""
    print_error(f"{tool}: {error}")


def print_lint_fix_suggestions(target_dir: str, target_dirs: list):
    """Print suggestions for fixing linting issues."""
    print_info("To fix issues, run:")
    print_info(f"   cd {target_dir}")
    print_info(f"   ruff check --fix {' '.join(target_dirs)}")
    print_info(f"   ruff format {' '.join(target_dirs)}")
    print_info(f"   isort {' '.join(target_dirs)}")


def print_lint_start(lint_type: str, target_path: str):
    """Print linting start message."""
    print_info(f"Starting {lint_type} linting")
    print_info(f"Target path: {target_path}")


def print_tool_check_result(tool: str, available: bool):
    """Print tool availability check result."""
    if available:
        print_success(f"{tool}: Available")
    else:
        print_error(f"{tool}: Not available")
