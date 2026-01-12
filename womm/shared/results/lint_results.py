#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# LINT RESULTS - Lint Result Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Lint result classes for Works On My Machine.

This module contains result classes for linting operations:
- Lint summary
- Tool execution results
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from typing import Any

# Local imports
from .base import BaseResult

# ///////////////////////////////////////////////////////////////
# TOOL RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class ToolResult(BaseResult):
    """Result of a tool execution."""

    tool_name: str = ""
    files_checked: int = 0
    issues_found: int = 0
    fixed_issues: int = 0
    data: Any | None = None


# ///////////////////////////////////////////////////////////////
# LINT SUMMARY
# ///////////////////////////////////////////////////////////////


@dataclass
class LintSummaryResult(BaseResult):
    """Summary of all linting operations."""

    total_files: int = 0
    total_issues: int = 0
    total_fixed: int = 0
    tool_results: dict[str, ToolResult] | None = None
    scan_summary: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.tool_results is None:
            self.tool_results = {}


# ///////////////////////////////////////////////////////////////
# TOOL STATUS RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class ToolStatusResult(BaseResult):
    """Result of tool status retrieval."""

    tool_summary: dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.tool_summary is None:
            self.tool_summary = {}


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "LintSummaryResult",
    "ToolResult",
    "ToolStatusResult",
]
