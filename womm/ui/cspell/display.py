#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SPELL UI - Spell Checking UI Components
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Spell checking UI components for Works On My Machine.

Provides Rich UI components for displaying spell check results,
including issue tables and status information. Follows the
Manager-Tools-UI pattern for clean separation of concerns.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import Any

# Third-party imports
from rich.table import Table

# Local imports
from ..common.ezpl_bridge import ezconsole, ezprinter

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////


def display_spell_issues_table(issues: list[dict[str, str | int]]) -> None:
    """
    Display spell check issues in a Rich table format.

    Args:
        issues: List of spelling issues with file, word, line information
    """
    if not issues:
        return

    # Create a table for clearer display
    table = Table(
        title="Spelling Issues Summary",
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
    )

    table.add_column("File", style="cyan", width=30)
    table.add_column("Issues", style="yellow", justify="center", width=10)
    table.add_column("Sample Issues", style="white", width=50)

    # Group by file
    files_issues = {}
    for issue in issues:
        file_path = issue["file"]
        if file_path not in files_issues:
            files_issues[file_path] = []
        files_issues[file_path].append(issue)

    # Add rows to table
    for file_path, file_issues_list in files_issues.items():
        # Create an overview of errors
        sample_issues = []
        for issue in file_issues_list[:3]:  # Limit to 3 examples
            word = issue.get("word", "")
            line = issue.get("line", 0)
            if word and line > 0:
                sample_issues.append(f"'{word}' (l.{line})")
            elif word:
                sample_issues.append(f"'{word}'")

        sample_text = ", ".join(sample_issues)
        if len(file_issues_list) > 3:
            sample_text += f" (+{len(file_issues_list) - 3} more)"

        table.add_row(str(file_path), str(len(file_issues_list)), sample_text)

    ezconsole.print(table)


def display_spell_summary(
    summary: dict[str, Any], issues: list[dict[str, Any]]
) -> None:
    """
    Display spell check summary information.

    Args:
        summary: Summary statistics from spell check
        issues: List of issues found
    """
    if issues:
        ezprinter.warn(
            f"Spell check completed with {summary['issues_found']} issues found in {summary['files_checked']} files"
        )
    else:
        ezprinter.success("Spell check completed successfully - No issues found")


def display_spell_status_table(status: dict[str, str]) -> None:
    """
    Display CSpell project status in table format.

    Args:
        status: Status information about CSpell configuration
    """
    # Cette fonction sera implémentée si nécessaire
    # Pour l'instant, on garde l'affichage simple dans spell_manager


def create_spell_progress_table(files: list[str]) -> None:
    """
    Create a progress table for spell checking multiple files.

    Args:
        files: List of files being processed
    """
    # Cette fonction sera implémentée si nécessaire
    # Pour l'instant, on utilise les spinners existants


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "create_spell_progress_table",
    "display_spell_issues_table",
    "display_spell_status_table",
    "display_spell_summary",
]
