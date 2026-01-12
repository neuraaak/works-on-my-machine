#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UTILS CSPELL - CSpell Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Pure utility functions for spell checking operations.

This package contains stateless utility functions for CSpell operations
that can be used independently without class instantiation.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .cspell_utils import (
    export_spell_results_to_json,
    format_dictionary_info,
    format_project_status,
    format_spell_check_results,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "export_spell_results_to_json",
    "format_dictionary_info",
    "format_project_status",
    "format_spell_check_results",
]
