#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UI CSPELL - CSpell UI Components
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
CSpell UI components for Works On My Machine.

This module provides UI components for spell checking operations,
including issue displays and summaries.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .display import (
    create_spell_progress_table,
    display_lint_summary,
    display_spell_issues_table,
    display_spell_status_table,
    display_spell_summary,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "create_spell_progress_table",
    "display_lint_summary",
    "display_spell_issues_table",
    "display_spell_status_table",
    "display_spell_summary",
]
