#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PYTHON PROJECT CREATION SERVICE - Python Project Creation Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Python Project Creation Service - Singleton service for Python project creation.

Handles Python project creation logic including:
- Project structure creation
- File generation from templates
- Virtual environment setup
- Dependency installation
- Development tools configuration
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.common import ValidationServiceError
from ...exceptions.project import ProjectServiceError, TemplateServiceError
from ...shared.configs.project import PythonProjectConfig
from ...shared.results import ProjectCreationResult
from ...utils.common import get_assets_module_path
from ...utils.project import (
    create_python_dev_config_files,
    create_python_main_files,
    create_python_requirements_files,
    create_python_structure,
    create_python_test_file,
    create_virtual_environment,
    install_python_dependencies,
    validate_project_name,
    validate_project_path,
)
from .template_service import TemplateService

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# PYTHON PROJECT CREATION SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class PythonProjectCreationService:
    """Singleton service for Python project creation operations."""

    _instance: ClassVar[PythonProjectCreationService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> PythonProjectCreationService:
        """Create or return the singleton instance.

        Returns:
            PythonProjectCreationService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize Python project creation service (only once)."""
        if PythonProjectCreationService._initialized:
            return

        self._template_service = TemplateService()
        self._template_dir = (
            get_assets_module_path() / "languages" / "python" / "py" / "templates"
        )
        self.logger = logging.getLogger(__name__)
        PythonProjectCreationService._initialized = True

    def create_project_structure(
        self, project_path: Path, project_name: str
    ) -> ProjectCreationResult:
        """Create the basic project structure.

        Args:
            project_path: Path where to create the project
            project_name: Name of the project

        Returns:
            ProjectCreationResult: Result with created directory information

        Raises:
            ProjectServiceError: If structure creation fails
            ProjectValidationError: If validation fails
        """
        try:
            created_dirs = create_python_structure(project_path, project_name)
            return ProjectCreationResult(
                success=True,
                message="Project structure created successfully",
                project_path=project_path,
                project_name=project_name,
                project_type="python",
                directories_created=(
                    created_dirs if isinstance(created_dirs, list) else []
                ),
            )

        except (ProjectServiceError, ValidationServiceError):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_project_structure: {e}")
            raise ProjectServiceError(
                message=f"Failed to create project structure: {e}",
                operation="create_project_structure",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def create_project_files(
        self, project_path: Path, project_name: str, **kwargs
    ) -> ProjectCreationResult:
        """Create Python-specific project files.

        Args:
            project_path: Path to the project
            project_name: Name of the project
            **kwargs: Additional configuration options (minimal: bool to create only basic files)

        Returns:
            ProjectCreationResult: Result with created files information

        Raises:
            ProjectServiceError: If file creation fails
            TemplateError: If template processing fails
        """
        try:
            validate_project_path(project_path)
            validate_project_name(project_name)

            minimal = kwargs.get("minimal", False)
            created_files = []

            # Create pyproject.toml (always created)
            pyproject_result = self._create_pyproject_toml(
                project_path, project_name, **kwargs
            )
            if pyproject_result.success:
                created_files.append("pyproject.toml")

            # Create main Python file (always created)
            main_files = create_python_main_files(project_path, project_name)
            if isinstance(main_files, list):
                created_files.extend(main_files)

            # In minimal mode, skip requirements, dev configs, and test files
            if not minimal:
                # Create test file
                test_files = create_python_test_file(project_path, project_name)
                if isinstance(test_files, list):
                    created_files.extend(test_files)

                # Create requirements files
                requirements_files = create_python_requirements_files(project_path)
                if isinstance(requirements_files, list):
                    created_files.extend(requirements_files)

                # Create development configuration files
                dev_config_files = create_python_dev_config_files(project_path)
                if isinstance(dev_config_files, list):
                    created_files.extend(dev_config_files)

            return ProjectCreationResult(
                success=True,
                message="Project files created successfully",
                project_path=project_path,
                project_name=project_name,
                project_type="python",
                files_created=created_files,
            )

        except (
            ProjectServiceError,
            TemplateServiceError,
            ValidationServiceError,
        ):
            raise
        except Exception as e:
            logger.error(f"Unexpected error in create_project_files: {e}")
            raise ProjectServiceError(
                message=f"Failed to create project files: {e}",
                operation="create_project_files",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def setup_virtual_environment(self, project_path: Path) -> ProjectCreationResult:
        """Set up Python virtual environment.

        Args:
            project_path: Path to the project

        Returns:
            ProjectCreationResult: Result of venv setup

        Raises:
            ProjectServiceError: If venv setup fails
        """
        try:
            result = create_virtual_environment(project_path)
            if isinstance(result, dict) and result.get("success"):
                return ProjectCreationResult(
                    success=True,
                    message="Virtual environment created successfully",
                    project_path=project_path,
                    project_type="python",
                )
            else:
                raise ProjectServiceError(
                    message="Failed to create virtual environment",
                    operation="setup_virtual_environment",
                    details="Virtual environment creation returned failure",
                )

        except ProjectServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in setup_virtual_environment: {e}")
            raise ProjectServiceError(
                message=f"Failed to setup virtual environment: {e}",
                operation="setup_virtual_environment",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def install_dev_dependencies(self, project_path: Path) -> ProjectCreationResult:
        """Install development dependencies.

        Args:
            project_path: Path to the project

        Returns:
            ProjectCreationResult: Result of dependency installation

        Raises:
            ProjectServiceError: If dependency installation fails
        """
        try:
            success = install_python_dependencies(
                project_path, PythonProjectConfig.DEV_REQUIREMENTS_FILE
            )
            return ProjectCreationResult(
                success=success,
                message=(
                    "Development dependencies installed successfully"
                    if success
                    else "Failed to install development dependencies"
                ),
                project_path=project_path,
                project_type="python",
            )

        except ProjectServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in install_dev_dependencies: {e}")
            raise ProjectServiceError(
                message=f"Failed to install development dependencies: {e}",
                operation="install_dev_dependencies",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def setup_dev_tools(self, project_path: Path) -> ProjectCreationResult:
        """Set up development tools for existing project.

        Args:
            project_path: Path to the project

        Returns:
            ProjectCreationResult: Result of dev tools setup

        Raises:
            ProjectServiceError: If dev tools setup fails
        """
        try:
            # Create development configuration files if they don't exist
            create_python_dev_config_files(project_path)

            # Install development dependencies
            return self.install_dev_dependencies(project_path)

        except ProjectServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in setup_dev_tools: {e}")
            raise ProjectServiceError(
                message=f"Failed to setup development tools: {e}",
                operation="setup_dev_tools",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def setup_git_repository(self, project_path: Path) -> ProjectCreationResult:
        """Initialize a Git repository for the project.

        Args:
            project_path: Path to the project

        Returns:
            ProjectCreationResult: Result of Git setup

        Raises:
            ProjectServiceError: If Git setup fails
        """
        try:
            self._validation_service.validate_project_path(project_path)

            # Check if git is available
            import shutil

            if not shutil.which("git"):
                logger.info("Git not found, skipping repository initialization")
                return ProjectCreationResult(
                    success=True,
                    message="Git repository setup skipped (git not found)",
                    project_path=project_path,
                    project_type="python",
                    warnings=["Git not found in system PATH"],
                )

            # Initialize git repository
            result = self._command_runner.run_command(
                ["git", "init"],
                cwd=str(project_path),
            )

            if result.success:
                return ProjectCreationResult(
                    success=True,
                    message="Git repository initialized successfully",
                    project_path=project_path,
                    project_type="python",
                )
            else:
                logger.warning(f"Failed to initialize Git repository: {result.stderr}")
                return ProjectCreationResult(
                    success=False,
                    message="Failed to initialize Git repository",
                    project_path=project_path,
                    project_type="python",
                    error=result.stderr,
                )

        except ProjectServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in setup_git_repository: {e}")
            raise ProjectServiceError(
                message=f"Failed to setup Git repository: {e}",
                operation="setup_git_repository",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _create_pyproject_toml(
        self, project_path: Path, project_name: str, **kwargs
    ) -> ProjectCreationResult:
        """Create pyproject.toml configuration file.

        Args:
            project_path: Path to the project
            project_name: Name of the project
            **kwargs: Additional configuration options

        Returns:
            ProjectCreationResult: Result of pyproject.toml creation

        Raises:
            ProjectServiceError: If pyproject.toml creation fails
            TemplateError: If template processing fails
        """
        try:
            template_path = self._template_dir / "pyproject.toml.template"
            output_path = project_path / "pyproject.toml"

            template_vars = {
                "PROJECT_NAME": project_name,
                "PROJECT_DESCRIPTION": f"{project_name} - A Python project created with WOMM CLI",
                "AUTHOR_NAME": kwargs.get("author_name", "Your Name"),
                "AUTHOR_EMAIL": kwargs.get("author_email", "your.email@example.com"),
                "PROJECT_URL": kwargs.get("project_url", ""),
                "PROJECT_REPOSITORY": kwargs.get("project_repository", ""),
                "PROJECT_DOCS_URL": kwargs.get("project_docs_url", ""),
                "PROJECT_KEYWORDS": kwargs.get(
                    "project_keywords", "python,cli,utility"
                ),
            }

            self._template_service.generate_template(
                template_path, output_path, template_vars
            )

            return ProjectCreationResult(
                success=True,
                message="pyproject.toml created successfully",
                project_path=project_path,
                project_name=project_name,
                project_type="python",
                files_created=["pyproject.toml"],
            )

        except TemplateServiceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in _create_pyproject_toml: {e}")
            raise ProjectServiceError(
                message=f"Failed to create pyproject.toml: {e}",
                operation="create_pyproject_toml",
                details=f"Exception type: {type(e).__name__}",
            ) from e
