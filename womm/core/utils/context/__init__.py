#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UTILS CONTEXT - Context Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context utilities for WOMM CLI.

This module provides utilities for managing Windows context menu operations,
including parameter handling, registry operations, and validation.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .context_parameters import ContextParameters, ContextType
from .registry_utils import RegistryUtils
from .validation import ValidationUtils

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ContextParameters",
    "ContextType",
    "RegistryUtils",
    "ValidationUtils",
]
