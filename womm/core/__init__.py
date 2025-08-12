#!/usr/bin/env python3
"""
Core functionality for WOMM.

Contains all core modules for dependency management, installation,
project management, security, tools, UI, and utilities.
"""

from .dependencies import dev_tools_manager, package_manager, runtime_manager
from .ui import console, panels, progress, tables
from .utils import cli_manager, results, system_detector
from .utils.lint_manager import LintManager

# Note: SpellManager with singleton is imported only when needed to avoid startup delays

__all__ = [
    "runtime_manager",
    "package_manager",
    "dev_tools_manager",
    "SpellManager",
    "LintManager",
    "console",
    "progress",
    "panels",
    "tables",
    "cli_manager",
    "results",
    "system_detector",
]
