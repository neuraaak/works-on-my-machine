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
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.project import (
    ProjectServiceError,
)
from ...shared.configs.project import ProjectConfig
from ...shared.results import (
    ProjectCreationResult,
    ProjectDetectionResult,
    ProjectSetupResult,
)
from ...ui.common import ezprinter
from ..dependencies.runtime_interface import (
    RuntimeInterface,
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
        """Initialize the project manager.

        Raises:
            ProjectServiceError: If initialization fails
        """
        try:
            self._create_interface = ProjectCreateInterface()
            self._setup_interface = ProjectSetupInterface()
            self._detection_interface = ProjectDetectionInterface()
            self.template_manager = TemplateInterface()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            raise ProjectServiceError(
                f"Failed to initialize project manager: {e}",
                details="Error creating component managers",
            ) from e

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

        Raises:
            ProjectValidationError: If project parameters are invalid
            ProjectServiceError: If project creation fails
        """
        try:
            # Input validation
            if not project_type or not isinstance(project_type, str):
                raise ValidationServiceError(
                    message="Project type is required and must be a string",
                    validation_type="project_type",
                    operation="project_creation",
                    reason="Project type is required and must be a string",
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
                    raise ValidationServiceError(
                        message="Project name is required when using target directory",
                        validation_type="project_name",
                        operation="project_creation",
                        reason="Project name is required when using target directory",
                    )
            elif project_name:
                project_path = Path.cwd() / project_name
            else:
                raise ValidationServiceError(
                    message="Project name is required when not using current directory",
                    validation_type="project_name",
                    operation="project_creation",
                    reason="Project name is required when not using current directory",
                )

            # Validate project type
            self._validate_project_type(project_type)

            # Check dependencies
            self._check_dependencies(project_type)

            # Handle dry-run mode
            if dry_run:
                ezprinter.print_dry_run_message(
                    "create project", f"{project_type} project '{project_name}'"
                )
                ezprinter.print_dry_run_message(
                    "create project structure", f"at {project_path}"
                )
                ezprinter.print_dry_run_message(
                    "setup development environment", f"for {project_type}"
                )
                ezprinter.print_dry_run_message(
                    "install development tools", f"for {project_type}"
                )
                ezprinter.print_dry_run_message(
                    "configure VSCode settings", f"for {project_type}"
                )
                ezprinter.print_dry_run_success()
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

            result = self._create_interface.create_project(
                project_type=js_type,
                project_name=project_name,
                project_path=project_path,
                dry_run=dry_run,
                force=kwargs.get("force", False),
                minimal=minimal,
                **kwargs,
            )
            return result

        except (ValidationServiceError, ProjectServiceError):
            # Re-raise our custom exceptions as-is
            raise
        except Exception as e:
            raise ProjectServiceError(
                f"Unexpected error creating project: {e}",
                details=f"Project type: {project_type}, Project name: {project_name}",
            ) from e

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
        result = self._detection_interface.detect_project_type(project_path)
        return result

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
        result = self._setup_interface.setup_development_environment(
            project_path, project_type
        )
        return result

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _validate_project_type(self, project_type: str) -> bool:
        """Validate that the project type is supported."""
        supported_types = ["python", "javascript", "react", "vue"]
        if project_type not in supported_types:
            raise ValidationServiceError(
                message=f"Unsupported project type: {project_type}",
                validation_type="project_type",
                operation="project_creation",
                reason=f"Unsupported project type: {project_type}",
            )
        return True

    def _check_dependencies(self, project_type: str) -> bool:
        """Check if required dependencies are available."""
        try:
            if project_type == "python":
                runtime_manager = RuntimeInterface()
                result = runtime_manager.check_runtime("python")
                if not result.success:
                    raise ProjectServiceError(
                        "Python runtime not found, attempting to install...",
                        details="Python runtime not found",
                    )

            elif project_type in ["javascript", "react", "vue"]:
                runtime_manager = RuntimeInterface()
                result = runtime_manager.check_runtime("node")
                if not result.success:
                    raise ProjectServiceError(
                        "Node.js runtime not found, attempting to install...",
                        details="Node.js runtime not found",
                    )

            return True

        except Exception as e:
            raise ProjectServiceError(
                f"Error checking dependencies: {e}",
                details=f"Project type: {project_type}",
            ) from e

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
        result = self._setup_interface.setup_project(
            project_path=project_path,
            project_type=project_type,
            virtual_env=virtual_env,
            install_deps=install_deps,
            setup_dev_tools=setup_dev_tools,
            setup_git_hooks=setup_git_hooks,
            **kwargs,
        )
        return result
