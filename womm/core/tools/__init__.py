"""
Tools modules for Works On My Machine.

This package contains specialized tools like CSpell and dictionary management.
"""

from .cspell_manager import (
    check_cspell_installed,
    install_cspell_global,
    run_spellcheck,
    setup_project_cspell,
)
from .dictionary_manager import add_all_dictionaries, get_dictionary_info

__all__ = [
    "install_cspell_global",
    "setup_project_cspell",
    "run_spellcheck",
    "check_cspell_installed",
    "add_all_dictionaries",
    "get_dictionary_info",
]
