#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT DETECTOR - Project Detection Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project Detector - Utilities for detecting project types and configurations.

Handles project type detection, configuration file analysis, and project structure validation.
Provides comprehensive project analysis capabilities for various development environments.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path

# Local imports
# Import specialized exceptions
from ...exceptions.project import ProjectDetectionError, ProjectUtilityError

# ///////////////////////////////////////////////////////////////
# PROJECT DETECTOR CLASS
# ///////////////////////////////////////////////////////////////


class ProjectDetector:
    """Detects project types and configurations."""

    # Project type indicators
    PROJECT_INDICATORS = {
        "python": {
            "files": ["setup.py", "pyproject.toml", "requirements.txt", "Pipfile"],
            "dirs": ["__pycache__", ".pytest_cache", ".mypy_cache"],
            "extensions": [".py", ".pyi"],
        },
        "javascript": {
            "files": ["package.json", "yarn.lock", "pnpm-lock.yaml"],
            "dirs": ["node_modules", ".next", ".nuxt"],
            "extensions": [".js", ".jsx", ".ts", ".tsx"],
        },
        "java": {
            "files": ["pom.xml", "build.gradle", "gradle.properties"],
            "dirs": ["target", "build", ".gradle"],
            "extensions": [".java", ".kt"],
        },
        "go": {
            "files": ["go.mod", "go.sum", "Gopkg.toml"],
            "dirs": ["vendor", "bin"],
            "extensions": [".go"],
        },
        "rust": {
            "files": ["Cargo.toml", "Cargo.lock"],
            "dirs": ["target", ".cargo"],
            "extensions": [".rs"],
        },
        "csharp": {
            "files": ["*.csproj", "*.sln", "packages.config"],
            "dirs": ["bin", "obj", "packages"],
            "extensions": [".cs", ".csx"],
        },
    }

    def __init__(self):
        """Initialize project detector."""
        self.logger = logging.getLogger(__name__)

    def detect_project_type(self, project_path: Path) -> str | None:
        """Detect the type of project at the given path.

        Args:
            project_path: Path to the project directory

        Returns:
            str | None: Detected project type or None if unknown

        Raises:
            ProjectUtilityError: If input validation fails
            ProjectDetectionError: If project detection fails
        """
        try:
            # Input validation
            if not project_path:
                raise ProjectUtilityError(
                    message="Project path cannot be None",
                    details="Empty project path provided for project type detection",
                )

            if not project_path.exists():
                raise ProjectDetectionError(
                    operation="detect_project_type",
                    project_path=str(project_path),
                    reason="Project path does not exist",
                    details=f"Path {project_path} was not found",
                )

            if not project_path.is_dir():
                raise ProjectDetectionError(
                    operation="detect_project_type",
                    project_path=str(project_path),
                    reason="Project path is not a directory",
                    details=f"Path {project_path} is not a directory",
                )

            # Analyze project structure
            project_files = list(project_path.iterdir())
            project_dirs = [item for item in project_files if item.is_dir()]
            project_files = [item for item in project_files if item.is_file()]

            # Check each project type
            for project_type, indicators in self.PROJECT_INDICATORS.items():
                if self._matches_project_type(project_files, project_dirs, indicators):
                    return project_type

            return None

        except (ProjectUtilityError, ProjectDetectionError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise ProjectUtilityError(
                message=f"Unexpected error during project type detection: {e}",
                details=f"Exception type: {type(e).__name__}, Project: {project_path}",
            ) from e

    def detect_project_config(self, project_path: Path) -> dict[str, str | bool | int]:
        """Detect project configuration files and settings.

        Args:
            project_path: Path to the project directory

        Returns:
            dict[str, str | bool | int]: Project configuration information

        Raises:
            ProjectUtilityError: If input validation fails
            ProjectDetectionError: If project configuration detection fails
        """
        try:
            # Input validation
            if not project_path:
                raise ProjectUtilityError(
                    message="Project path cannot be None",
                    details="Empty project path provided for project configuration detection",
                )

            if not project_path.exists():
                raise ProjectDetectionError(
                    operation="detect_project_config",
                    project_path=str(project_path),
                    reason="Project path does not exist",
                    details=f"Path {project_path} was not found",
                )

            if not project_path.is_dir():
                raise ProjectDetectionError(
                    operation="detect_project_config",
                    project_path=str(project_path),
                    reason="Project path is not a directory",
                    details=f"Path {project_path} is not a directory",
                )

            config = {
                "project_type": None,
                "config_files": {},
                "dependencies": {},
                "build_tools": [],
                "ide_configs": [],
            }

            # Detect project type first
            project_type = self.detect_project_type(project_path)
            config["project_type"] = project_type

            # Analyze configuration files based on project type
            if project_type == "python":
                config.update(self._analyze_python_config(project_path))
            elif project_type == "javascript":
                config.update(self._analyze_javascript_config(project_path))
            elif project_type == "java":
                config.update(self._analyze_java_config(project_path))
            elif project_type == "go":
                config.update(self._analyze_go_config(project_path))
            elif project_type == "rust":
                config.update(self._analyze_rust_config(project_path))
            elif project_type == "csharp":
                config.update(self._analyze_csharp_config(project_path))

            return config

        except (ProjectUtilityError, ProjectDetectionError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise ProjectUtilityError(
                message=f"Unexpected error during project configuration detection: {e}",
                details=f"Exception type: {type(e).__name__}, Project: {project_path}",
            ) from e

    def detect_project_structure(
        self, project_path: Path
    ) -> dict[str, str | bool | int]:
        """Detect project structure and organization.

        Args:
            project_path: Path to the project directory

        Returns:
            dict[str, str | bool | int]: Project structure information

        Raises:
            ProjectUtilityError: If input validation fails
            ProjectDetectionError: If project structure detection fails
        """
        try:
            # Input validation
            if not project_path:
                raise ProjectUtilityError(
                    message="Project path cannot be None",
                    details="Empty project path provided for project structure detection",
                )

            if not project_path.exists():
                raise ProjectDetectionError(
                    operation="detect_project_structure",
                    project_path=str(project_path),
                    reason="Project path does not exist",
                    details=f"Path {project_path} was not found",
                )

            if not project_path.is_dir():
                raise ProjectDetectionError(
                    operation="detect_project_structure",
                    project_path=str(project_path),
                    reason="Project path is not a directory",
                    details=f"Path {project_path} is not a directory",
                )

            structure = {
                "source_dirs": [],
                "test_dirs": [],
                "config_dirs": [],
                "build_dirs": [],
                "documentation_dirs": [],
                "total_files": 0,
                "total_dirs": 0,
            }

            try:
                # Walk through project structure
                for item in project_path.rglob("*"):
                    if item.is_file():
                        structure["total_files"] += 1
                    elif item.is_dir():
                        structure["total_dirs"] += 1
                        self._categorize_directory(item, structure, project_path)

            except (PermissionError, OSError) as e:
                raise ProjectDetectionError(
                    operation="detect_project_structure",
                    project_path=str(project_path),
                    reason=f"Permission or OS error during structure analysis: {e}",
                    details=f"Failed to analyze project structure: {e}",
                ) from e

            return structure

        except (ProjectUtilityError, ProjectDetectionError):
            # Re-raise specialized exceptions as-is
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise ProjectUtilityError(
                message=f"Unexpected error during project structure detection: {e}",
                details=f"Exception type: {type(e).__name__}, Project: {project_path}",
            ) from e

    def _matches_project_type(
        self, files: list[Path], dirs: list[Path], indicators: dict[str, list[str]]
    ) -> bool:
        """Check if project files and directories match a specific project type.

        Args:
            files: List of project files
            dirs: List of project directories
            indicators: Project type indicators

        Returns:
            bool: True if project matches the type
        """
        try:
            file_names = [f.name for f in files]
            dir_names = [d.name for d in dirs]

            # Check for indicator files
            for indicator_file in indicators.get("files", []):
                if indicator_file in file_names:
                    return True

            # Check for indicator directories
            for indicator_dir in indicators.get("dirs", []):
                if indicator_dir in dir_names:
                    return True

            # Check for file extensions
            for file in files:
                if file.suffix.lower() in indicators.get("extensions", []):
                    return True

            return False

        except Exception as e:
            # Log but don't raise - this is a helper method
            self.logger.warning(f"Error matching project type: {e}")
            return False

    def _categorize_directory(
        self,
        directory: Path,
        structure: dict[str, str | bool | int],
        project_root: Path,
    ) -> None:
        """Categorize a directory based on its name and contents.

        Args:
            directory: Directory to categorize
            structure: Structure dictionary to update
            project_root: Root of the project
        """
        try:
            dir_name = directory.name.lower()
            relative_path = str(directory.relative_to(project_root))

            # Source directories
            if dir_name in [
                "src",
                "source",
                "app",
                "main",
                "lib",
                "core",
            ] or dir_name.endswith(("src", "source")):
                structure["source_dirs"].append(relative_path)

            # Test directories
            elif dir_name in [
                "test",
                "tests",
                "spec",
                "specs",
                "__tests__",
            ] or dir_name.endswith(("test", "tests")):
                structure["test_dirs"].append(relative_path)

            # Configuration directories
            elif dir_name in ["config", "conf", "settings", ".config"]:
                structure["config_dirs"].append(relative_path)

            # Build directories
            elif dir_name in ["build", "dist", "target", "out", "bin"]:
                structure["build_dirs"].append(relative_path)

            # Documentation directories
            elif dir_name in ["docs", "documentation", "doc"]:
                structure["documentation_dirs"].append(relative_path)

        except Exception as e:
            # Log but don't raise - this is a helper method
            self.logger.warning(f"Error categorizing directory {directory}: {e}")

    def _analyze_python_config(self, project_path: Path) -> dict[str, str | bool | int]:
        """Analyze Python project configuration.

        Args:
            project_path: Path to the Python project

        Returns:
            dict[str, str | bool | int]: Python configuration information
        """
        try:
            config = {"config_files": {}, "dependencies": {}, "build_tools": []}

            # Check for common Python config files
            config_files = {
                "setup.py": "setup.py",
                "pyproject.toml": "pyproject.toml",
                "requirements.txt": "requirements.txt",
                "Pipfile": "Pipfile",
                "poetry.lock": "poetry.lock",
                "setup.cfg": "setup.cfg",
                "tox.ini": "tox.ini",
                "pytest.ini": "pytest.ini",
                "mypy.ini": "mypy.ini",
                ".flake8": ".flake8",
                "ruff.toml": "ruff.toml",
            }

            for config_file, config_path_str in config_files.items():
                config_path_obj = project_path / config_path_str
                if config_path_obj.exists():
                    config["config_files"][config_file] = str(config_path_obj)

            # Detect build tools
            if "pyproject.toml" in config["config_files"]:
                config["build_tools"].append("poetry")
            if "setup.py" in config["config_files"]:
                config["build_tools"].append("setuptools")
            if "Pipfile" in config["config_files"]:
                config["build_tools"].append("pipenv")

            return config

        except Exception as e:
            # Log but don't raise - this is a helper method
            self.logger.warning(f"Error analyzing Python config: {e}")
            return {"config_files": {}, "dependencies": {}, "build_tools": []}

    def _analyze_javascript_config(
        self, project_path: Path
    ) -> dict[str, str | bool | int]:
        """Analyze JavaScript project configuration.

        Args:
            project_path: Path to the JavaScript project

        Returns:
            dict[str, str | bool | int]: JavaScript configuration information
        """
        try:
            config = {"config_files": {}, "dependencies": {}, "build_tools": []}

            # Check for common JavaScript config files
            config_files = {
                "package.json": "package.json",
                "yarn.lock": "yarn.lock",
                "pnpm-lock.yaml": "pnpm-lock.yaml",
                "package-lock.json": "package-lock.json",
                "tsconfig.json": "tsconfig.json",
                "webpack.config.js": "webpack.config.js",
                "vite.config.js": "vite.config.js",
                "rollup.config.js": "rollup.config.js",
                ".eslintrc.js": ".eslintrc.js",
                ".prettierrc": ".prettierrc",
            }

            for config_file, config_path_str in config_files.items():
                config_path_obj = project_path / config_path_str
                if config_path_obj.exists():
                    config["config_files"][config_file] = str(config_path_obj)

            # Detect package managers
            if "yarn.lock" in config["config_files"]:
                config["build_tools"].append("yarn")
            elif "pnpm-lock.yaml" in config["config_files"]:
                config["build_tools"].append("pnpm")
            else:
                config["build_tools"].append("npm")

            return config

        except Exception as e:
            # Log but don't raise - this is a helper method
            self.logger.warning(f"Error analyzing JavaScript config: {e}")
            return {"config_files": {}, "dependencies": {}, "build_tools": []}

    def _analyze_java_config(self, project_path: Path) -> dict[str, str | bool | int]:
        """Analyze Java project configuration.

        Args:
            project_path: Path to the Java project

        Returns:
            dict[str, str | bool | int]: Java configuration information
        """
        try:
            config = {"config_files": {}, "dependencies": {}, "build_tools": []}

            # Check for common Java config files
            config_files = {
                "pom.xml": "pom.xml",
                "build.gradle": "build.gradle",
                "gradle.properties": "gradle.properties",
                "settings.gradle": "settings.gradle",
                "build.xml": "build.xml",
            }

            for config_file, config_path_str in config_files.items():
                config_path_obj = project_path / config_path_str
                if config_path_obj.exists():
                    config["config_files"][config_file] = str(config_path_obj)

            # Detect build tools
            if "pom.xml" in config["config_files"]:
                config["build_tools"].append("maven")
            if "build.gradle" in config["config_files"]:
                config["build_tools"].append("gradle")
            if "build.xml" in config["config_files"]:
                config["build_tools"].append("ant")

            return config

        except Exception as e:
            # Log but don't raise - this is a helper method
            self.logger.warning(f"Error analyzing Java config: {e}")
            return {"config_files": {}, "dependencies": {}, "build_tools": []}

    def _analyze_go_config(self, project_path: Path) -> dict[str, str | bool | int]:
        """Analyze Go project configuration.

        Args:
            project_path: Path to the Go project

        Returns:
            dict[str, str | bool | int]: Go configuration information
        """
        try:
            config = {"config_files": {}, "dependencies": {}, "build_tools": []}

            # Check for common Go config files
            config_files = {
                "go.mod": "go.mod",
                "go.sum": "go.sum",
                "Gopkg.toml": "Gopkg.toml",
                "Gopkg.lock": "Gopkg.lock",
            }

            for config_file, config_path_str in config_files.items():
                config_path_obj = project_path / config_path_str
                if config_path_obj.exists():
                    config["config_files"][config_file] = str(config_path_obj)

            # Go always uses go build
            config["build_tools"].append("go")

            return config

        except Exception as e:
            # Log but don't raise - this is a helper method
            self.logger.warning(f"Error analyzing Go config: {e}")
            return {"config_files": {}, "dependencies": {}, "build_tools": []}

    def _analyze_rust_config(self, project_path: Path) -> dict[str, str | bool | int]:
        """Analyze Rust project configuration.

        Args:
            project_path: Path to the Rust project

        Returns:
            dict[str, str | bool | int]: Rust configuration information
        """
        try:
            config = {"config_files": {}, "dependencies": {}, "build_tools": []}

            # Check for common Rust config files
            config_files = {
                "Cargo.toml": "Cargo.toml",
                "Cargo.lock": "Cargo.lock",
            }

            for config_file, config_path_str in config_files.items():
                config_path_obj = project_path / config_path_str
                if config_path_obj.exists():
                    config["config_files"][config_file] = str(config_path_obj)

            # Rust always uses cargo
            config["build_tools"].append("cargo")

            return config

        except Exception as e:
            # Log but don't raise - this is a helper method
            self.logger.warning(f"Error analyzing Rust config: {e}")
            return {"config_files": {}, "dependencies": {}, "build_tools": []}

    def _analyze_csharp_config(self, project_path: Path) -> dict[str, str | bool | int]:
        """Analyze C# project configuration.

        Args:
            project_path: Path to the C# project

        Returns:
            dict[str, str | bool | int]: C# configuration information
        """
        try:
            config = {"config_files": {}, "dependencies": {}, "build_tools": []}

            # Check for common C# config files
            config_files = {
                "*.csproj": "*.csproj",
                "*.sln": "*.sln",
                "packages.config": "packages.config",
                "global.json": "global.json",
            }

            for config_file, config_path_str in config_files.items():
                if config_file.startswith("*"):
                    # Handle wildcard patterns
                    pattern = config_file[1:]  # Remove *
                    for file_path in project_path.glob(f"*{pattern}"):
                        config["config_files"][file_path.name] = str(file_path)
                else:
                    config_path_obj = project_path / config_path_str
                    if config_path_obj.exists():
                        config["config_files"][config_file] = str(config_path_obj)

            # C# typically uses MSBuild or dotnet
            if any(".csproj" in key for key in config["config_files"]):
                config["build_tools"].append("dotnet")
            if any(".sln" in key for key in config["config_files"]):
                config["build_tools"].append("msbuild")

            return config

        except Exception as e:
            # Log but don't raise - this is a helper method
            self.logger.warning(f"Error analyzing C# config: {e}")
            return {"config_files": {}, "dependencies": {}, "build_tools": []}
