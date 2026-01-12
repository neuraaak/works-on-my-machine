#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT CREATION INTERFACE - Project Creation Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project creation interface for WOMM CLI.

Handles project creation operations following the MEF pattern.
Provides unified interface for creating Python, JavaScript, React, and Vue projects.

This interface orchestrates project creation services and converts service exceptions
to interface exceptions.
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
    CreateInterfaceError,
    ProjectServiceError,
    TemplateServiceError,
)
from ...services import (
    CommandRunnerService,
    ConflictResolutionService,
    JavaScriptProjectCreationService,
    ProjectDetectionService,
    PythonProjectCreationService,
    TemplateService,
)
from ...shared.results.project_results import ProjectCreationResult
from ...ui.common.ezpl_bridge import ezprinter
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
    handling UI interactions and orchestrating project creation services.
    """

    def __init__(self):
        """Initialize the project creation interface.

        Raises:
            ProjectCreationInterfaceError: If interface initialization fails
        """
        try:
            self._detection_service = ProjectDetectionService()
            self._template_service = TemplateService()
            self._conflict_service = ConflictResolutionService()
            self._command_runner = CommandRunnerService()
            self._python_service = PythonProjectCreationService()
            self._javascript_service = JavaScriptProjectCreationService()
            self.logger = logging.getLogger(__name__)
        except Exception as e:
            logger.error(
                f"Failed to initialize ProjectCreationInterface: {e}", exc_info=True
            )
            raise CreateInterfaceError(
                message=f"Failed to initialize project creation interface: {e}",
                operation="initialization",
                details=f"Exception type: {type(e).__name__}",
            ) from e

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

        Raises:
            ProjectCreationInterfaceError: If project creation fails
        """
        try:
            # Validate inputs
            validate_project_type(project_type)
            validate_project_name(project_name)
            validate_project_path(project_path)

            # Handle dry-run mode
            if dry_run:
                return self._handle_dry_run(
                    project_type, project_name, project_path, **kwargs
                )

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
                raise CreateInterfaceError(
                    message=f"Unsupported project type: {project_type}",
                    operation="create_project",
                    project_type=project_type,
                    details="Supported types: python, javascript, react, vue",
                )

        except ValidationServiceError as e:
            logger.error(f"Validation error in create_project: {e}", exc_info=True)
            # Extract meaningful error message
            error_message = (
                e.message or e.reason or str(e) or "Project validation failed"
            )
            raise CreateInterfaceError(
                message=f"Project validation failed: {error_message}",
                operation="create_project",
                project_path=str(project_path),
                project_type=project_type,
                details=e.details or str(e),
            ) from e
        except (ProjectServiceError, TemplateServiceError) as e:
            logger.error(f"Service error in create_project: {e}", exc_info=True)
            raise CreateInterfaceError(
                message=f"Project creation failed: {e.message}",
                operation="create_project",
                project_path=str(project_path),
                project_type=project_type,
                details=e.details or str(e),
            ) from e
        except CreateInterfaceError:
            # Re-raise interface exceptions as-is
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_project: {e}", exc_info=True)
            raise CreateInterfaceError(
                message=f"Unexpected error during project creation: {e}",
                operation="create_project",
                project_path=str(project_path),
                project_type=project_type,
                details=f"Exception type: {type(e).__name__}",
            ) from e

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
        ezprinter.print_header("Project Creation (DRY RUN)")
        ezprinter.info(f"Would create {project_type} project '{project_name}'")
        ezprinter.info(f"Project path: {project_path}")
        ezprinter.info("Would create project structure")
        ezprinter.info("Would setup development environment")
        ezprinter.info("Would install development tools")
        ezprinter.info("Would configure VSCode settings")
        ezprinter.success("Dry-run completed successfully")

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
            force: If True, overwrite existing files without prompting
            **kwargs: Additional configuration options (minimal: bool for minimal setup)

        Returns:
            ProjectCreationResult: Result of the project creation operation

        Raises:
            ProjectCreationInterfaceError: If project creation fails
        """
        try:
            minimal = kwargs.get("minimal", False)
            mode_text = " (minimal)" if minimal else ""
            ezprinter.print_header(f"Creating Python Project{mode_text}")
            ezprinter.info(f"Project: {project_name}")
            ezprinter.info(f"Path: {project_path}")

            # Create project structure
            with ezprinter.create_spinner_with_status(
                "Creating project structure..."
            ) as spinner:
                structure_result = self._python_service.create_project_structure(
                    project_path, project_name
                )
                if not structure_result.get("success"):
                    raise CreateInterfaceError(
                        message="Failed to create project structure",
                        operation="create_python_project",
                        project_path=str(project_path),
                        project_type="python",
                        details="Structure creation returned failure",
                    )
                spinner.update_status("Project structure created")

            # Create project files
            with ezprinter.create_spinner_with_status(
                "Creating Python files..."
            ) as spinner:
                files_result = self._python_service.create_project_files(
                    project_path, project_name, **kwargs
                )
                if not files_result.get("success"):
                    raise CreateInterfaceError(
                        message="Failed to create project files",
                        operation="create_python_project",
                        project_path=str(project_path),
                        project_type="python",
                        details="File creation returned failure",
                    )
                spinner.update_status("Python files created")

            # Skip environment setup, dependencies, and tools in minimal mode
            if not minimal:
                # Setup virtual environment
                with ezprinter.create_spinner_with_status(
                    "Setting up virtual environment..."
                ) as spinner:
                    venv_result = self._python_service.setup_virtual_environment(
                        project_path
                    )
                    if not venv_result.get("success"):
                        raise CreateInterfaceError(
                            message="Failed to setup virtual environment",
                            operation="create_python_project",
                            project_path=str(project_path),
                            project_type="python",
                            details="Venv setup returned failure",
                        )
                    spinner.update_status("Virtual environment ready")

                # Install development dependencies
                with ezprinter.create_spinner_with_status(
                    "Installing development dependencies..."
                ) as spinner:
                    deps_result = self._python_service.install_dev_dependencies(
                        project_path
                    )
                    if not deps_result.get("success"):
                        raise CreateInterfaceError(
                            message="Failed to install development dependencies",
                            operation="create_python_project",
                            project_path=str(project_path),
                            project_type="python",
                            details="Dependency installation returned failure",
                        )
                    spinner.update_status("Dependencies installed")

                # Setup development tools
                with ezprinter.create_spinner_with_status(
                    "Configuring development tools..."
                ) as spinner:
                    tools_result = self._python_service.setup_dev_tools(project_path)
                    if not tools_result.get("success"):
                        raise CreateInterfaceError(
                            message="Failed to setup development tools",
                            operation="create_python_project",
                            project_path=str(project_path),
                            project_type="python",
                            details="Dev tools setup returned failure",
                        )
                    spinner.update_status("Development tools configured")

                # Setup Git repository
                with ezprinter.create_spinner_with_status(
                    "Setting up Git repository..."
                ) as spinner:
                    git_result = self._python_service.setup_git_repository(project_path)
                    if git_result.get("skipped"):
                        spinner.update_status("Git setup skipped")
                    else:
                        spinner.update_status("Git repository initialized")

            files_created = files_result.get("files", [])
            tools_configured = (
                self._get_configured_tools(project_path, "python")
                if not minimal
                else []
            )
            ezprinter.success(f"Python project '{project_name}' created successfully")

            return ProjectCreationResult(
                success=True,
                project_path=project_path,
                project_name=project_name,
                project_type="python",
                files_created=files_created,
                tools_configured=tools_configured,
            )

        except CreateInterfaceError:
            raise
        except (ProjectServiceError, TemplateServiceError) as e:
            logger.error(f"Service error in _create_python_project: {e}", exc_info=True)
            raise CreateInterfaceError(
                message=f"Python project creation failed: {e.message}",
                operation="create_python_project",
                project_path=str(project_path),
                project_type="python",
                details=e.details or str(e),
            ) from e
        except Exception as e:
            logger.error(f"Error creating Python project: {e}", exc_info=True)
            raise CreateInterfaceError(
                message=f"Failed to create Python project: {e}",
                operation="create_python_project",
                project_path=str(project_path),
                project_type="python",
                details=f"Exception type: {type(e).__name__}",
            ) from e

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
            force: If True, overwrite existing files without prompting
            **kwargs: Additional configuration options (minimal: bool for minimal setup)

        Returns:
            ProjectCreationResult: Result of the project creation operation

        Raises:
            ProjectCreationInterfaceError: If project creation fails
        """
        try:
            minimal = kwargs.get("minimal", False)
            mode_text = " (minimal)" if minimal else ""
            ezprinter.print_header(f"Creating JavaScript Project{mode_text}")
            ezprinter.info(f"Project: {project_name}")
            ezprinter.info(f"Path: {project_path}")
            ezprinter.info(f"Type: {project_type}")

            # Create project structure
            with ezprinter.create_spinner_with_status(
                "Creating project structure..."
            ) as spinner:
                structure_result = self._javascript_service.create_project_structure(
                    project_path, project_name
                )
                if not structure_result.get("success"):
                    raise CreateInterfaceError(
                        message="Failed to create project structure",
                        operation="create_javascript_project",
                        project_path=str(project_path),
                        project_type=project_type,
                        details="Structure creation returned failure",
                    )
                spinner.update_status("Project structure created")

            # Create project files
            with ezprinter.create_spinner_with_status(
                "Creating JavaScript files..."
            ) as spinner:
                files_result = self._javascript_service.create_project_files(
                    project_path, project_name, project_type, **kwargs
                )
                if not files_result.get("success"):
                    raise CreateInterfaceError(
                        message="Failed to create project files",
                        operation="create_javascript_project",
                        project_path=str(project_path),
                        project_type=project_type,
                        details="File creation returned failure",
                    )
                spinner.update_status("JavaScript files created")

            # Skip npm init, dependencies, and tools in minimal mode
            if not minimal:
                # Initialize npm project
                with ezprinter.create_spinner_with_status(
                    "Initializing npm project..."
                ) as spinner:
                    npm_result = self._javascript_service.initialize_npm_project(
                        project_path, project_name, **kwargs
                    )
                    if not npm_result.get("success"):
                        raise CreateInterfaceError(
                            message="Failed to initialize npm project",
                            operation="create_javascript_project",
                            project_path=str(project_path),
                            project_type=project_type,
                            details="npm initialization returned failure",
                        )
                    spinner.update_status("npm project initialized")

                # Install dependencies
                with ezprinter.create_spinner_with_status(
                    "Installing dependencies..."
                ) as spinner:
                    deps_result = self._javascript_service.install_dependencies(
                        project_path, project_type
                    )
                    if not deps_result.get("success"):
                        raise CreateInterfaceError(
                            message="Failed to install dependencies",
                            operation="create_javascript_project",
                            project_path=str(project_path),
                            project_type=project_type,
                            details="Dependency installation returned failure",
                        )
                    spinner.update_status("Dependencies installed")

                # Setup development tools
                with ezprinter.create_spinner_with_status(
                    "Configuring development tools..."
                ) as spinner:
                    tools_result = self._javascript_service.setup_dev_tools(
                        project_path, project_type
                    )
                    if not tools_result.get("success"):
                        raise CreateInterfaceError(
                            message="Failed to setup development tools",
                            operation="create_javascript_project",
                            project_path=str(project_path),
                            project_type=project_type,
                            details="Dev tools setup returned failure",
                        )
                    spinner.update_status("Development tools configured")

                # Setup Git repository
                with ezprinter.create_spinner_with_status(
                    "Setting up Git repository..."
                ) as spinner:
                    git_result = self._javascript_service.setup_git_repository(
                        project_path
                    )
                    if git_result.get("skipped"):
                        spinner.update_status("Git setup skipped")
                    else:
                        spinner.update_status("Git repository initialized")

            files_created = files_result.get("files", [])
            tools_configured = (
                self._get_configured_tools(project_path, "javascript")
                if not minimal
                else []
            )
            ezprinter.success(
                f"JavaScript project '{project_name}' created successfully"
            )

            return ProjectCreationResult(
                success=True,
                project_path=project_path,
                project_name=project_name,
                project_type=project_type,
                files_created=files_created,
                tools_configured=tools_configured,
            )

        except CreateInterfaceError:
            raise
        except (ProjectServiceError, TemplateServiceError) as e:
            logger.error(
                f"Service error in _create_javascript_project: {e}", exc_info=True
            )
            raise CreateInterfaceError(
                message=f"JavaScript project creation failed: {e.message}",
                operation="create_javascript_project",
                project_path=str(project_path),
                project_type=project_type,
                details=e.details or str(e),
            ) from e
        except Exception as e:
            logger.error(f"Error creating JavaScript project: {e}", exc_info=True)
            raise CreateInterfaceError(
                message=f"Failed to create JavaScript project: {e}",
                operation="create_javascript_project",
                project_path=str(project_path),
                project_type=project_type,
                details=f"Exception type: {type(e).__name__}",
            ) from e

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
