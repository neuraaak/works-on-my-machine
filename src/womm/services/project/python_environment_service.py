#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PYTHON ENVIRONMENT SERVICE - Python Environment Setup Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Python Environment Service - Singleton service for Python environment setup.

Handles post-creation Python environment setup including:
- Virtual environment setup
- Dependency installation
- Development tools configuration
- Git repository initialization
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
from ...exceptions.project import ProjectServiceError
from ...shared.configs.project import PythonProjectConfig
from ...shared.results import ProjectCreationResult
from ...utils.project import create_python_dev_config_files, validate_project_path
from ..common.command_runner_service import CommandRunnerService
from .env_utils import create_virtual_environment, install_python_dependencies

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# PYTHON ENVIRONMENT SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class PythonEnvironmentService:
    """Singleton service for Python environment setup operations."""

    _instance: ClassVar[PythonEnvironmentService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> PythonEnvironmentService:
        """Create or return the singleton instance.

        Returns:
            PythonEnvironmentService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize Python environment service (only once)."""
        if PythonEnvironmentService._initialized:
            return

        self._command_runner = CommandRunnerService()
        self.logger = logging.getLogger(__name__)
        PythonEnvironmentService._initialized = True

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
                    operation="setup_virtual_environment",
                    reason="Virtual environment creation returned failure",
                )

        except ProjectServiceError:
            raise
        except Exception as e:
            logger.exception("Unexpected error in setup_virtual_environment")
            raise ProjectServiceError(
                operation="setup_virtual_environment",
                reason=str(e),
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
            logger.exception("Unexpected error in install_dev_dependencies")
            raise ProjectServiceError(
                operation="install_dev_dependencies",
                reason=str(e),
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
            logger.exception("Unexpected error in setup_dev_tools")
            raise ProjectServiceError(
                operation="setup_dev_tools",
                reason=str(e),
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
            validate_project_path(project_path, must_exist=True, require_empty=False)

            # Check if git is available
            import shutil

            git_path = shutil.which("git")
            if not git_path:
                logger.info("Git not found, skipping repository initialization")
                return ProjectCreationResult(
                    success=True,
                    message="Git repository setup skipped (git not found)",
                    project_path=project_path,
                    project_type="python",
                    warnings=["Git not found in system PATH"],
                )

            # Initialize git repository
            result = self._command_runner.run(
                [git_path, "init"],
                description="Initialize Git repository",
                cwd=project_path,
            )

            if result.returncode == 0:
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
            logger.exception("Unexpected error in setup_git_repository")
            raise ProjectServiceError(
                operation="setup_git_repository",
                reason=str(e),
                details=f"Exception type: {type(e).__name__}",
            ) from e


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["PythonEnvironmentService"]
