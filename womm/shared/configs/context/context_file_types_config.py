#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT FILE TYPES CONFIG - File Type Extensions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Configuration for context menu file type extensions.

This config class exposes file type extension mappings used by
context menu utilities for file categorization.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from typing import ClassVar

# ///////////////////////////////////////////////////////////////
# CLASS DEFINITION
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class ContextFileTypesConfig:
    """Context menu file types configuration (static, read-only).

    Contains file extension mappings for different file categories
    used in context menu operations.
    """

    # ///////////////////////////////////////////////////////////
    # FILE TYPE EXTENSIONS
    # ///////////////////////////////////////////////////////////

    FILE_TYPE_EXTENSIONS: ClassVar[dict[str, set[str]]] = {
        "image": {
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".tiff",
            ".webp",
            ".svg",
            ".ico",
        },
        "text": {
            ".txt",
            ".md",
            ".py",
            ".js",
            ".html",
            ".css",
            ".json",
            ".xml",
            ".csv",
            ".log",
        },
        "archive": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".cab"},
        "document": {
            ".pdf",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
            ".odt",
            ".ods",
            ".odp",
        },
        "media": {
            ".mp3",
            ".mp4",
            ".avi",
            ".mkv",
            ".wav",
            ".flac",
            ".mov",
            ".wmv",
            ".flv",
        },
        "code": {
            ".py",
            ".js",
            ".ts",
            ".java",
            ".cpp",
            ".c",
            ".h",
            ".cs",
            ".php",
            ".rb",
            ".go",
            ".rs",
        },
    }

    # ///////////////////////////////////////////////////////////
    # HELPER METHODS
    # ///////////////////////////////////////////////////////////

    @classmethod
    def get_file_type(cls, extension: str) -> str | None:
        """Get the file type for an extension.

        Args:
            extension: File extension (with dot)

        Returns:
            File type name or None if not categorized
        """
        ext_lower = extension.lower()
        for file_type, extensions in cls.FILE_TYPE_EXTENSIONS.items():
            if ext_lower in extensions:
                return file_type
        return None

    @classmethod
    def get_extensions_for_type(cls, file_type: str) -> set[str]:
        """Get extensions for a file type.

        Args:
            file_type: File type name (image, text, archive, etc.)

        Returns:
            Set of extensions or empty set if type not found
        """
        return cls.FILE_TYPE_EXTENSIONS.get(file_type, set())

    @classmethod
    def get_all_file_types(cls) -> list[str]:
        """Get all available file types.

        Returns:
            List of file type names
        """
        return list(cls.FILE_TYPE_EXTENSIONS.keys())

    @classmethod
    def get_all_extensions(cls) -> dict[str, set[str]]:
        """Get a copy of all file type extensions.

        Returns:
            Copy of FILE_TYPE_EXTENSIONS dict
        """
        return cls.FILE_TYPE_EXTENSIONS.copy()


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["ContextFileTypesConfig"]
