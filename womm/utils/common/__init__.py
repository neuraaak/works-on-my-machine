#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UTILS COMMON - Common Utility Functions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Common pure utility functions for Works On My Machine.

This package contains stateless utility functions shared across the codebase:
- File scanning utilities (Python detection, path exclusion)
- Path resolution utilities (project root, assets, scripts)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .file_scanner_utils import (
    contains_security_sensitive_pattern,
    is_python_file,
    should_exclude_path,
)
from .path_resolver_utils import (
    get_assets_module_path,
    get_bin_module_path,
    get_project_root,
    get_shared_module_path,
    is_pip_installation,
    resolve_script_path,
    validate_script_exists,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "contains_security_sensitive_pattern",
    "get_assets_module_path",
    "get_bin_module_path",
    "get_project_root",
    "get_shared_module_path",
    "is_pip_installation",
    "is_python_file",
    "resolve_script_path",
    "should_exclude_path",
    "validate_script_exists",
]
