#!/usr/bin/env python3
"""
Main project manager for WOMM CLI.
Orchestrates project creation and management operations.
"""

import logging
from pathlib import Path
from typing import Optional

from ...exceptions.project.project_exceptions import (
    ProjectManagerError,
    ProjectValidationError,
)
from ...ui.common.progress import create_spinner_with_status
from ...utils.project.project_detector import ProjectDetector
from ...utils.project.vscode_config import generate_vscode_config
from ..dependencies.runtime_manager import runtime_manager
from .creation.javascript_project_manager import JavaScriptProjectManager
from .creation.project_creator import ProjectCreator
from .creation.python_project_manager import PythonProjectManager
from .templates.template_manager import TemplateManager


class ProjectManager:
    """Main project manager for WOMM CLI."""

    def __init__(self):
        """Initialize the project manager.

        Raises:
            ProjectManagerError: If initialization fails
        """
        try:
            self.project_creator = ProjectCreator()
            self.python_manager = PythonProjectManager()
            self.javascript_manager = JavaScriptProjectManager()
            self.template_manager = TemplateManager()
            self.detector = ProjectDetector()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            raise ProjectManagerError(
                f"Failed to initialize project manager: {e}",
                details="Error creating component managers",
            ) from e

    def create_project(
        self,
        project_type: str,
        project_name: Optional[str] = None,
        current_dir: bool = False,
        dry_run: bool = False,
        **kwargs,
    ) -> bool:
        """
        Create a new project of the specified type.

        Args:
            project_type: Type of project to create (python, javascript, etc.)
            project_name: Name of the project
            current_dir: Whether to use current directory
            **kwargs: Additional project-specific options including 'target'

        Returns:
            True if project creation was successful

        Raises:
            ProjectValidationError: If project parameters are invalid
            ProjectManagerError: If project creation fails
        """
        try:
            # Input validation
            if not project_type or not isinstance(project_type, str):
                raise ProjectValidationError(
                    "project_creation",
                    "project_type",
                    "Project type is required and must be a string",
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
                    raise ProjectValidationError(
                        "project_creation",
                        "project_name",
                        "Project name is required when using target directory",
                    )
            elif project_name:
                project_path = Path.cwd() / project_name
            else:
                raise ProjectValidationError(
                    "project_creation",
                    "project_name",
                    "Project name is required when not using current directory",
                )

            # Validate project type
            self._validate_project_type(project_type)

            # Check dependencies
            self._check_dependencies(project_type)

            # Handle dry-run mode
            if dry_run:
                from ...ui.common.console import (
                    print_dry_run_message,
                    print_dry_run_success,
                )

                print_dry_run_message(
                    "create project", f"{project_type} project '{project_name}'"
                )
                print_dry_run_message("create project structure", f"at {project_path}")
                print_dry_run_message(
                    "setup development environment", f"for {project_type}"
                )
                print_dry_run_message(
                    "install development tools", f"for {project_type}"
                )
                print_dry_run_message(
                    "configure VSCode settings", f"for {project_type}"
                )
                print_dry_run_success()
                return True

            # Create project based on type
            if project_type == "python":
                return self.python_manager.create_project(
                    project_path, project_name, **kwargs
                )
            elif project_type in ["javascript", "react", "vue"]:
                js_type = (
                    kwargs.get("project_type", "node")
                    if project_type == "javascript"
                    else project_type
                )
                return self.javascript_manager.create_project(
                    project_path, project_name, js_type, **kwargs
                )
            else:
                raise ProjectValidationError(
                    "project_creation",
                    "project_type",
                    f"Unsupported project type: {project_type}",
                )

        except (ProjectValidationError, ProjectManagerError):
            # Re-raise our custom exceptions as-is
            raise
        except Exception as e:
            raise ProjectManagerError(
                f"Unexpected error creating project: {e}",
                details=f"Project type: {project_type}, Project name: {project_name}",
            ) from e

    def detect_project_type(
        self, project_path: Optional[Path] = None
    ) -> tuple[str, int]:
        """
        Detect the type of project in the given path.

        Args:
            project_path: Path to analyze (defaults to current directory)

        Returns:
            Tuple of (project_type, confidence_score)
        """
        detector = ProjectDetector(project_path)
        return detector.detect_project_type()

    def setup_development_environment(
        self, project_path: Path, project_type: str
    ) -> bool:
        """
        Set up development environment for an existing project.

        Args:
            project_path: Path to the project
            project_type: Type of project

        Returns:
            True if setup was successful, False otherwise
        """
        try:
            with create_spinner_with_status("Setting up development environment..."):
                # Generate VSCode configuration
                generate_vscode_config(project_path, project_type)

                # Set up project-specific environment
                if project_type == "python":
                    return self.python_manager.setup_environment(project_path)
                elif project_type in ["javascript", "react", "vue"]:
                    return self.javascript_manager.setup_environment(project_path)
                else:
                    raise ProjectManagerError(
                        f"Unsupported project type for environment setup: {project_type}",
                        details="Environment setup failed",
                    )

        except Exception as e:
            raise ProjectManagerError(
                f"Error setting up development environment: {e}",
                details=f"Project path: {project_path}, Project type: {project_type}",
            ) from e

    def _validate_project_type(self, project_type: str) -> bool:
        """Validate that the project type is supported."""
        supported_types = ["python", "javascript", "react", "vue"]
        if project_type not in supported_types:
            raise ProjectValidationError(
                "project_creation",
                "project_type",
                f"Unsupported project type: {project_type}",
            )
        return True

    def _check_dependencies(self, project_type: str) -> bool:
        """Check if required dependencies are available."""
        try:
            if project_type == "python":
                result = runtime_manager.check_runtime("python")
                if not result.success:
                    raise ProjectManagerError(
                        "Python runtime not found, attempting to install...",
                        details="Python runtime not found",
                    )

            elif project_type in ["javascript", "react", "vue"]:
                result = runtime_manager.check_runtime("node")
                if not result.success:
                    raise ProjectManagerError(
                        "Node.js runtime not found, attempting to install...",
                        details="Node.js runtime not found",
                    )

            return True

        except Exception as e:
            raise ProjectManagerError(
                f"Error checking dependencies: {e}",
                details=f"Project type: {project_type}",
            ) from e

    def get_available_project_types(self) -> list[tuple[str, str]]:
        """Get list of available project types with descriptions."""
        return [
            ("python", "Python project with virtual environment and development tools"),
            ("javascript", "JavaScript/Node.js project with npm and development tools"),
            ("react", "React.js project with modern development setup"),
            ("vue", "Vue.js project with modern development setup"),
        ]

    def get_project_templates(self, project_type: str) -> list[str]:
        """Get available templates for a project type."""
        return self.template_manager.get_templates(project_type)

    def setup_project(
        self,
        project_type: str,
        project_path: Path,
        virtual_env: bool = False,
        install_deps: bool = False,
        setup_dev_tools: bool = False,
        setup_git_hooks: bool = False,
        **kwargs,
    ) -> bool:
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
            True if setup was successful, False otherwise
        """
        try:
            # Validate project type
            self._validate_project_type(project_type)

            # Check dependencies
            self._check_dependencies(project_type)

            # Set up project based on type
            if project_type == "python":
                return self.python_manager.setup_existing_project(
                    project_path,
                    virtual_env=virtual_env,
                    install_deps=install_deps,
                    setup_dev_tools=setup_dev_tools,
                    setup_git_hooks=setup_git_hooks,
                    **kwargs,
                )
            elif project_type in ["javascript", "react", "vue"]:
                return self.javascript_manager.setup_existing_project(
                    project_path,
                    install_deps=install_deps,
                    setup_dev_tools=setup_dev_tools,
                    setup_git_hooks=setup_git_hooks,
                    **kwargs,
                )
            else:
                raise ProjectValidationError(
                    "project_setup",
                    "project_type",
                    f"Unsupported project type for setup: {project_type}",
                )

        except Exception as e:
            raise ProjectManagerError(
                f"Error setting up project: {e}",
                details=f"Project path: {project_path}, Project type: {project_type}",
            ) from e
