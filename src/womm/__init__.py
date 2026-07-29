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

from ._version import __version__

# ///////////////////////////////////////////////////////////////
# PACKAGE METADATA
# ///////////////////////////////////////////////////////////////

__author__ = "Neuraaak"
__maintainer__ = "Neuraaak"
__description__ = (
    "Universal development tools for multiple languages - "
    "Automatic installation, cross-platform configuration, global commands"
)
__python_requires__ = ">=3.13"
__keywords__ = ["logging", "rich", "loguru", "console", "file"]
__url__ = "https://github.com/neuraaak/works-on-my-machine"
__repository__ = "https://github.com/neuraaak/works-on-my-machine"

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////


def main() -> None:
    """CLI entry point wrapper to avoid early heavy imports."""
    from .cli import main as _main

    _main()


__all__ = [
    "__version__",
    "__author__",
    "__maintainer__",
    "__description__",
    "__python_requires__",
    "__keywords__",
    "__url__",
    "__repository__",
    "main",
]
