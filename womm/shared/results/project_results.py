#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT RESULTS - Project Result Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project result classes for Works On My Machine.

This module contains result classes for project operations:
- Project detection
- Project creation
- Project setup
- Template operations
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
# SETUP RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class SetupResult(BaseResult):
    """Result for project setup operations."""

    project_path: Path | None = None
    project_name: str = ""
    files_created: list[str] | None = None
    tools_configured: list[str] | None = None
    warnings: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.files_created is None:
            self.files_created = []
        if self.tools_configured is None:
            self.tools_configured = []
        if self.warnings is None:
            self.warnings = []


# ///////////////////////////////////////////////////////////////
# PROJECT DETECTION RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class ProjectDetectionResult(BaseResult):
    """Result for project type detection."""

    project_type: str = ""
    confidence: float = 0.0
    detected_files: list[str] | None = None
    configuration_files: dict[str, str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.detected_files is None:
            self.detected_files = []
        if self.configuration_files is None:
            self.configuration_files = {}


# ///////////////////////////////////////////////////////////////
# PROJECT CREATION RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class ProjectCreationResult(BaseResult):
    """Result for project creation operations."""

    project_path: Path | None = None
    project_name: str = ""
    project_type: str = ""
    files_created: list[str] | None = None
    directories_created: list[str] | None = None
    tools_configured: list[str] | None = None
    warnings: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.files_created is None:
            self.files_created = []
        if self.directories_created is None:
            self.directories_created = []
        if self.tools_configured is None:
            self.tools_configured = []
        if self.warnings is None:
            self.warnings = []


# ///////////////////////////////////////////////////////////////
# PROJECT SETUP RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class ProjectSetupResult(BaseResult):
    """Result for project setup operations."""

    project_path: Path | None = None
    project_name: str = ""
    project_type: str = ""
    files_modified: list[str] | None = None
    tools_configured: list[str] | None = None
    warnings: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.files_modified is None:
            self.files_modified = []
        if self.tools_configured is None:
            self.tools_configured = []
        if self.warnings is None:
            self.warnings = []


# ///////////////////////////////////////////////////////////////
# TEMPLATE RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class TemplateResult(BaseResult):
    """Result for template operations."""

    template_name: str = ""
    template_path: Path | None = None
    project_type: str = ""
    files_processed: int = 0
    files_created: list[str] | None = None
    metadata: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.files_created is None:
            self.files_created = []
        if self.metadata is None:
            self.metadata = {}


# ///////////////////////////////////////////////////////////////
# CONFIGURATION RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class ConfigurationResult(BaseResult):
    """Result for configuration operations."""

    config_type: str = ""  # vscode, git, cspell, etc.
    config_files: list[str] | None = None
    settings_applied: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.config_files is None:
            self.config_files = []
        if self.settings_applied is None:
            self.settings_applied = {}


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ConfigurationResult",
    "ProjectCreationResult",
    "ProjectDetectionResult",
    "ProjectSetupResult",
    "SetupResult",
    "TemplateResult",
]
