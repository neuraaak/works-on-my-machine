#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# COMMAND RESULTS - Command Result Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Command result classes for Works On My Machine.

This module contains result classes for command operations:
- Command availability
- Command version information
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass

# Local imports
from .base import BaseResult

# ///////////////////////////////////////////////////////////////
# COMMAND AVAILABILITY RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class CommandAvailabilityResult(BaseResult):
    """Result of command availability check."""

    command_name: str = ""
    is_available: bool = False
    security_validated: bool = False


# ///////////////////////////////////////////////////////////////
# COMMAND VERSION RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class CommandVersionResult(BaseResult):
    """Result of command version retrieval."""

    command_name: str = ""
    version: str = ""
    version_flag: str = "--version"


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "CommandAvailabilityResult",
    "CommandVersionResult",
]
