#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# WOMM - Works On My Machine
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Works On My Machine (WOMM) - Development Environment Manager.

A comprehensive tool for managing development environments, dependencies,
and project setup across multiple programming languages.
"""

# ///////////////////////////////////////////////////////////////
# PACKAGE METADATA
# ///////////////////////////////////////////////////////////////

__version__ = "2.7.0"
__author__ = "Neuraaak"
__description__ = "Universal development tools for multiple languages - Automatic installation, cross-platform configuration, global commands"

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .cli import main
from .core.managers.dependencies.dev_tools_manager import dev_tools_manager
from .core.managers.dependencies.package_manager import package_manager
from .core.managers.dependencies.runtime_manager import runtime_manager
from .core.managers.lint.lint_manager import LintManager
from .core.managers.spell.spell_manager import SpellManager
from .languages import javascript, python

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

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
