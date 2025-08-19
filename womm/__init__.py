#!/usr/bin/env python3
"""
Works On My Machine (WOMM) - Development Environment Manager

A comprehensive tool for managing development environments, dependencies,
and project setup across multiple programming languages.

Author: WOMM Team
"""

__version__ = "2.3.0"
__author__ = "WOMM Team"
__description__ = "Development Environment Manager"

# Core exports
# Main CLI entry point
from .cli import main
from .core.managers.dependencies.dev_tools_manager import dev_tools_manager
from .core.managers.dependencies.package_manager import package_manager
from .core.managers.dependencies.runtime_manager import runtime_manager
from .core.managers.lint.lint_manager import LintManager
from .core.managers.spell.spell_manager import SpellManager

# Language support
from .languages import javascript, python

__all__ = [
    "__version__",
    "__author__",
    "__description__",
    "runtime_manager",
    "package_manager",
    "dev_tools_manager",
    "SpellManager",
    "LintManager",
    "python",
    "javascript",
    "main",
]
