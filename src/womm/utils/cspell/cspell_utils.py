#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CSPELL UTILS - Pure CSpell Utility Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure CSpell utility functions for Works On My Machine.

This module contains stateless utility functions for:
- Formatting and displaying spell check information
- Exporting spell check results to JSON files
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
from datetime import datetime
from pathlib import Path
from typing import Any

# Local imports
from ...exceptions.cspell import CSpellServiceError

# ///////////////////////////////////////////////////////////////
# FORMATTING FUNCTIONS
# ///////////////////////////////////////////////////////////////


def format_project_status(status: dict[str, Any]) -> dict[str, Any]:
    """Format project status data for display.

    Args:
        status: Raw status dictionary from service

    Returns:
        dict: Formatted status dictionary

    Raises:
        SpellServiceError: If formatting fails
    """
    try:
        # Add dictionary files information if not present
        if "dict_files" not in status:
            try:
                project_path = Path(status.get("config_path", ".")).parent
                dict_dir = project_path / ".cspell-dict"
                if dict_dir.exists():
                    dict_files = list(dict_dir.glob("*.txt"))
                    status["dict_files"] = [f.name for f in dict_files]
                    status["total_words"] = sum(
                        len(f.read_text().splitlines()) for f in dict_files
                    )
                else:
                    status["dict_files"] = []
                    status["total_words"] = 0
            except Exception:
                status["dict_files"] = []
                status["total_words"] = 0

        return status

    except Exception as e:
        raise CSpellServiceError(
            message=f"Failed to format project status: {e}",
            operation="format_status",
            details=str(e),
        ) from e


def format_dictionary_info(dict_info: dict[str, Any]) -> dict[str, Any]:
    """Format dictionary information for display.

    Args:
        dict_info: Raw dictionary info dictionary

    Returns:
        dict: Formatted dictionary info

    Raises:
        SpellServiceError: If formatting fails
    """
    try:
        # Ensure all required keys exist
        formatted = {
            "directory_exists": dict_info.get("directory_exists", False),
            "total_files": dict_info.get("total_files", 0),
            "files": dict_info.get("files", []),
        }
        return formatted

    except Exception as e:
        raise CSpellServiceError(
            message=f"Failed to format dictionary info: {e}",
            operation="format_dict_info",
            details=str(e),
        ) from e


def format_spell_check_results(
    summary: dict[str, Any], issues: list[dict[str, Any]]
) -> dict[str, Any]:
    """Format spell check results for display.

    Args:
        summary: Summary of spell check
        issues: List of spelling issues

    Returns:
        dict: Formatted results dictionary

    Raises:
        SpellServiceError: If formatting fails
    """
    try:
        formatted = {
            "summary": summary,
            "issues": issues,
            "files_checked": summary.get("files_checked", 0),
            "issues_found": summary.get("issues_found", 0),
        }
        return formatted

    except Exception as e:
        raise CSpellServiceError(
            message=f"Failed to format spell check results: {e}",
            operation="format_results",
            details=str(e),
        ) from e


# ///////////////////////////////////////////////////////////////
# EXPORT FUNCTIONS
# ///////////////////////////////////////////////////////////////


def export_spell_results_to_json(
    path: Path,
    summary: dict[str, Any],
    issues: list[dict[str, Any]],
    export_path: Path,
) -> Path:
    """Export spell check results to JSON file.

    Args:
        path: Path that was checked
        summary: Summary of the spell check
        issues: List of spelling issues
        export_path: Path to export the JSON file

    Returns:
        Path: Path to the exported JSON file

    Raises:
        SpellServiceError: If export fails
    """
    try:
        # Create export directory if it doesn't exist
        export_dir = export_path
        export_dir.mkdir(parents=True, exist_ok=True)

        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = path.name if path.is_file() else None
        filename = f"spell-check_{project_name}_{timestamp}.json"
        export_file = export_dir / filename

        # Prepare export data
        export_data: dict[str, Any] = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "path": str(path),
                "project_name": project_name,
                "export_file": str(export_file),
            },
            "summary": summary,
            "issues": issues,
        }

        # Add file-by-file analysis
        files_issues: dict[str, list[dict[str, Any]]] = {}
        for issue in issues:
            file_path = issue["file"]
            if file_path not in files_issues:
                files_issues[file_path] = []
            files_issues[file_path].append(issue)

        files_analysis: dict[str, dict[str, Any]] = {}
        for file_path, file_issues_list in files_issues.items():
            files_analysis[file_path] = {
                "total_issues": len(file_issues_list),
                "issues": file_issues_list,
            }

        export_data["files_analysis"] = files_analysis

        # Write JSON file
        with open(export_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return export_file

    except Exception as e:
        raise CSpellServiceError(
            message=f"Failed to export spell results to JSON: {e}",
            operation="export_results",
            details=f"Exception type: {type(e).__name__}",
        ) from e


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "export_spell_results_to_json",
    "format_dictionary_info",
    "format_project_status",
    "format_spell_check_results",
]
