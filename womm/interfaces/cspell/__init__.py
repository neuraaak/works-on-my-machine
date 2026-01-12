#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# INTERFACES SPELL - Spell Checking Interfaces
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Spell checking interfaces for Works On My Machine.

This package contains spell checking interface modules that orchestrate services
for CSpell integration and word validation.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .checker_interface import CSpellCheckerInterface
from .dictionary_interface import CSpellDictionaryInterface

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "CSpellCheckerInterface",
    "CSpellDictionaryInterface",
]
