#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# MANAGERS - Core Managers
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Core managers for Works On My Machine.

This package contains core manager modules for handling various aspects
of the WOMM system including dependencies, installation, and project management.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from ..utils.cli_utils import (
    CLIUtils,
    CommandResult,
    get_tool_version,
    run_command,
    run_silent,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "run_command",
    "run_silent",
    "get_tool_version",
    "CLIUtils",
    "CommandResult",
]
