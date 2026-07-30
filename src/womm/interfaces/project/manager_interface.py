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

from ...services.dependencies import probe

# Local imports
from ...shared.configs.project import ProjectConfig
from ...shared.results import (
    ProjectCreationResult,
    ProjectDetectionResult,
    ProjectSetupResult,
)
from .create_interface import ProjectCreateInterface
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
        self._create_interface = ProjectCreateInterface()
        self._setup_interface = ProjectSetupInterface()
        self._detection_interface = ProjectDetectionInterface()
        self.template_manager = TemplateInterface()
        self.logger = logging.getLogger(__name__)

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def create_project(
        self,
        project_type: str,
        project_name: str | None = None,
        current_dir: bool = False,
        dry_run: bool = False,
        minimal: bool = False,
        **kwargs,
    ) -> ProjectCreationResult:
        """
        Create a new project of the specified type.

        Args:
            project_type: Type of project to create (python, javascript, etc.)
            project_name: Name of the project
            current_dir: Whether to use current directory
            **kwargs: Additional project-specific options including 'target'

        Returns:
            ProjectCreationResult: Result of project creation
        """
        # Input validation
        if not project_type or not isinstance(project_type, str):
            return ProjectCreationResult(
                success=False,
                error="Project type is required and must be a string",
            )

        # Determine project path
        target = kwargs.get("target")

        if current_dir:
            project_path = Path.cwd()
            project_name = project_path.name
        elif target:
            # Use specified target directory
            target_path = Path(target)
            if project_name:
                project_path = target_path / project_name
            else:
                return ProjectCreationResult(
                    success=False,
                    project_type=project_type,
                    error="Project name is required when using target directory",
                )
        elif project_name:
            project_path = Path.cwd() / project_name
        else:
            return ProjectCreationResult(
                success=False,
                project_type=project_type,
                error="Project name is required when not using current directory",
            )

        # Validate project type
        type_error = self._validate_project_type(project_type)
        if type_error:
            return ProjectCreationResult(
                success=False,
                project_path=project_path,
                project_type=project_type,
                error=type_error,
            )

        # Check dependencies
        deps_error = self._check_dependencies(project_type)
        if deps_error:
            return ProjectCreationResult(
                success=False,
                project_path=project_path,
                project_type=project_type,
                error=deps_error,
            )

        # Handle dry-run mode
        if dry_run:
            return ProjectCreationResult(
                success=True,
                project_path=Path.cwd(),
                project_name=project_name or "<project>",
                project_type=project_type,
                files_created=[],
                tools_configured=[],
                warnings=["Dry-run mode: no actual changes were made"],
            )

        # Use new creation interface
        # Map JavaScript types correctly
        if project_type == "javascript":
            # Get type from kwargs (e.g., "js", "react", "vue")
            js_type_option = kwargs.get("type", "js")
            # Map type to actual project type
            type_map = {
                "js": "node",
                "ts": "node",
                "react": "react",
                "vue": "vue",
                "react-ts": "react",
                "vue-ts": "vue",
                "node": "node",
            }
            js_type = type_map.get(js_type_option, "node")
        else:
            js_type = project_type

        resolved_project_name = project_name or project_path.name
        force = kwargs.pop("force", False)
        return self._create_interface.create_project(
            project_type=js_type,
            project_name=resolved_project_name,
            project_path=project_path,
            dry_run=dry_run,
            force=force,
            minimal=minimal,
            **kwargs,
        )

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

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _validate_project_type(self, project_type: str) -> str:
        """Validate that the project type is supported.

        Returns:
            Empty string if valid, otherwise an error message.
        """
        supported_types = ["python", "javascript", "react", "vue"]
        if project_type not in supported_types:
            return f"Unsupported project type: {project_type}"
        return ""

    def _check_dependencies(self, project_type: str) -> str:
        """Check if required dependencies are available.

        Returns:
            Empty string if dependencies are satisfied, otherwise an error message.
        """
        if project_type == "python":
            result = probe("python")
            if not result.success:
                return "Python runtime not found, attempting to install..."

        elif project_type in ["javascript", "react", "vue"]:
            result = probe("node")
            if not result.success:
                return "Node.js runtime not found, attempting to install..."

        return ""

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
