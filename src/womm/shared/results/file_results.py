#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# FILE RESULTS - File Result Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
File result classes for Works On My Machine.

This module contains result classes for file operations:
- File operations (copy, create, delete, etc.)
- File scanning operations
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from pathlib import Path

# Local imports
from .base import BaseResult

# ///////////////////////////////////////////////////////////////
# FILE OPERATION RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class FileOperationResult(BaseResult):
    """Result for file operations."""

    operation: str = ""  # copy, create, delete, etc.
    source_path: Path | None = None
    destination_path: Path | None = None
    file_size: int = 0
    operation_time: float = 0.0


# ///////////////////////////////////////////////////////////////
# FILE SCAN RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class FileScanResult(BaseResult):
    """Result for file scanning operations."""

    target_path: Path | None = None
    total_files: int = 0
    files_found: list[Path] | None = None
    excluded_dirs: list[str] | None = None
    file_extensions: list[str] | None = None
    scan_time: float = 0.0

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.files_found is None:
            self.files_found = []
        if self.excluded_dirs is None:
            self.excluded_dirs = []
        if self.file_extensions is None:
            self.file_extensions = []


# ///////////////////////////////////////////////////////////////
# FILE SEARCH RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class FileSearchResult(BaseResult):
    """Result for finding Python files."""

    target_path: Path | None = None
    files_found: list[Path] | None = None
    recursive: bool = False
    search_time: float = 0.0

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.files_found is None:
            self.files_found = []


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "FileOperationResult",
    "FileScanResult",
    "FileSearchResult",
]
