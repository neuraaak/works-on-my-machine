#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT CREATION INTERFACE - Project Creation Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project creation interface for WOMM CLI.

Handles project creation operations following the MEF pattern.
Provides unified interface for creating Python, JavaScript, React, and Vue projects.

This interface orchestrates project creation services and converts service
exceptions into a typed ``ProjectCreationResult`` — it never raises.
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
from ...exceptions.project import ProjectServiceError
from ...services import (
    CommandRunnerService,
    ConflictResolutionService,
    JavaScriptEnvironmentService,
    JavaScriptProjectCreationService,
    ProjectDetectionService,
    PythonEnvironmentService,
    PythonProjectCreationService,
    TemplateService,
)
from ...shared.results import ProjectCreationResult
from ...utils.project import (
    validate_project_name,
    validate_project_path,
    validate_project_type,
)

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class ProjectCreateInterface:
    """Project creation interface for project operations.

    This class provides a high-level interface for project creation operations,
    orchestrating project creation services without rendering terminal output.
    """

    def __init__(self):
        """Initialize the project creation interface."""
        self._detection_service = ProjectDetectionService()
        self._template_service = TemplateService()
        self._conflict_service = ConflictResolutionService()
        self._command_runner = CommandRunnerService()
        self._python_service = PythonProjectCreationService()
        self._javascript_service = JavaScriptProjectCreationService()
        self._python_environment_service = PythonEnvironmentService()
        self._javascript_environment_service = JavaScriptEnvironmentService()
        self.logger = logging.getLogger(__name__)

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def create_project(
        self,
        project_type: str,
        project_name: str,
        project_path: Path,
        dry_run: bool = False,
        force: bool = False,
        **kwargs,
    ) -> ProjectCreationResult:
        """
        Create a new project.

        Args:
            project_type: Type of project to create (python, javascript, react, vue)
            project_name: Name of the project
            project_path: Path where to create the project
            dry_run: If True, show what would be done without making changes
            force: If True, overwrite existing files without prompting
            **kwargs: Additional configuration options

        Returns:
            ProjectCreationResult: Result of the project creation operation
        """
        try:
            # Validate inputs
            validate_project_type(project_type)
            validate_project_name(project_name)

            # Handle dry-run mode
            if dry_run:
                return self._handle_dry_run(
                    project_type, project_name, project_path, **kwargs
                )

            self._conflict_service.validate_project_destination(project_path, force)
            validate_project_path(project_path, require_empty=not force)

            # Create project based on type
            if project_type == "python":
                return self._create_python_project(
                    project_name, project_path, force, **kwargs
                )
            elif project_type in ["javascript", "react", "vue", "node"]:
                # If project_type is "javascript", determine actual type from type option
                if project_type == "javascript":
                    js_type_option = kwargs.get("type", "js")
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
                return self._create_javascript_project(
                    project_name, project_path, js_type, force, **kwargs
                )
            else:
                return ProjectCreationResult(
                    success=False,
                    project_path=project_path,
                    project_type=project_type,
                    error=(
                        f"Unsupported project type: {project_type}. "
                        "Supported types: python, javascript, react, vue"
                    ),
                )

        except (ValidationServiceError, ValueError, OSError) as e:
            logger.error(f"Validation error in create_project: {e}", exc_info=True)
            error_message = getattr(e, "reason", str(e)) or "Project validation failed"
            return ProjectCreationResult(
                success=False,
                project_path=project_path,
                project_type=project_type,
                error=f"Project validation failed: {error_message}",
            )
        except ProjectServiceError as e:
            logger.error(f"Service error in create_project: {e}", exc_info=True)
            return ProjectCreationResult(
                success=False,
                project_path=project_path,
                project_type=project_type,
                error=f"Project creation failed: {e.reason}",
            )
        except Exception as e:
            logger.error(f"Unexpected error in create_project: {e}", exc_info=True)
            return ProjectCreationResult(
                success=False,
                project_path=project_path,
                project_type=project_type,
                error=f"Unexpected error during project creation: {e}",
            )

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _handle_dry_run(
        self,
        project_type: str,
        project_name: str,
        project_path: Path,
        **kwargs,  # noqa: ARG002
    ) -> ProjectCreationResult:
        """Handle dry-run mode for project creation.

        Args:
            project_type: Type of project to create
            project_name: Name of the project
            project_path: Path where to create the project
            **kwargs: Additional configuration options

        Returns:
            ProjectCreationResult: Result indicating dry-run mode
        """
        return ProjectCreationResult(
            success=True,
            project_path=project_path,
            project_name=project_name,
            project_type=project_type,
            files_created=[],
            tools_configured=[],
            warnings=["Dry-run mode: no actual changes were made"],
        )

    def _create_python_project(
        self,
        project_name: str,
        project_path: Path,
        force: bool,  # noqa: ARG002
        **kwargs,
    ) -> ProjectCreationResult:
        """Create a Python project.

        Args:
            project_name: Name of the project
            project_path: Path where to create the project
            force: If True, merge generated files into an existing directory
            **kwargs: Additional configuration options (minimal: bool for minimal setup)

        Returns:
            ProjectCreationResult: Result of the project creation operation
        """
        try:
            minimal = kwargs.get("minimal", False)

            # Create project structure
            structure_result = self._python_service.create_project_structure(
                project_path, project_name
            )
            if not structure_result.success:
                return ProjectCreationResult(
                    success=False,
                    project_path=project_path,
                    project_type="python",
                    error="Failed to create project structure",
                )

            # Create project files
            files_result = self._python_service.create_project_files(
                project_path, project_name, **kwargs
            )
            if not files_result.success:
                return ProjectCreationResult(
                    success=False,
                    project_path=project_path,
                    project_type="python",
                    error="Failed to create project files",
                )

            # Skip environment setup, dependencies, and tools in minimal mode
            if not minimal:
                # Setup virtual environment
                venv_result = (
                    self._python_environment_service.setup_virtual_environment(
                        project_path
                    )
                )
                if not venv_result.success:
                    return ProjectCreationResult(
                        success=False,
                        project_path=project_path,
                        project_type="python",
                        error="Failed to setup virtual environment",
                    )

                # Setup development tools and install development dependencies
                tools_result = self._python_environment_service.setup_dev_tools(
                    project_path
                )
                if not tools_result.success:
                    return ProjectCreationResult(
                        success=False,
                        project_path=project_path,
                        project_type="python",
                        error="Failed to setup development tools",
                    )

                # Setup Git repository
                git_result = self._python_environment_service.setup_git_repository(
                    project_path
                )
                if not git_result.success:
                    return ProjectCreationResult(
                        success=False,
                        project_path=project_path,
                        project_type="python",
                        error="Failed to setup Git repository",
                    )

            files_created = files_result.files_created or []
            tools_configured = (
                self._get_configured_tools(project_path, "python")
                if not minimal
                else []
            )
            return ProjectCreationResult(
                success=True,
                project_path=project_path,
                project_name=project_name,
                project_type="python",
                files_created=files_created,
                tools_configured=tools_configured,
            )

        except ProjectServiceError as e:
            logger.error(f"Service error in _create_python_project: {e}", exc_info=True)
            return ProjectCreationResult(
                success=False,
                project_path=project_path,
                project_type="python",
                error=f"Python project creation failed: {e.reason}",
            )
        except Exception as e:
            logger.error(f"Error creating Python project: {e}", exc_info=True)
            return ProjectCreationResult(
                success=False,
                project_path=project_path,
                project_type="python",
                error=f"Failed to create Python project: {e}",
            )

    def _create_javascript_project(
        self,
        project_name: str,
        project_path: Path,
        project_type: str,
        force: bool,  # noqa: ARG002
        **kwargs,
    ) -> ProjectCreationResult:
        """Create a JavaScript/React/Vue project.

        Args:
            project_name: Name of the project
            project_path: Path where to create the project
            project_type: JavaScript project type (node, react, vue)
            force: If True, merge generated files into an existing directory
            **kwargs: Additional configuration options (minimal: bool for minimal setup)

        Returns:
            ProjectCreationResult: Result of the project creation operation
        """
        try:
            minimal = kwargs.get("minimal", False)

            # Create project structure
            structure_result = self._javascript_service.create_project_structure(
                project_path, project_name, project_type
            )
            if not structure_result.success:
                return ProjectCreationResult(
                    success=False,
                    project_path=project_path,
                    project_type=project_type,
                    error="Failed to create project structure",
                )

            # Create project files
            files_result = self._javascript_service.create_project_files(
                project_path, project_name, project_type, **kwargs
            )
            if not files_result.success:
                return ProjectCreationResult(
                    success=False,
                    project_path=project_path,
                    project_type=project_type,
                    error="Failed to create project files",
                )

            # Skip npm init, dependencies, and tools in minimal mode
            if not minimal:
                # Initialize npm project
                npm_result = self._javascript_service.initialize_npm_project(
                    project_path, project_name, **kwargs
                )
                if not npm_result.success:
                    return ProjectCreationResult(
                        success=False,
                        project_path=project_path,
                        project_type=project_type,
                        error="Failed to initialize npm project",
                    )

                # Install dependencies
                deps_result = self._javascript_environment_service.install_dependencies(
                    project_path, project_type
                )
                if not deps_result.success:
                    return ProjectCreationResult(
                        success=False,
                        project_path=project_path,
                        project_type=project_type,
                        error="Failed to install dependencies",
                    )

                # Setup development tools
                tools_result = self._javascript_environment_service.setup_dev_tools(
                    project_path, project_type
                )
                if not tools_result.success:
                    return ProjectCreationResult(
                        success=False,
                        project_path=project_path,
                        project_type=project_type,
                        error="Failed to setup development tools",
                    )

                # Setup Git repository
                git_result = self._javascript_environment_service.setup_git_repository(
                    project_path
                )
                if not git_result.success:
                    return ProjectCreationResult(
                        success=False,
                        project_path=project_path,
                        project_type=project_type,
                        error="Failed to setup Git repository",
                    )

            files_created = files_result.files_created or []
            tools_configured = (
                self._get_configured_tools(project_path, "javascript")
                if not minimal
                else []
            )
            return ProjectCreationResult(
                success=True,
                project_path=project_path,
                project_name=project_name,
                project_type=project_type,
                files_created=files_created,
                tools_configured=tools_configured,
            )

        except ProjectServiceError as e:
            logger.error(
                f"Service error in _create_javascript_project: {e}", exc_info=True
            )
            return ProjectCreationResult(
                success=False,
                project_path=project_path,
                project_type=project_type,
                error=f"JavaScript project creation failed: {e.reason}",
            )
        except Exception as e:
            logger.error(f"Error creating JavaScript project: {e}", exc_info=True)
            return ProjectCreationResult(
                success=False,
                project_path=project_path,
                project_type=project_type,
                error=f"Failed to create JavaScript project: {e}",
            )

    def _get_created_files(self, project_path: Path) -> list[str]:
        """Get list of created files in the project.

        Args:
            project_path: Path to the project

        Returns:
            List of created file paths (relative to project_path)
        """
        try:
            files = []
            if project_path.exists():
                for file_path in project_path.rglob("*"):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(project_path)
                        files.append(str(relative_path))
            return sorted(files)
        except Exception as e:
            logger.warning(f"Failed to enumerate created files: {e}")
            return []

    def _get_configured_tools(
        self, project_path: Path, _project_type: str
    ) -> list[str]:
        """Get list of configured development tools.

        Args:
            project_path: Path to the project
            project_type: Type of project

        Returns:
            List of configured tool names
        """
        tools = []
        try:
            # Check for common configuration files
            if (project_path / "pyproject.toml").exists():
                tools.append("pyproject.toml")
            if (project_path / "package.json").exists():
                tools.append("package.json")
            if (project_path / ".vscode").exists():
                tools.append("VSCode")
            if (project_path / ".git").exists():
                tools.append("Git")
            if (project_path / ".venv").exists() or (project_path / "venv").exists():
                tools.append("Virtual Environment")
        except Exception as e:
            logger.warning(f"Failed to enumerate configured tools: {e}")
        return tools
