#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# JAVASCRIPT ENVIRONMENT SERVICE - JavaScript Environment Setup Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
JavaScript Environment Service - Singleton service for JavaScript environment setup.

Handles post-creation JavaScript/Node.js/React/Vue environment setup including:
- Dependency installation
- Development tools configuration
- Git repository initialization
- Git hooks setup
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import shutil
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.project import ProjectServiceError
from ...shared.results import ProjectCreationResult
from ...utils.project import validate_project_path
from ..common.command_runner_service import CommandRunnerService
from .env_utils import install_npm_dependencies, install_npm_dev_dependencies

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

JAVASCRIPT_PROJECT_TYPES = frozenset({"javascript", "node", "react", "vue"})


def _validate_javascript_project_type(project_type: str) -> None:
    """Validate a JavaScript service project type."""
    if project_type not in JAVASCRIPT_PROJECT_TYPES:
        supported_types = ", ".join(sorted(JAVASCRIPT_PROJECT_TYPES))
        raise ValueError(
            f"Unsupported JavaScript project type: {project_type}. "
            f"Supported types: {supported_types}"
        )


# ///////////////////////////////////////////////////////////////
# JAVASCRIPT ENVIRONMENT SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class JavaScriptEnvironmentService:
    """Singleton service for JavaScript environment setup operations."""

    _instance: ClassVar[JavaScriptEnvironmentService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> JavaScriptEnvironmentService:
        """Create or return the singleton instance.

        Returns:
            JavaScriptEnvironmentService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize JavaScript environment service (only once)."""
        if JavaScriptEnvironmentService._initialized:
            return

        self._command_runner = CommandRunnerService()
        self.logger = logging.getLogger(__name__)
        JavaScriptEnvironmentService._initialized = True

    def install_dependencies(
        self,
        project_path: Path,
        project_type: str,
    ) -> ProjectCreationResult:
        """Install project dependencies.

        Args:
            project_path: Path to the project
            project_type: Type of JavaScript project (node, react, vue)

        Returns:
            ProjectCreationResult: Result of dependency installation

        Raises:
            ProjectServiceError: If dependency installation fails
        """
        try:
            validate_project_path(project_path, must_exist=True, require_empty=False)
            _validate_javascript_project_type(project_type)

            success = install_npm_dependencies(project_path)
            if not success:
                raise ProjectServiceError(
                    operation="install_dependencies",
                    reason="npm install command failed",
                    details="npm install did not complete successfully",
                )

            return ProjectCreationResult(
                success=True,
                message="Dependencies installed successfully",
                project_path=project_path,
                project_type=project_type,
            )

        except ProjectServiceError:
            raise
        except Exception as e:
            logger.exception("install_dependencies failed")
            raise ProjectServiceError(
                operation="install_dependencies",
                reason=str(e),
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def setup_dev_tools(
        self, project_path: Path, project_type: str
    ) -> ProjectCreationResult:
        """Set up development tools.

        Args:
            project_path: Path to the project
            project_type: Type of JavaScript project (node, react, vue)

        Returns:
            ProjectCreationResult: Result of dev tools setup

        Raises:
            ProjectServiceError: If development tools setup fails
        """
        try:
            validate_project_path(project_path, must_exist=True, require_empty=False)
            _validate_javascript_project_type(project_type)

            # Check if npm is available
            if not shutil.which("npm"):
                raise ProjectServiceError(
                    operation="setup_dev_tools",
                    reason="npm is not installed or not in PATH",
                    details="npm command not found in PATH",
                )

            # Install development dependencies
            dev_dependencies = [
                "eslint",
                "prettier",
                "husky",
                "lint-staged",
                "@types/node",
            ]

            # Add type-specific dev dependencies
            if project_type == "react":
                dev_dependencies.extend(
                    [
                        "@types/react",
                        "@types/react-dom",
                        "@testing-library/react",
                        "@testing-library/jest-dom",
                    ]
                )
            elif project_type == "vue":
                dev_dependencies.extend(
                    [
                        "@vue/cli-service",
                        "@vue/compiler-sfc",
                    ]
                )

            # Install dev dependencies
            success = install_npm_dev_dependencies(project_path, dev_dependencies)
            if not success:
                raise ProjectServiceError(
                    operation="setup_dev_tools",
                    reason="Failed to install development tools",
                    details="npm install dev tools command failed",
                )

            return ProjectCreationResult(
                success=True,
                message="Development tools installed successfully",
                project_path=project_path,
                project_type=project_type,
            )

        except ProjectServiceError:
            raise
        except Exception as e:
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

            # Initialize git repository using CommandRunnerService
            git_path = shutil.which("git")
            if not git_path:
                logger.info("Git not found, skipping repository initialization")
                return ProjectCreationResult(
                    success=True,
                    message="Git repository setup skipped (git not found)",
                    project_path=project_path,
                    warnings=["Git not found in system PATH"],
                )
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
                )
            else:
                logger.warning(f"Failed to initialize Git repository: {result.stderr}")
                return ProjectCreationResult(
                    success=False,
                    message="Failed to initialize Git repository",
                    project_path=project_path,
                    error=result.stderr,
                )

        except ProjectServiceError:
            raise
        except Exception as e:
            raise ProjectServiceError(
                operation="setup_git_repository",
                reason=str(e),
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def setup_git_hooks(self, project_path: Path) -> ProjectCreationResult:
        """Set up Git hooks with Husky.

        Args:
            project_path: Path to the project

        Returns:
            ProjectCreationResult: Result of Git hooks setup

        Raises:
            ProjectServiceError: If Git hooks setup fails
        """
        try:
            validate_project_path(project_path, must_exist=True, require_empty=False)

            # Initialize husky using CommandRunnerService
            npx_path = shutil.which("npx")
            if not npx_path:
                logger.warning("npx not found, skipping Git hooks setup")
                return ProjectCreationResult(
                    success=True,
                    message="Git hooks setup skipped (npx not found)",
                    project_path=project_path,
                    warnings=["npx not found in system PATH"],
                )
            result = self._command_runner.run(
                [npx_path, "husky", "install"],
                description="Install Husky Git hooks",
                cwd=project_path,
            )

            if result.returncode == 0:
                hook_result = self._command_runner.run(
                    [
                        npx_path,
                        "husky",
                        "add",
                        ".husky/pre-commit",
                        "npm run lint-staged",
                    ],
                    description="Add pre-commit hook",
                    cwd=project_path,
                )
                if hook_result.returncode != 0:
                    return ProjectCreationResult(
                        success=False,
                        message="Failed to create Git pre-commit hook",
                        project_path=project_path,
                        error=hook_result.stderr,
                    )
                return ProjectCreationResult(
                    success=True,
                    message="Git hooks installed successfully",
                    project_path=project_path,
                )
            else:
                return ProjectCreationResult(
                    success=False,
                    message="Failed to initialize Husky",
                    project_path=project_path,
                    error=result.stderr,
                )

        except ProjectServiceError:
            raise
        except Exception as e:
            raise ProjectServiceError(
                operation="setup_git_hooks",
                reason=str(e),
                details=f"Exception type: {type(e).__name__}",
            ) from e


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["JavaScriptEnvironmentService"]
