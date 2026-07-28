#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# JAVASCRIPT PROJECT CREATION SERVICE - JavaScript Project Creation Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
JavaScript Project Creation Service - Singleton service for JavaScript project creation.

Handles JavaScript/Node.js/React/Vue project creation logic including:
- Project structure creation
- File generation from templates
- npm project initialization
- Dependency installation
- Development tools configuration
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import logging
import shutil
from pathlib import Path
from threading import Lock
from typing import Any, ClassVar

# Local imports
from ...exceptions.project import ProjectServiceError
from ...shared.results import ProjectCreationResult
from ...utils.common import get_assets_module_path
from ...utils.project import (
    check_npm_available,
    create_javascript_config_files,
    create_javascript_source_files,
    create_javascript_structure,
    install_npm_dependencies,
    install_npm_dev_dependencies,
    validate_project_name,
    validate_project_path,
)
from ..common.command_runner_service import CommandRunnerService
from .template_service import TemplateService

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

JAVASCRIPT_PROJECT_TYPES = frozenset({"javascript", "node", "react", "vue"})
JAVASCRIPT_TEMPLATE_VARIANTS = {
    "javascript": "js",
    "node": "js",
    "react": "react",
    "vue": "vue",
}


def _validate_javascript_project_type(project_type: str) -> None:
    """Validate a JavaScript service project type."""
    if project_type not in JAVASCRIPT_PROJECT_TYPES:
        supported_types = ", ".join(sorted(JAVASCRIPT_PROJECT_TYPES))
        raise ValueError(
            f"Unsupported JavaScript project type: {project_type}. "
            f"Supported types: {supported_types}"
        )


# ///////////////////////////////////////////////////////////////
# JAVASCRIPT PROJECT CREATION SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class JavaScriptProjectCreationService:
    """Singleton service for JavaScript project creation operations."""

    _instance: ClassVar[JavaScriptProjectCreationService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> JavaScriptProjectCreationService:
        """Create or return the singleton instance.

        Returns:
            JavaScriptProjectCreationService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize JavaScript project creation service (only once)."""
        if JavaScriptProjectCreationService._initialized:
            return

        self._template_service = TemplateService()
        self._command_runner = CommandRunnerService()
        self._template_dir = get_assets_module_path() / "languages" / "javascript"
        self.logger = logging.getLogger(__name__)
        JavaScriptProjectCreationService._initialized = True

    def create_project_structure(
        self, project_path: Path, project_name: str, project_type: str = "node"
    ) -> ProjectCreationResult:
        """Create the basic project structure.

        Args:
            project_path: Path where to create the project
            project_name: Name of the project
            project_type: Type of JavaScript project (node, react, vue)

        Returns:
            ProjectCreationResult: Result with created directory information

        Raises:
            ProjectServiceError: If structure creation or validation fails
        """
        try:
            validate_project_path(project_path)
            validate_project_name(project_name)
            _validate_javascript_project_type(project_type)
            created_dirs = create_javascript_structure(project_path, project_name)
            return ProjectCreationResult(
                success=True,
                message="Project structure created successfully",
                project_path=project_path,
                project_name=project_name,
                project_type=project_type,
                directories_created=(
                    created_dirs if isinstance(created_dirs, list) else []
                ),
            )

        except ProjectServiceError:
            raise
        except Exception as e:
            logger.exception("Unexpected error in create_project_structure")
            raise ProjectServiceError(
                operation="create_project_structure",
                reason=str(e),
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def create_project_files(
        self,
        project_path: Path,
        project_name: str,
        project_type: str,
        **kwargs,
    ) -> ProjectCreationResult:
        """Create JavaScript-specific project files.

        Args:
            project_path: Path to the project
            project_name: Name of the project
            project_type: Type of JavaScript project (node, react, vue)
            **kwargs: Additional configuration options

        Returns:
            ProjectCreationResult: Result with created files information

        Raises:
            ProjectServiceError: If file creation or template processing fails
        """
        try:
            validate_project_path(project_path, must_exist=True, require_empty=False)
            validate_project_name(project_name)
            _validate_javascript_project_type(project_type)

            created_files = []

            # Create package.json
            package_result = self._create_package_json(
                project_path, project_name, project_type, **kwargs
            )
            if package_result.get("success"):
                created_files.append("package.json")

            # Create source files based on project type (always created)
            source_files = create_javascript_source_files(
                project_path, project_name, project_type
            )
            if isinstance(source_files, list):
                created_files.extend(source_files)

            # In minimal mode, skip dev config files
            minimal = kwargs.get("minimal", False)
            if not minimal:
                # Create configuration files
                config_files = create_javascript_config_files(project_path)
                if isinstance(config_files, list):
                    created_files.extend(config_files)

            return ProjectCreationResult(
                success=True,
                message="Project files created successfully",
                project_path=project_path,
                project_name=project_name,
                project_type=project_type,
                files_created=created_files,
            )

        except ProjectServiceError:
            raise
        except Exception as e:
            logger.exception("Unexpected error in create_project_files")
            raise ProjectServiceError(
                operation="create_project_files",
                reason=str(e),
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def initialize_npm_project(
        self,
        project_path: Path,
        _project_name: str,
        **kwargs,  # noqa: ARG002
    ) -> ProjectCreationResult:
        """Initialize npm project.

        Args:
            project_path: Path to the project
            project_name: Name of the project
            **kwargs: Additional configuration options

        Returns:
            ProjectCreationResult: Result of npm initialization

        Raises:
            ProjectServiceError: If npm project initialization fails
        """
        try:
            validate_project_path(project_path, must_exist=True, require_empty=False)

            # Check if npm is available
            if not check_npm_available():
                raise ProjectServiceError(
                    operation="initialize_npm_project",
                    reason="npm is not installed or not in PATH",
                    details="npm command not found in PATH",
                )

            # package.json already created, so initialization is complete
            return ProjectCreationResult(
                success=True,
                message="npm project initialized successfully",
                project_path=project_path,
                project_name=_project_name,
            )

        except ProjectServiceError:
            raise
        except Exception as e:
            logger.exception("initialize_npm_project failed")
            raise ProjectServiceError(
                operation="initialize_npm_project",
                reason=str(e),
                details=f"Exception type: {type(e).__name__}",
            ) from e

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
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _create_package_json(
        self, project_path: Path, project_name: str, project_type: str, **kwargs
    ) -> dict[str, Any]:
        """Create package.json configuration file.

        Args:
            project_path: Path to the project
            project_name: Name of the project
            project_type: Type of JavaScript project (node, react, vue)
            **kwargs: Additional configuration options

        Returns:
            dict: Metadata about file creation with 'success' key

        Raises:
            ProjectServiceError: If package.json creation or template processing fails
        """
        try:
            template_variant = JAVASCRIPT_TEMPLATE_VARIANTS[project_type]
            template_path = (
                self._template_dir
                / template_variant
                / "templates"
                / "package.json.template"
            )
            output_path = project_path / "package.json"

            # Base template variables
            template_vars = {
                "PROJECT_NAME": project_name,
                "PROJECT_DESCRIPTION": f"{project_name} - A JavaScript project created with WOMM CLI",
                "AUTHOR_NAME": kwargs.get("author_name", "Your Name"),
                "AUTHOR_EMAIL": kwargs.get("author_email", "your.email@example.com"),
                "PROJECT_URL": kwargs.get("project_url", ""),
                "PROJECT_REPOSITORY": kwargs.get("project_repository", ""),
                "PROJECT_DOCS_URL": kwargs.get("project_docs_url", ""),
                "PROJECT_KEYWORDS": kwargs.get(
                    "project_keywords", "javascript,node,cli"
                ),
                "MAIN_FILE": "src/main.js",
                "MODULE_TYPE": "commonjs",
                "DEV_COMMAND": "node src/main.js",
                "BUILD_COMMAND": "echo 'No build step required'",
                "START_COMMAND": "node src/main.js",
                "KEYWORDS": "javascript,node,cli",
                "JEST_ENVIRONMENT": "node",
                "DEPENDENCIES": "",
                "DEV_DEPENDENCIES": "",
                "PREPARE_SCRIPT": "",
            }

            # Add project type specific variables
            if project_type == "react":
                template_vars.update(
                    {
                        "PROJECT_TYPE": "react",
                        "FRAMEWORK_NAME": "React",
                        "FRAMEWORK_VERSION": "^18.2.0",
                        "MAIN_FILE": "src/index.jsx",
                        "MODULE_TYPE": "module",
                        "DEV_COMMAND": "react-scripts start",
                        "BUILD_COMMAND": "react-scripts build",
                        "START_COMMAND": "react-scripts start",
                        "KEYWORDS": "react,javascript,frontend",
                        "JEST_ENVIRONMENT": "jsdom",
                        "DEPENDENCIES": "",
                        "DEV_DEPENDENCIES": "",
                    }
                )
            elif project_type == "vue":
                template_vars.update(
                    {
                        "PROJECT_TYPE": "vue",
                        "FRAMEWORK_NAME": "Vue",
                        "FRAMEWORK_VERSION": "^3.3.0",
                        "MAIN_FILE": "src/main.js",
                        "MODULE_TYPE": "module",
                        "DEV_COMMAND": "vue-cli-service serve",
                        "BUILD_COMMAND": "vue-cli-service build",
                        "START_COMMAND": "vue-cli-service serve",
                        "KEYWORDS": "vue,javascript,frontend",
                        "JEST_ENVIRONMENT": "jsdom",
                        "DEPENDENCIES": "",
                        "DEV_DEPENDENCIES": "",
                    }
                )
            else:  # node
                template_vars.update(
                    {
                        "PROJECT_TYPE": "node",
                        "FRAMEWORK_NAME": "Node.js",
                        "FRAMEWORK_VERSION": "^18.0.0",
                        "MAIN_FILE": "src/main.js",
                        "MODULE_TYPE": "commonjs",
                        "DEV_COMMAND": "node src/main.js",
                        "BUILD_COMMAND": "echo 'No build step required'",
                        "START_COMMAND": "node src/main.js",
                        "KEYWORDS": "javascript,node,cli",
                        "JEST_ENVIRONMENT": "node",
                        "DEPENDENCIES": "",
                        "DEV_DEPENDENCIES": "",
                    }
                )

            # Generate the package.json content
            self._template_service.generate_template(
                template_path, output_path, template_vars
            )

            json.loads(output_path.read_text(encoding="utf-8"))

            return {"success": True}

        except Exception as e:
            raise ProjectServiceError(
                operation="create_package_json",
                reason=str(e),
                details=f"Exception type: {type(e).__name__}",
            ) from e
