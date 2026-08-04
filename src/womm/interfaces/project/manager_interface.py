#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT MANAGER - Project Creation and Management
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Main project manager for WOMM CLI.

Orchestrates project creation and management operations.
Provides unified interface for creating and managing projects
across different languages and frameworks.

This interface never raises: every public method returns a typed Result.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path

# Local imports
from ...shared.configs.project import ProjectConfig
from ...shared.results import (
    ProjectDetectionResult,
    ProjectSetupResult,
)
from .detection_interface import ProjectDetectionInterface
from .setup_interface import ProjectSetupInterface
from .template_interface import TemplateInterface

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class ProjectManagerInterface:
    """Main project manager for WOMM CLI."""

    def __init__(self):
        """Initialize the project manager."""
        self._setup_interface = ProjectSetupInterface()
        self._detection_interface = ProjectDetectionInterface()
        self.template_manager = TemplateInterface()
        self.logger = logging.getLogger(__name__)

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def detect_project_type(
        self, project_path: Path | None = None
    ) -> ProjectDetectionResult:
        """
        Detect the type of project in the given path.

        Args:
            project_path: Path to analyze (defaults to current directory)

        Returns:
            ProjectDetectionResult: Detection result with project type and confidence
        """
        return self._detection_interface.detect_project_type(project_path)

    def setup_development_environment(
        self, project_path: Path, project_type: str
    ) -> ProjectSetupResult:
        """
        Set up development environment for an existing project.

        Args:
            project_path: Path to the project
            project_type: Type of project

        Returns:
            ProjectSetupResult: Result of the setup operation
        """
        return self._setup_interface.setup_development_environment(
            project_path, project_type
        )

    def get_available_project_types(self) -> list[tuple[str, str]]:
        """Get list of available project types with descriptions.

        Returns:
            List of tuples (project_type, description) from ProjectConfig
        """
        return ProjectConfig.get_project_types_for_ui()

    def get_project_templates(self, project_type: str) -> list[str]:
        """Get available templates for a project type."""
        result = self.template_manager.list_templates()
        if isinstance(result, dict):
            return result.get(project_type, [])
        return []

    def setup_project(
        self,
        project_type: str,
        project_path: Path,
        virtual_env: bool = False,
        install_deps: bool = False,
        setup_dev_tools: bool = False,
        setup_git_hooks: bool = False,
        **kwargs,
    ) -> ProjectSetupResult:
        """
        Set up an existing project with development tools and configuration.

        Args:
            project_type: Type of project (python, javascript, react, vue)
            project_path: Path to the existing project
            virtual_env: Whether to create virtual environment (Python only)
            install_deps: Whether to install dependencies
            setup_dev_tools: Whether to set up development tools
            setup_git_hooks: Whether to set up Git hooks
            **kwargs: Additional project-specific options

        Returns:
            ProjectSetupResult: Result of the setup operation
        """
        return self._setup_interface.setup_project(
            project_path=project_path,
            project_type=project_type,
            virtual_env=virtual_env,
            install_deps=install_deps,
            setup_dev_tools=setup_dev_tools,
            setup_git_hooks=setup_git_hooks,
            **kwargs,
        )
