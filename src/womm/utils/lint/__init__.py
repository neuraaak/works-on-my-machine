#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# LINT UTILS - Linting Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for linting operations.

This package contains stateless utility functions for:
- Lint output parsing
- Result validation
- Tool detection and version extraction
- Exporting lint results
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .lint_utils import (
    check_tool_availability,
    export_lint_results_to_json,
    get_tool_version,
    parse_lint_output,
    validate_lint_result,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "check_tool_availability",
    "export_lint_results_to_json",
    "get_tool_version",
    "parse_lint_output",
    "validate_lint_result",
]
