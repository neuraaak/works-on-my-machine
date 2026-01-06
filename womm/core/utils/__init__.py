#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UTILS - Utility Modules
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Utility modules for Works On My Machine.

This package contains specialized utility modules for various functionalities
including spell checking, system operations, and project management tools.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .context import ContextParameters, ContextType, RegistryUtils, ValidationUtils
from .spell.cspell_utils import (
    check_cspell_installed,
    run_spellcheck,
    setup_project_cspell,
)
from .spell.dictionary_utils import add_all_dictionaries, get_dictionary_info

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "setup_project_cspell",
    "run_spellcheck",
    "check_cspell_installed",
    "add_all_dictionaries",
    "get_dictionary_info",
    "ContextParameters",
    "ContextType",
    "RegistryUtils",
    "ValidationUtils",
]
