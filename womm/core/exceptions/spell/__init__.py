#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS SPELL - Spell Checking Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Spell checking exceptions for Works On My Machine.

This package contains custom exceptions used specifically by spell checking modules:
- SpellManager (womm/core/managers/spell/spell_manager.py)
- Spell utilities (womm/core/utils/spell/cspell_utils.py, dictionary_utils.py)

Following a pragmatic approach with focused exception types:
1. SpellUtilityError - Base exception for spell checking utilities
2. CSpellError - CSpell-specific errors
3. DictionaryError - Dictionary management errors
4. SpellManagerError - Base exception for spell manager
5. SpellValidationError - Spell validation errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .spell_exceptions import (
    CSpellError,
    DictionaryError,
    SpellManagerError,
    SpellUtilityError,
    SpellValidationError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    # Base exception
    "SpellUtilityError",
    # CSpell exceptions
    "CSpellError",
    # Dictionary exceptions
    "DictionaryError",
    # Manager exceptions
    "SpellManagerError",
    "SpellValidationError",
]
