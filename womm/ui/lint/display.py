#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# LINT UI - Linting UI Components
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Linting UI components for Works On My Machine.

This module provides Rich UI components for displaying linting results,
including summary tables and tool status information. Follows the
Manager-Tools-UI pattern for clean separation of concerns.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Third-party imports
from rich.table import Table

# Local imports
from ...shared.result_models import LintSummaryResult
from ..common.ezpl_bridge import ezconsole, ezprinter

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////


def display_lint_summary(summary: LintSummaryResult, mode: str = "check") -> None:
    """
    Display comprehensive linting summary with enhanced UI.

    Args:
        summary: LintSummary containing all results
        mode: Mode of operation ("check" or "fix")
    """
    # Display scan summary first
    if summary.scan_summary:
        print()
        _display_scan_info(summary.scan_summary)

    # Display tool results
    print()
    _display_tool_results(summary.tool_results, mode)

    # Display overall summary
    print()
    _display_overall_summary(summary, mode)


def _display_scan_info(scan_summary: dict) -> None:
    """Display file scanning information."""
    total_files = scan_summary.get("total_files", 0)
    total_size = scan_summary.get("total_size", 0)
    directories = scan_summary.get("directories", set())
    extensions = scan_summary.get("extensions", {})

    ezprinter.info(
        f"📁 Scanned {total_files} files ({_format_size(total_size)}) across {len(directories)} directories"
    )

    if extensions:
        ext_info = ", ".join(f"{ext}: {count}" for ext, count in extensions.items())
        ezprinter.info(f"📄 File types: {ext_info}")


def _display_tool_results(tool_results: dict, mode: str) -> None:
    """Display results from each linting tool."""
    if not tool_results:
        ezprinter.warn("No tool results to display")
        return

    # Create results table
    table = Table(title=f"🔧 Linting Results ({mode.title()} Mode)", show_header=True)
    table.add_column("Tool", style="cyan", width=12)
    table.add_column("Status", width=10)
    table.add_column("Files", justify="right", width=8)

    if mode == "check":
        table.add_column("Issues", justify="right", width=8)
    else:
        table.add_column("Fixed", justify="right", width=8)

    table.add_column("Details", style="dim")

    for tool_name, result in tool_results.items():
        # Status with emoji
        if result.success:
            status = "✅ PASS" if mode == "check" else "✅ FIXED"
            status_style = "green"
        else:
            status = "❌ FAIL" if mode == "check" else "❌ ERROR"
            status_style = "red"

        # File count
        files_count = str(result.files_checked)

        # Issues or fixes count
        if mode == "check":
            count_value = str(result.issues_found)
            count_style = "red" if result.issues_found > 0 else "green"
        else:
            count_value = str(result.fixed_issues)
            count_style = "green" if result.fixed_issues > 0 else "dim"

        # Details (truncated message)
        details = _truncate_message(result.message)

        table.add_row(
            tool_name,
            f"[{status_style}]{status}[/{status_style}]",
            files_count,
            f"[{count_style}]{count_value}[/{count_style}]",
            details,
        )

    ezconsole.print(table)


def _display_overall_summary(summary: LintSummaryResult, mode: str) -> None:
    """Display overall summary of linting operation."""
    if mode == "check":
        if summary.success:
            if summary.total_issues == 0:
                ezprinter.success(
                    f"✨ All checks passed! {summary.total_files} files are clean."
                )
            else:
                ezprinter.warn(
                    f"⚠️  Found {summary.total_issues} issues across {summary.total_files} files."
                )
        else:
            ezprinter.tip(
                "For detailed diagnostics, run the tools directly:\n"
                "  • ruff check <path>\n"
                "  • black --check <path>\n"
                "  • isort --check-only <path>\n"
                "  • bandit -r <path>"
            )
    elif summary.success:
        if summary.total_fixed > 0:
            ezprinter.success(
                f"✨ Fixed {summary.total_fixed} issues across {summary.total_files} files!"
            )
        else:
            ezprinter.info(f"✅ No issues to fix in {summary.total_files} files.")
    else:
        ezprinter.tip(
            "Some tools reported issues. For detailed diagnostics and auto-fixes, run the tools directly:\n"
            "  • ruff check --fix <path>\n"
            "  • black <path>\n"
            "  • isort <path>\n"
            "  • bandit -r <path>  (security only, no auto-fix)"
        )


def _format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def _truncate_message(message: str, max_length: int = 50) -> str:
    """Truncate message for table display."""
    if not message:
        return ""

    # Remove newlines and clean up
    clean_message = " ".join(message.split())

    if len(clean_message) <= max_length:
        return clean_message

    return clean_message[: max_length - 3] + "..."


def display_tool_status(tool_summary: dict) -> None:
    """
    Display status of available linting tools.

    Args:
        tool_summary: Dictionary of tool names to status/version strings
    """
    table = Table(title="🔧 Linting Tools Status", show_header=True)
    table.add_column("Tool", style="cyan", width=15)
    table.add_column("Status", width=20)
    table.add_column("Version/Details", style="dim")

    for tool_name, status in tool_summary.items():
        if "not available" in status.lower():
            status_display = "[red]❌ Not Available[/red]"
            version_display = "Install required"
        else:
            status_display = "[green]✅ Available[/green]"
            version_display = status

        table.add_row(tool_name, status_display, version_display)

    ezconsole.print(table)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "display_lint_summary",
    "display_tool_status",
]
