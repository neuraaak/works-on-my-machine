#!/usr/bin/env python3
"""
WOMM CLI Commands Package.
Contains all command modules for the CLI interface.
"""

# Import all command modules
from . import context, lint, new, setup, spell, system, template

# Import individual commands for direct access
from .install import install, path_cmd, uninstall

__all__ = [
    "install",
    "uninstall",
    "path_cmd",
    "new",
    "lint",
    "spell",
    "system",
    "context",
    "setup",
    "template",
]
