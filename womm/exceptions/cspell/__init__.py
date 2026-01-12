#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# EXCEPTIONS CSPELL - CSpell Service Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
CSpell service exceptions for Works On My Machine.

This package exports all exceptions for spell checking operations.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .cspell_interface import (
    CSpellCheckInterfaceError,
    CSpellDictionaryInterfaceError,
    CSpellInterfaceError,
)
from .cspell_service import (
    CheckServiceError,
    CSpellServiceError,
    DictionaryServiceError,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [  # noqa: RUF022
    # cspell_interface
    "CSpellInterfaceError",
    "CSpellCheckInterfaceError",
    "CSpellCheckInterfaceError",
    "CSpellDictionaryInterfaceError",
    # cspell_service
    "CheckServiceError",
    "DictionaryServiceError",
    "CSpellServiceError",
]
