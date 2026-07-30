#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SERVICES CONTEXT - Context Services
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Context services for WOMM CLI.

This module provides services for managing Windows context menu operations,
including parameter handling, registry operations, and validation.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .parameters import ContextParameters, ContextType
from .registry_service import ContextRegistryService
from .validation_service import ContextValidationService

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ContextParameters",
    "ContextRegistryService",
    "ContextType",
    "ContextValidationService",
]
