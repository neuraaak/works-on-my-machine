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
from .backup_entries import ContextBackupEntriesReader
from .parameters import ContextParameters, ContextType
from .registry_paths import context_type_from_registry_path
from .registry_service import ContextRegistryService
from .validation_service import ContextValidationService

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ContextBackupEntriesReader",
    "ContextParameters",
    "ContextRegistryService",
    "ContextType",
    "ContextValidationService",
    "context_type_from_registry_path",
]
