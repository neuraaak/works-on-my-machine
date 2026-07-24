#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UI - User Interface Module
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
User Interface module for Works On My Machine.

This package contains UI components using Rich for beautiful terminal output.
Provides console utilities, interactive components, and display functions.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from . import common, context, cspell, dependencies, lint, project, system

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "common",
    "context",
    "cspell",
    "dependencies",
    "lint",
    "project",
    "system",
]
