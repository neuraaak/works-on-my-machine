#!/usr/bin/env python3
"""
Works On My Machine (WOMM) - Modular CLI Package.
Universal development tools for Python and JavaScript projects.
Enhanced with comprehensive security validation.
"""

# CONSTANTS
########################################################
# Package metadata and version information

__version__ = "1.6.0"
__author__ = "Works On My Machine Team"
__description__ = "Universal development tools for Python and JavaScript projects"

# IMPORTS
########################################################
# Main CLI group import for easy access

from .cli import womm

# EXPORTS
########################################################
# Public API exports

__all__ = ["womm"]
