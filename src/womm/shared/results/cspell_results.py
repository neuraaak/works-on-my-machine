#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CSPELL RESULTS - CSpell Result Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
CSpell result classes for Works On My Machine.

This module contains result classes for CSpell operations:
- Configuration operations
- Dictionary operations
- Spell checking operations
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Local imports
from .base import BaseResult

# ///////////////////////////////////////////////////////////////
# CSPELL CONFIG RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class CSpellConfigResult(BaseResult):
    """Result of CSpell configuration operations."""

    config_path: Path | None = None
    project_type: str | None = None
    words_count: int = 0
    dictionaries: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.dictionaries is None:
            self.dictionaries = []


# ///////////////////////////////////////////////////////////////
# DICTIONARY RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class DictionaryResult(BaseResult):
    """Result of dictionary operations."""

    dictionary_path: Path | None = None
    words_added: int = 0
    total_words: int = 0
    files_processed: int = 0


# ///////////////////////////////////////////////////////////////
# SPELL CHECK RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class CSpellCheckResult(BaseResult):
    """Result of a spell checking operation with detailed issues."""

    target_path: Path | None = None
    files_checked: int = 0
    issues_found: int = 0
    issues: list[dict[str, Any]] | None = None
    issues_by_file: dict[str, set[str]] | None = None  # file -> set of unknown words
    raw_output: str = ""
    raw_stderr: str = ""
    check_time: float = 0.0

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.issues is None:
            self.issues = []
        if self.issues_by_file is None:
            self.issues_by_file = {}


# ///////////////////////////////////////////////////////////////
# SPELL RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class CSpellResult(BaseResult):
    """Result of a spell checking operation."""

    data: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.data is None:
            self.data = {}


# ///////////////////////////////////////////////////////////////
# SPELL SUMMARY
# ///////////////////////////////////////////////////////////////


@dataclass
class CSpellSummary(BaseResult):
    """Summary of spell checking operations."""

    total_files: int = 0
    files_with_errors: int = 0
    total_errors: int = 0
    errors_by_file: dict[str, Any] | None = None
    suggestions: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.errors_by_file is None:
            self.errors_by_file = {}
        if self.suggestions is None:
            self.suggestions = []


# ///////////////////////////////////////////////////////////////
# CSPELL INSTALL RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class CSpellInstallResult(BaseResult):
    """Result of CSpell installation operations."""

    cspell_installed: bool = False
    version: str | None = None
    install_time: float = 0.0


# ///////////////////////////////////////////////////////////////
# PROJECT SETUP RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class ProjectSetupResult(BaseResult):
    """Result of CSpell project setup operations."""

    project_path: Path | None = None
    project_type: str | None = None
    config_created: bool = False
    setup_time: float = 0.0


# ///////////////////////////////////////////////////////////////
# ADD WORDS RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class AddWordsResult(BaseResult):
    """Result of word addition operations."""

    project_path: Path | None = None
    words: list[str] | None = None
    words_added: int = 0
    addition_time: float = 0.0

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.words is None:
            self.words = []


# ///////////////////////////////////////////////////////////////
# DICTIONARY SETUP RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class DictionarySetupResult(BaseResult):
    """Result of dictionary setup operations."""

    dictionaries_installed: bool = False
    dictionaries_count: int = 0
    setup_time: float = 0.0


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "AddWordsResult",
    "CSpellCheckResult",
    "CSpellConfigResult",
    "CSpellInstallResult",
    "CSpellResult",
    "CSpellSummary",
    "DictionaryResult",
    "DictionarySetupResult",
    "ProjectSetupResult",
]
