#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SCRIPT CONFIG - Script & Icon Configuration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Script detection and icon configuration for context menu entries.

This config module exposes script type mappings, icon configurations,
and system paths used by context menu utilities and services.
"""

from __future__ import annotations

from typing import ClassVar

# ///////////////////////////////////////////////////////////////
# ICON CONFIG CLASS
# ///////////////////////////////////////////////////////////////


class IconConfig:
    """Icon configuration for context menu operations.

    Contains icon mappings for file extensions, system shortcuts,
    and paths for icon resolution.
    """

    # ///////////////////////////////////////////////////////////
    # EXTENSION TO ICON MAPPING
    # ///////////////////////////////////////////////////////////

    EXTENSION_ICONS: ClassVar[dict[str, str | None]] = {
        # Scripts
        ".py": "python.exe,0",
        ".ps1": "powershell.exe,0",
        ".bat": "cmd.exe,0",
        ".cmd": "cmd.exe,0",
        ".js": "node.exe,0",
        ".ts": "node.exe,0",
        # Documents
        ".txt": "notepad.exe,0",
        ".md": "notepad.exe,0",
        ".doc": "wordpad.exe,0",
        ".docx": "wordpad.exe,0",
        ".pdf": "AcroRd32.exe,0",
        # Images
        ".jpg": "rundll32.exe,shell32.dll,ShellImagePreview",
        ".jpeg": "rundll32.exe,shell32.dll,ShellImagePreview",
        ".png": "rundll32.exe,shell32.dll,ShellImagePreview",
        ".gif": "rundll32.exe,shell32.dll,ShellImagePreview",
        ".bmp": "rundll32.exe,shell32.dll,ShellImagePreview",
        ".ico": "rundll32.exe,shell32.dll,ShellImagePreview",
        # Archives
        ".zip": "zipfldr.dll,0",
        ".rar": "WinRAR.exe,0",
        ".7z": "7zFM.exe,0",
        ".tar": "zipfldr.dll,0",
        ".gz": "zipfldr.dll,0",
        # Code
        ".html": "mshtml.dll,0",
        ".htm": "mshtml.dll,0",
        ".css": "mshtml.dll,0",
        ".xml": "mshtml.dll,0",
        ".json": "notepad.exe,0",
        # Executables
        ".exe": None,  # Use file's own icon
        ".msi": None,  # Use file's own icon
    }

    # ///////////////////////////////////////////////////////////
    # SYSTEM ICON SHORTCUTS
    # ///////////////////////////////////////////////////////////

    SYSTEM_ICONS: ClassVar[dict[str, str | None]] = {
        "auto": None,  # Auto-detect
        "python": "python.exe,0",
        "powershell": "powershell.exe,0",
        "cmd": "cmd.exe,0",
        "node": "node.exe,0",
        "notepad": "notepad.exe,0",
        "explorer": "explorer.exe,0",
        "folder": "shell32.dll,4",
        "file": "shell32.dll,1",
        "gear": "shell32.dll,14",
        "settings": "shell32.dll,21",
    }

    # ///////////////////////////////////////////////////////////
    # SYSTEM PATHS FOR ICON SEARCH
    # ///////////////////////////////////////////////////////////

    SYSTEM_PATHS: ClassVar[list[str]] = [
        "C:\\Windows\\System32",
        "C:\\Windows",
        "C:\\Program Files",
        "C:\\Program Files (x86)",
    ]

    # ///////////////////////////////////////////////////////////
    # ICON SEPARATOR CHARACTER
    # ///////////////////////////////////////////////////////////

    ICON_SEPARATOR: ClassVar[str] = ","

    # ///////////////////////////////////////////////////////////
    # SPECIAL ICON VALUES
    # ///////////////////////////////////////////////////////////

    SPECIAL_ICON_VALUE_AUTO: ClassVar[str] = "auto"
    SPECIAL_ICON_VALUE_DEFAULT: ClassVar[str] = "default"
    SPECIAL_ICON_VALUE_NONE: ClassVar[str] = "none"


# ///////////////////////////////////////////////////////////////
# SCRIPT CONFIG CLASS
# ///////////////////////////////////////////////////////////////


class ScriptConfig:
    """Script detection and configuration for context menu.

    Contains script type detection, command templates,
    and execution parameters.
    """

    # ///////////////////////////////////////////////////////////
    # SCRIPT TYPE CONSTANTS
    # ///////////////////////////////////////////////////////////

    TYPE_PYTHON: ClassVar[str] = "python"
    TYPE_POWERSHELL: ClassVar[str] = "powershell"
    TYPE_BATCH: ClassVar[str] = "batch"
    TYPE_EXECUTABLE: ClassVar[str] = "executable"
    TYPE_UNKNOWN: ClassVar[str] = "unknown"

    # ///////////////////////////////////////////////////////////
    # EXTENSION TO SCRIPT TYPE MAPPING
    # ///////////////////////////////////////////////////////////

    EXTENSION_TO_TYPE: ClassVar[dict[str, str]] = {
        ".py": "python",
        ".ps1": "powershell",
        ".bat": "batch",
        ".cmd": "batch",
        ".exe": "executable",
        ".msi": "executable",
    }

    # ///////////////////////////////////////////////////////////
    # DEFAULT ICONS FOR SCRIPT TYPES
    # ///////////////////////////////////////////////////////////

    DEFAULT_ICONS: ClassVar[dict[str, str | None]] = {
        "python": "python.exe,0",
        "powershell": "powershell.exe,0",
        "batch": "cmd.exe,0",
        "executable": None,  # Use file's own icon
        "unknown": None,
    }

    # ///////////////////////////////////////////////////////////
    # CONTEXT PARAMETERS FOR SCRIPT TYPES
    # ///////////////////////////////////////////////////////////

    CONTEXT_PARAMETERS: ClassVar[dict[str, str]] = {
        "python": "%V",  # Directory context
        "powershell": "%V",  # Directory context
        "batch": "%V",  # Directory context
        "executable": "%V",  # Directory context
        "unknown": "%V",  # Default to directory
    }

    # ///////////////////////////////////////////////////////////
    # PYTHON INTERPRETERS TO CHECK
    # ///////////////////////////////////////////////////////////

    PYTHON_INTERPRETERS: ClassVar[list[str]] = [
        "python3",
        "python",
        "py",
    ]

    # ///////////////////////////////////////////////////////////
    # MINIMUM PYTHON VERSION (MAJOR.MINOR)
    # ///////////////////////////////////////////////////////////

    MINIMUM_PYTHON_VERSION: ClassVar[list[int]] = [3, 8]

    # ///////////////////////////////////////////////////////////
    # PYTHON LAUNCHER FALLBACK COMMAND
    # ///////////////////////////////////////////////////////////

    PYTHON_LAUNCHER_FALLBACK: ClassVar[str] = "cmd.exe /k py"

    # ///////////////////////////////////////////////////////////
    # POWERSHELL COMMAND TEMPLATE
    # ///////////////////////////////////////////////////////////

    POWERSHELL_COMMAND_TEMPLATE: ClassVar[str] = (
        "powershell.exe -ExecutionPolicy Bypass -File"
    )

    # ///////////////////////////////////////////////////////////
    # SCRIPT TYPE SET FOR DIRECT EXECUTION
    # ///////////////////////////////////////////////////////////

    DIRECT_EXECUTION_TYPES: ClassVar[set[str]] = {
        "batch",
        "executable",
    }


__all__ = ["IconConfig", "ScriptConfig"]
