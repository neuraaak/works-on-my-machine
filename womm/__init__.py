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

from pathlib import Path

# ///////////////////////////////////////////////////////////////
# PACKAGE METADATA
# ///////////////////////////////////////////////////////////////

__version__ = "3.2.1"
__author__ = "Neuraaak"
__description__ = (
    "Universal development tools for multiple languages - "
    "Automatic installation, cross-platform configuration, global commands"
)

# ///////////////////////////////////////////////////////////////
# PROOF FILE DETECTION
# ///////////////////////////////////////////////////////////////

# Check if proof file exists in current womm package directory
_WOMM_DIR = Path(__file__).parent
HAS_PROOF_FILE = (_WOMM_DIR / ".proof").exists()

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////


def main() -> None:
    """CLI entry point wrapper to avoid early heavy imports."""
    from .cli import main as _main

    _main()


__all__ = [
    "HAS_PROOF_FILE",
    "__author__",
    "__description__",
    "__version__",
    "main",
]
