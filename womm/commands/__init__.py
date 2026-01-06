#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# COMMANDS - CLI Commands Package
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
WOMM CLI Commands Package.

This package contains all command modules for the WOMM CLI interface.
Each module represents a specific command group with related functionality.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .context import context_group
from .install import install, path_cmd, uninstall
from .lint import lint_group
from .new import new_group
from .setup import setup_group
from .spell import spell_group
from .system import system_group
from .template import template_group

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Installation commands
    "install",
    "uninstall",
    "path_cmd",
    # Project commands
    "new_group",
    "setup_group",
    "template_group",
    # System commands
    "system_group",
    # Quality commands
    "spell_group",
    "lint_group",
    # Context commands
    "context_group",
]
