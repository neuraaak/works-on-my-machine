#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPENDENCIES UTILS - Dependencies Utility Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependencies utility functions for Works On My Machine.

This package contains pure utility functions for:
- Package manager operations
- Runtime management
- Development tools management
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .devtools_utils import (
    detect_installation_method,
    get_all_tools_for_language,
    get_tool_type_for_language,
    resolve_tool_path,
)
from .runtime_utils import (
    compare_versions,
    get_package_name_for_manager,
    parse_version,
    satisfies_min_version,
)
from .system_package_manager_utils import (
    build_install_command,
    build_search_command,
    extract_first_line_version,
    extract_version_from_output,
    select_best_manager,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "build_install_command",
    "build_search_command",
    "compare_versions",
    "detect_installation_method",
    "extract_first_line_version",
    "extract_version_from_output",
    "get_all_tools_for_language",
    "get_package_name_for_manager",
    "get_tool_type_for_language",
    "parse_version",
    "resolve_tool_path",
    "satisfies_min_version",
    "select_best_manager",
]
