#!/usr/bin/env python3
"""
Works On My Machine (WOMM) - Modular CLI Package.
Universal development tools for Python and JavaScript projects.
Enhanced with comprehensive security validation.
"""

__version__ = "1.0.0"
__author__ = "Works On My Machine Team"
__description__ = "Universal development tools for Python and JavaScript projects"

# Import main CLI group for easy access
from .cli import womm

__all__ = ["womm"]
