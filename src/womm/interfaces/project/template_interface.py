#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEMPLATE INTERFACE - Template Management Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Template interface for WOMM CLI.

Handles template generation from existing projects and template management.
Provides unified interface for template operations following the MEF pattern.

This interface orchestrates TemplateService and converts service exceptions
into a typed ``TemplateResult`` — it never raises. Read-only helpers
(``list_templates``, ``get_template_info``) return safe empty defaults
(``{}``/``None``) on failure instead of raising, since callers already treat
those as "nothing found".
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import logging
import re
from pathlib import Path

# Local imports
from ...exceptions.common import ValidationServiceError
from ...services import ProjectDetectionService, TemplateService
from ...shared.paths import user_templates_dir
from ...shared.results import ProjectDetectionResult, TemplateResult
from ...utils.common import safe_rmtree

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class TemplateInterface:
    """Template management interface for project creation from existing projects.

    This class provides a high-level interface for template operations,
    handling UI interactions and orchestrating the TemplateService.
    """

    def __init__(self):
        """Initialize the template interface."""
        self._template_service = TemplateService()
        self._detection_service = ProjectDetectionService()
        # User templates are data: they live under the data directory, and
        # its creation is owned by shared.paths — not by this constructor.
        self._templates_dir = user_templates_dir()
        self.logger = logging.getLogger(__name__)

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def create_template_from_project(
        self,
        source_project_path: Path,
        template_name: str,
        dry_run: bool = False,
        **kwargs,
    ) -> TemplateResult:
        """
        Create a template from an existing project.

        Args:
            source_project_path: Path to the existing project
            template_name: Name for the new template
            dry_run: Show what would be done without making changes
            **kwargs: Additional template metadata

        Returns:
            TemplateResult: Result of template creation operation
        """
        try:
            # Input validation
            if not source_project_path:
                return TemplateResult(
                    success=False,
                    template_name=template_name,
                    error="Source project path cannot be None",
                )

            if not template_name:
                return TemplateResult(
                    success=False,
                    template_name="",
                    error="Template name cannot be None or empty",
                )

            if not source_project_path.exists():
                return TemplateResult(
                    success=False,
                    template_name=template_name,
                    error=f"Source project does not exist: {source_project_path}",
                )

            if dry_run:
                return TemplateResult(
                    success=True,
                    message="Dry run completed successfully",
                    template_name=template_name,
                )

            # Create template directory
            template_dir = self._templates_dir / template_name
            if template_dir.exists():
                return TemplateResult(
                    success=False,
                    template_name=template_name,
                    error=f"Template '{template_name}' already exists at {template_dir}",
                )

            template_dir.mkdir(parents=True, exist_ok=True)

            # Detect project type using ProjectDetectionService
            type_result = self._detection_service.detect_project_type(
                source_project_path
            )
            project_type = (
                type_result.project_type
                if isinstance(type_result, ProjectDetectionResult)
                else "unknown"
            )

            # Scan and generalize the project
            template_files = self._scan_and_generalize_project(
                source_project_path, template_dir
            )

            # Create template.json
            template_data = {
                "name": template_name,
                "description": kwargs.get(
                    "description", f"Template generated from {source_project_path.name}"
                ),
                "version": "1.0.0",
                "author": "WOMM CLI",
                "project_type": project_type,
                "source_project": str(source_project_path),
                "created": kwargs.get("created", ""),
                "variables": self._extract_template_variables(template_dir),
                "files": template_files,
            }

            template_json = template_dir / "template.json"
            try:
                with open(template_json, "w", encoding="utf-8") as f:
                    json.dump(template_data, f, indent=2, ensure_ascii=False)
            except (PermissionError, OSError, TypeError, ValueError) as e:
                return TemplateResult(
                    success=False,
                    template_name=template_name,
                    error=f"Failed to create template metadata file: {e}",
                )

            file_count = len(template_files)

            return TemplateResult(
                success=True,
                message=f"Template '{template_name}' created successfully",
                template_name=template_name,
                template_path=template_dir,
                project_type=project_type,
                files_created=template_files,
                files_processed=file_count,
                metadata=template_data,
            )

        except ValidationServiceError as e:
            return TemplateResult(
                success=False,
                template_name=template_name,
                error=f"Template creation failed: {getattr(e, 'message', str(e))}",
            )
        except Exception as e:
            logger.error(
                f"Unexpected error in create_template_from_project: {e}", exc_info=True
            )
            return TemplateResult(
                success=False,
                template_name=template_name,
                error=f"Unexpected error during template creation: {e}",
            )

    def generate_from_template(
        self,
        template_name: str,
        target_path: Path,
        template_vars: dict[str, str] | None = None,
    ) -> TemplateResult:
        """
        Generate a project from a template.

        Args:
            template_name: Name of the template to use
            target_path: Path where to generate the project
            template_vars: Variables to substitute in templates

        Returns:
            TemplateResult: Result of template generation operation
        """
        try:
            # Input validation
            if not template_name:
                return TemplateResult(
                    success=False,
                    template_name="",
                    error="Template name cannot be None or empty",
                )

            if not target_path:
                return TemplateResult(
                    success=False,
                    template_name=template_name,
                    error="Target path cannot be None",
                )

            template_dir = self._templates_dir / template_name

            if not template_dir.exists():
                return TemplateResult(
                    success=False,
                    template_name=template_name,
                    error=f"Template '{template_name}' not found at {template_dir}",
                )

            # Validate template
            if not self._validate_template(template_name):
                return TemplateResult(
                    success=False,
                    template_name=template_name,
                    error="Template validation failed: metadata or structure is invalid",
                )

            # Create target directory
            try:
                target_path.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                return TemplateResult(
                    success=False,
                    template_name=template_name,
                    error=f"Failed to create target directory: {e}",
                )

            # Get template files
            template_files = self._get_template_files(template_dir)
            files_created = []

            # Process each file
            for template_file in template_files:
                if self._process_template_file(
                    template_file, template_dir, target_path, template_vars
                ):
                    files_created.append(template_file)
                else:
                    return TemplateResult(
                        success=False,
                        template_name=template_name,
                        error=f"Failed to process template file: {template_file}",
                    )

            return TemplateResult(
                success=True,
                message=f"Project generated from template '{template_name}'",
                template_name=template_name,
                template_path=template_dir,
                files_created=files_created,
                files_processed=len(files_created),
            )

        except ValidationServiceError as e:
            return TemplateResult(
                success=False,
                template_name=template_name,
                error=f"Template generation failed: {getattr(e, 'message', str(e))}",
            )
        except Exception as e:
            logger.error(
                f"Unexpected error in generate_from_template: {e}", exc_info=True
            )
            return TemplateResult(
                success=False,
                template_name=template_name,
                error=f"Unexpected error during template generation: {e}",
            )

    def list_templates(self) -> dict[str, list[str]]:
        """
        List all available templates.

        Returns:
            Dictionary mapping project types to template lists, empty on failure.
        """
        try:
            templates: dict[str, list[str]] = {}

            for template_dir in self._templates_dir.iterdir():
                if template_dir.is_dir() and not template_dir.name.startswith("."):
                    template_info = self._get_template_info(template_dir.name)
                    if template_info:
                        project_type = template_info.get("project_type", "unknown")
                        if project_type not in templates:
                            templates[project_type] = []
                        templates[project_type].append(template_dir.name)

            return templates

        except Exception as e:
            logger.error(f"Error listing templates: {e}", exc_info=True)
            return {}

    def get_template_info(self, template_name: str) -> dict | None:
        """
        Get information about a specific template.

        Args:
            template_name: Name of the template

        Returns:
            Template information dictionary or None if not found or on error.
        """
        if not template_name:
            logger.warning("Template name cannot be None or empty")
            return None

        return self._get_template_info(template_name)

    def delete_template(self, template_name: str) -> TemplateResult:
        """
        Delete a template.

        Args:
            template_name: Name of the template

        Returns:
            TemplateResult: Result of template deletion operation
        """
        try:
            if not template_name:
                return TemplateResult(
                    success=False,
                    template_name="",
                    error="Template name cannot be None or empty",
                )

            template_dir = self._templates_dir / template_name

            if not template_dir.exists():
                return TemplateResult(
                    success=False,
                    template_name=template_name,
                    error=f"Template '{template_name}' not found at {template_dir}",
                )

            # Remove template directory
            try:
                safe_rmtree(template_dir, allowed_parent=self._templates_dir)
            except (PermissionError, OSError) as e:
                return TemplateResult(
                    success=False,
                    template_name=template_name,
                    error=f"Failed to delete template directory: {e}",
                )

            return TemplateResult(
                success=True,
                message=f"Template '{template_name}' deleted successfully",
                template_name=template_name,
                template_path=template_dir,
            )

        except ValidationServiceError as e:
            return TemplateResult(
                success=False,
                template_name=template_name,
                error=f"Template deletion failed: {getattr(e, 'message', str(e))}",
            )
        except Exception as e:
            logger.error(f"Unexpected error in delete_template: {e}", exc_info=True)
            return TemplateResult(
                success=False,
                template_name=template_name,
                error=f"Unexpected error during template deletion: {e}",
            )

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _scan_and_generalize_project(
        self, source_path: Path, template_dir: Path
    ) -> list[str]:
        """
        Scan project and create generalized template files.

        Args:
            source_path: Source project path
            template_dir: Template directory to create files in

        Returns:
            list[str]: List of template file paths
        """
        template_files = []

        # Files to ignore
        ignore_patterns = [
            "__pycache__",
            ".git",
            ".venv",
            "venv",
            "node_modules",
            ".pytest_cache",
            ".mypy_cache",
            "*.pyc",
            "*.pyo",
            ".DS_Store",
            "Thumbs.db",
            ".vscode",
            ".idea",
        ]

        for item in source_path.rglob("*"):
            # Skip ignored patterns
            if any(pattern in str(item) for pattern in ignore_patterns):
                continue

            if item.is_file():
                # Get relative path
                rel_path = item.relative_to(source_path)

                # Generalize the path (replace project name in folder names)
                rel_path_str = str(rel_path)
                generalized_path = rel_path_str.replace(
                    source_path.name, "{{PROJECT_NAME}}"
                )
                generalized_path = generalized_path.replace(
                    source_path.name.replace("-", "_"), "{{PROJECT_NAME}}"
                )
                generalized_path = generalized_path.replace(
                    source_path.name.replace("_", "-"), "{{PROJECT_NAME}}"
                )

                template_file = template_dir / f"{generalized_path}.template"

                # Create parent directories
                try:
                    template_file.parent.mkdir(parents=True, exist_ok=True)
                except (PermissionError, OSError) as e:
                    logger.warning(
                        f"Error creating directory {template_file.parent}: {e}"
                    )
                    continue

                # Read and generalize content
                try:
                    content = item.read_text(encoding="utf-8", errors="ignore")
                    generalized_content = self._generalize_content(
                        content, source_path.name
                    )

                    # Write template file
                    template_file.write_text(generalized_content, encoding="utf-8")
                    template_files.append(generalized_path)
                except (PermissionError, OSError, UnicodeDecodeError) as e:
                    logger.warning(f"Error processing file {item}: {e}")
                    continue

        return template_files

    def _generalize_content(self, content: str, source_project_name: str) -> str:
        """
        Generalize content by replacing specific values with template variables.

        Args:
            content: Content to generalize
            source_project_name: Name of the source project

        Returns:
            str: Generalized content
        """
        if not content or not source_project_name:
            return content

        # Common patterns to generalize
        generalizations = [
            # Project names (common patterns)
            (r"my-project", "{{PROJECT_NAME}}"),
            (r"my_project", "{{PROJECT_NAME}}"),
            (r"MyProject", "{{PROJECT_NAME}}"),
            # Source project name (most important)
            (re.escape(source_project_name), "{{PROJECT_NAME}}"),
            (
                re.escape(source_project_name.replace("-", "_")),
                "{{PROJECT_NAME}}",
            ),
            (
                re.escape(source_project_name.replace("_", "-")),
                "{{PROJECT_NAME}}",
            ),
            # Author information
            (r"John Doe", "{{AUTHOR_NAME}}"),
            (r"john\.doe@example\.com", "{{AUTHOR_EMAIL}}"),
            # Common email patterns
            (
                r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
                "{{AUTHOR_EMAIL}}",
            ),
            # URLs and repositories
            (
                r"https://github\.com/[a-zA-Z0-9-]+/[a-zA-Z0-9-]+",
                "{{PROJECT_REPOSITORY}}",
            ),
            (r"https://example\.com", "{{PROJECT_URL}}"),
            # Version numbers
            (
                r'"version":\s*"[0-9]+\.[0-9]+\.[0-9]+"',
                '"version": "{{PROJECT_VERSION}}"',
            ),
        ]

        generalized = content
        for pattern, replacement in generalizations:
            try:
                generalized = re.sub(
                    pattern, replacement, generalized, flags=re.IGNORECASE
                )
            except re.error as e:
                logger.warning(f"Error applying regex pattern '{pattern}': {e}")
                continue

        return generalized

    def _extract_template_variables(self, template_dir: Path) -> dict[str, str]:
        """
        Extract template variables from template files.

        Args:
            template_dir: Template directory to scan

        Returns:
            dict[str, str]: Dictionary of template variables
        """
        variables: dict[str, str] = {}

        if not template_dir:
            return variables

        # Default variables
        default_vars = {
            "PROJECT_NAME": "Project name",
            "AUTHOR_NAME": "Author name",
            "AUTHOR_EMAIL": "Author email",
            "PROJECT_VERSION": "0.1.0",
            "PROJECT_DESCRIPTION": "Project description",
            "PROJECT_URL": "Project URL",
            "PROJECT_REPOSITORY": "Project repository",
        }

        # Scan template files for variables
        for template_file in template_dir.rglob("*.template"):
            try:
                content = template_file.read_text(encoding="utf-8")
                matches = re.findall(r"\{\{([^}]+)\}\}", content)
                for match in matches:
                    if match not in variables:
                        variables[match] = default_vars.get(match, f"{match} value")
            except (PermissionError, OSError, UnicodeDecodeError) as e:
                logger.warning(f"Error reading template file {template_file}: {e}")
                continue

        return variables

    def _get_template_files(self, template_dir: Path) -> list[str]:
        """
        Get list of template files.

        Args:
            template_dir: Template directory to scan

        Returns:
            list[str]: List of template file paths
        """
        try:
            if not template_dir:
                return []

            files = []
            for item in template_dir.rglob("*.template"):
                if item.is_file():
                    # Get relative path from template directory
                    rel_path = item.relative_to(template_dir)
                    # Remove .template extension for output
                    output_path = str(rel_path).replace(".template", "")
                    files.append(output_path)
            return sorted(files)

        except Exception as e:
            logger.warning(f"Error listing template files: {e}")
            return []

    def _process_template_file(
        self,
        template_file: str,
        template_dir: Path,
        target_path: Path,
        template_vars: dict[str, str] | None = None,
    ) -> bool:
        """
        Process a single template file.

        Args:
            template_file: Template file name
            template_dir: Template directory
            target_path: Target directory
            template_vars: Template variables

        Returns:
            bool: True if processing was successful
        """
        try:
            if not template_file:
                logger.warning("Template file name cannot be None or empty")
                return False

            source_file = template_dir / f"{template_file}.template"

            # Substitute variables in the file path as well
            target_file_path = template_file
            if template_vars:
                for var_name, var_value in template_vars.items():
                    target_file_path = target_file_path.replace(
                        f"{{{{{var_name}}}}}", str(var_value)
                    )

            target_file = target_path / target_file_path

            if not source_file.exists():
                return True  # Skip if template file doesn't exist

            # Create target directory if needed
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # Read template content
            content = source_file.read_text(encoding="utf-8")

            # Substitute variables using TemplateService
            if template_vars:
                content = self._template_service.replace_placeholders(
                    content, **template_vars
                )

            # Write output file
            target_file.write_text(content, encoding="utf-8")

            return True

        except Exception as e:
            logger.error(f"Error processing template file {template_file}: {e}")
            return False

    def _get_template_info(self, template_name: str) -> dict | None:
        """
        Get template information.

        Args:
            template_name: Name of the template

        Returns:
            dict | None: Template information or None
        """
        try:
            if not template_name:
                return None

            template_dir = self._templates_dir / template_name
            template_json = template_dir / "template.json"

            if template_json.exists():
                try:
                    with open(template_json, encoding="utf-8") as f:
                        return json.load(f)
                except (PermissionError, OSError, json.JSONDecodeError) as e:
                    logger.warning(
                        f"Error reading template.json for {template_name}: {e}"
                    )
                    return None

            return None

        except Exception as e:
            logger.warning(f"Error getting template info for {template_name}: {e}")
            return None

    def _validate_template(self, template_name: str) -> bool:
        """
        Validate a template.

        Args:
            template_name: Name of the template to validate

        Returns:
            bool: True if template is valid
        """
        try:
            if not template_name:
                logger.warning("Template name cannot be None or empty")
                return False

            template_dir = self._templates_dir / template_name
            template_json = template_dir / "template.json"

            if not template_json.exists():
                logger.warning(f"Template metadata file not found: {template_json}")
                return False

            # Validate template.json
            try:
                with open(template_json, encoding="utf-8") as f:
                    template_data = json.load(f)
            except (PermissionError, OSError, json.JSONDecodeError) as e:
                logger.warning(f"Error reading template.json: {e}")
                return False

            required_fields = ["name", "project_type"]
            for field in required_fields:
                if field not in template_data:
                    logger.warning(
                        f"Template metadata is missing required field: {field}"
                    )
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating template: {e}", exc_info=True)
            return False
