#!/usr/bin/env python3
"""
Template manager for WOMM CLI.
Handles template generation from existing projects and template management.
"""

import json
import logging
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from ....exceptions.project.project_exceptions import (
    ProjectManagerError,
    ProjectValidationError,
    TemplateError,
)
from ....ui.common.console import print_success


class TemplateManager:
    """Template management for project creation from existing projects."""

    def __init__(self):
        """Initialize the template manager."""
        self.logger = logging.getLogger(__name__)

        try:
            # Templates stored in user's home directory
            self.templates_dir = Path.home() / ".womm" / ".templates"
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            self.template_cache: Dict[str, Dict] = {}
        except Exception as e:
            raise ProjectManagerError(
                message="Failed to initialize template manager",
                details=f"Error creating templates directory: {e}",
            ) from e

    def create_template_from_project(
        self,
        source_project_path: Path,
        template_name: str,
        dry_run: bool = False,
        **kwargs,
    ) -> bool:
        """
        Create a template from an existing project.

        Args:
            source_project_path: Path to the existing project
            template_name: Name for the new template
            dry_run: Show what would be done without making changes
            **kwargs: Additional template metadata

        Returns:
            True if template creation was successful, False otherwise

        Raises:
            ProjectValidationError: If input parameters are invalid
            TemplateError: If template creation fails
            ProjectManagerError: If unexpected error occurs
        """
        try:
            # Input validation
            if not source_project_path:
                raise ProjectValidationError(
                    validation_type="source_project_path",
                    value="None",
                    reason="Source project path cannot be None",
                    details="Source project path is required for template creation",
                )

            if not template_name:
                raise ProjectValidationError(
                    validation_type="template_name",
                    value="None",
                    reason="Template name cannot be None or empty",
                    details="Template name is required for template creation",
                )

            if not source_project_path.exists():
                raise ProjectValidationError(
                    validation_type="source_project_path",
                    value=str(source_project_path),
                    reason="Source project does not exist",
                    details="The specified source project path does not exist",
                )

            if dry_run:
                from ....ui.common.console import (
                    print_dry_run_message,
                    print_dry_run_success,
                    print_dry_run_warning,
                    print_header,
                )

                print_dry_run_warning()
                print_header("🚀 Template Creation (DRY RUN)")

                # Simulate template creation process
                print_dry_run_message(
                    "validate inputs",
                    f"source: {source_project_path}, template: {template_name}",
                )
                print_dry_run_message(
                    "detect project type", f"analyze {source_project_path}"
                )
                print_dry_run_message(
                    "scan project files", "identify files to include in template"
                )
                print_dry_run_message(
                    "generalize project",
                    "replace specific values with template variables",
                )
                print_dry_run_message(
                    "create template directory",
                    f"directory: {self.templates_dir / template_name}",
                )
                print_dry_run_message(
                    "copy project files", "copy and generalize project structure"
                )
                print_dry_run_message(
                    "create template metadata", "generate template.json with metadata"
                )
                print_dry_run_message(
                    "extract variables", "identify template variables for customization"
                )

                if kwargs.get("description"):
                    print_dry_run_message(
                        "set description", f"description: {kwargs.get('description')}"
                    )

                print_dry_run_success()
                return True

            # Create template directory
            template_dir = self.templates_dir / template_name
            if template_dir.exists():
                raise TemplateError(
                    operation="creation",
                    template_path=str(template_dir),
                    reason="Template already exists",
                    details=f"Template '{template_name}' already exists at {template_dir}",
                )

            template_dir.mkdir(parents=True, exist_ok=True)

            # Detect project type
            project_type = self._detect_project_type(source_project_path)

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
                raise TemplateError(
                    operation="metadata_creation",
                    template_path=str(template_json),
                    reason="Failed to create template metadata file",
                    details=f"Error writing template.json: {e}",
                ) from e

            # Get file count for summary
            file_count = len(template_files)

            # Use new UI function for creation summary
            from ....ui.project.template_ui import print_template_creation_summary

            print_template_creation_summary(
                template_name, str(source_project_path), file_count
            )
            return True

        except (ProjectValidationError, TemplateError):
            # Re-raise specialized exceptions
            raise
        except Exception as e:
            raise ProjectManagerError(
                message="Unexpected error during template creation",
                details=f"Error creating template '{template_name}' from '{source_project_path}': {e}",
            ) from e

    def generate_from_template(
        self,
        template_name: str,
        target_path: Path,
        template_vars: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Generate a project from a template.

        Args:
            template_name: Name of the template to use
            target_path: Path where to generate the project
            template_vars: Variables to substitute in templates

        Returns:
            True if generation was successful, False otherwise

        Raises:
            ProjectValidationError: If input parameters are invalid
            TemplateError: If template generation fails
            ProjectManagerError: If unexpected error occurs
        """
        try:
            # Input validation
            if not template_name:
                raise ProjectValidationError(
                    validation_type="template_name",
                    value="None",
                    reason="Template name cannot be None or empty",
                    details="Template name is required for project generation",
                )

            if not target_path:
                raise ProjectValidationError(
                    validation_type="target_path",
                    value="None",
                    reason="Target path cannot be None",
                    details="Target path is required for project generation",
                )

            template_dir = self.templates_dir / template_name

            if not template_dir.exists():
                raise TemplateError(
                    operation="generation",
                    template_path=str(template_dir),
                    reason="Template not found",
                    details=f"Template '{template_name}' does not exist at {template_dir}",
                )

            # Validate template
            if not self._validate_template(template_name):
                raise TemplateError(
                    operation="validation",
                    template_path=str(template_dir),
                    reason="Template validation failed",
                    details="Template metadata or structure is invalid",
                )

            # Create target directory
            try:
                target_path.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                raise TemplateError(
                    operation="target_creation",
                    template_path=str(target_path),
                    reason="Failed to create target directory",
                    details=f"Error creating target directory: {e}",
                ) from e

            # Get template files
            template_files = self._get_template_files(template_dir)

            # Process each file
            for template_file in template_files:
                if not self._process_template_file(
                    template_file, template_dir, target_path, template_vars
                ):
                    raise TemplateError(
                        operation="file_processing",
                        template_path=template_file,
                        reason="Failed to process template file",
                        details=f"Error processing template file: {template_file}",
                    )

            print_success(f"Project generated from template '{template_name}'")
            return True

        except (ProjectValidationError, TemplateError):
            # Re-raise specialized exceptions
            raise
        except Exception as e:
            raise ProjectManagerError(
                message="Unexpected error during template generation",
                details=f"Error generating project from template '{template_name}' to '{target_path}': {e}",
            ) from e

    def list_templates(self) -> Dict[str, List[str]]:
        """
        List all available templates.

        Returns:
            Dictionary mapping project types to template lists

        Raises:
            ProjectManagerError: If unexpected error occurs
        """
        try:
            templates = {}

            for template_dir in self.templates_dir.iterdir():
                if template_dir.is_dir() and not template_dir.name.startswith("."):
                    template_info = self._get_template_info(template_dir.name)
                    if template_info:
                        project_type = template_info.get("project_type", "unknown")
                        if project_type not in templates:
                            templates[project_type] = []
                        templates[project_type].append(template_dir.name)

            return templates

        except Exception as e:
            self.logger.error(f"Error listing templates: {e}")
            raise ProjectManagerError(
                message="Failed to list templates",
                details=f"Error scanning templates directory: {e}",
            ) from e

    def get_template_info(self, template_name: str) -> Optional[Dict]:
        """
        Get information about a specific template.

        Args:
            template_name: Name of the template

        Returns:
            Template information dictionary or None if not found

        Raises:
            ProjectValidationError: If template name is invalid
            ProjectManagerError: If unexpected error occurs
        """
        try:
            if not template_name:
                raise ProjectValidationError(
                    validation_type="template_name",
                    value="None",
                    reason="Template name cannot be None or empty",
                    details="Template name is required to get template info",
                )

            return self._get_template_info(template_name)
        except ProjectValidationError:
            # Re-raise specialized exceptions
            raise
        except Exception as e:
            raise ProjectManagerError(
                message="Failed to get template info",
                details=f"Error retrieving info for template '{template_name}': {e}",
            ) from e

    def delete_template(self, template_name: str, show_summary: bool = True) -> bool:
        """
        Delete a template.

        Args:
            template_name: Name of the template
            show_summary: Whether to show deletion summary (default: True)

        Returns:
            True if deletion was successful, False otherwise

        Raises:
            ProjectValidationError: If template name is invalid
            TemplateError: If template deletion fails
            ProjectManagerError: If unexpected error occurs
        """
        try:
            if not template_name:
                raise ProjectValidationError(
                    validation_type="template_name",
                    value="None",
                    reason="Template name cannot be None or empty",
                    details="Template name is required for template deletion",
                )

            template_dir = self.templates_dir / template_name

            if not template_dir.exists():
                raise TemplateError(
                    operation="deletion",
                    template_path=str(template_dir),
                    reason="Template not found",
                    details=f"Template '{template_name}' does not exist at {template_dir}",
                )

            # Remove template directory
            try:
                shutil.rmtree(template_dir)
            except (PermissionError, OSError) as e:
                raise TemplateError(
                    operation="deletion",
                    template_path=str(template_dir),
                    reason="Failed to delete template directory",
                    details=f"Error removing template directory: {e}",
                ) from e

            # Show deletion summary only if requested
            if show_summary:
                from ....ui.project.template_ui import print_template_deletion_summary

                print_template_deletion_summary(template_name)

            return True

        except (ProjectValidationError, TemplateError):
            # Re-raise specialized exceptions
            raise
        except Exception as e:
            raise ProjectManagerError(
                message="Unexpected error during template deletion",
                details=f"Error deleting template '{template_name}': {e}",
            ) from e

    def _detect_project_type(self, project_path: Path) -> str:
        """
        Detect the type of project.

        Args:
            project_path: Path to the project to analyze

        Returns:
            str: Detected project type

        Raises:
            ProjectDetectionError: If project type detection fails
        """
        try:
            if not project_path:
                raise ProjectValidationError(
                    validation_type="project_path",
                    value="None",
                    reason="Project path cannot be None",
                    details="Project path is required for type detection",
                )

            # Check for Python project
            if (project_path / "pyproject.toml").exists() or (
                project_path / "requirements.txt"
            ).exists():
                return "python"

            # Check for JavaScript project
            if (project_path / "package.json").exists():
                try:
                    with open(project_path / "package.json", encoding="utf-8") as f:
                        package_data = json.load(f)
                        dependencies = package_data.get("dependencies", {})
                        if "react" in dependencies:
                            return "react"
                        elif "vue" in dependencies:
                            return "vue"
                    return "javascript"
                except (PermissionError, OSError, json.JSONDecodeError) as e:
                    self.logger.warning(f"Error reading package.json: {e}")
                    return "javascript"

            return "unknown"

        except ProjectValidationError:
            # Re-raise specialized exceptions
            raise
        except Exception as e:
            self.logger.warning(f"Error detecting project type: {e}")
            return "unknown"

    def _scan_and_generalize_project(
        self, source_path: Path, template_dir: Path
    ) -> List[str]:
        """
        Scan project and create generalized template files.

        Args:
            source_path: Source project path
            template_dir: Template directory to create files in

        Returns:
            List[str]: List of template file paths

        Raises:
            TemplateError: If template file creation fails
        """
        try:
            if not source_path or not template_dir:
                raise ProjectValidationError(
                    validation_type="path",
                    value=f"source_path={source_path}, template_dir={template_dir}",
                    reason="Source path and template directory cannot be None",
                    details="Both source path and template directory are required",
                )

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
                        self.logger.warning(
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
                        self.logger.warning(f"Error processing file {item}: {e}")
                        continue

            return template_files

        except ProjectValidationError:
            # Re-raise specialized exceptions
            raise
        except Exception as e:
            raise TemplateError(
                operation="project_scanning",
                template_path=str(template_dir),
                reason="Failed to scan and generalize project",
                details=f"Error scanning project at {source_path}: {e}",
            ) from e

    def _generalize_content(self, content: str, source_project_name: str) -> str:
        """
        Generalize content by replacing specific values with template variables.

        Args:
            content: Content to generalize
            source_project_name: Name of the source project

        Returns:
            str: Generalized content

        Raises:
            TemplateError: If content generalization fails
        """
        try:
            if not content:
                return content

            if not source_project_name:
                raise ProjectValidationError(
                    validation_type="source_project_name",
                    value="None",
                    reason="Source project name cannot be None",
                    details="Source project name is required for content generalization",
                )

            # Common patterns to generalize
            generalizations = [
                # Project names (common patterns)
                (r"my-project", "{{PROJECT_NAME}}"),
                (r"my_project", "{{PROJECT_NAME}}"),
                (r"MyProject", "{{PROJECT_NAME}}"),
                # Source project name (most important)
                (re.escape(source_project_name), "{{PROJECT_NAME}}"),
                (re.escape(source_project_name.replace("-", "_")), "{{PROJECT_NAME}}"),
                (re.escape(source_project_name.replace("_", "-")), "{{PROJECT_NAME}}"),
                # Author information
                (r"John Doe", "{{AUTHOR_NAME}}"),
                (r"john\.doe@example\.com", "{{AUTHOR_EMAIL}}"),
                # Common email patterns
                (r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", "{{AUTHOR_EMAIL}}"),
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
                    self.logger.warning(
                        f"Error applying regex pattern '{pattern}': {e}"
                    )
                    continue

            return generalized

        except ProjectValidationError:
            # Re-raise specialized exceptions
            raise
        except Exception as e:
            raise TemplateError(
                operation="content_generalization",
                template_path="content",
                reason="Failed to generalize content",
                details=f"Error generalizing content for project '{source_project_name}': {e}",
            ) from e

    def _extract_template_variables(self, template_dir: Path) -> Dict[str, str]:
        """
        Extract template variables from template files.

        Args:
            template_dir: Template directory to scan

        Returns:
            Dict[str, str]: Dictionary of template variables

        Raises:
            TemplateError: If variable extraction fails
        """
        try:
            if not template_dir:
                raise ProjectValidationError(
                    validation_type="template_dir",
                    value="None",
                    reason="Template directory cannot be None",
                    details="Template directory is required for variable extraction",
                )

            variables = {}

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
                    self.logger.warning(
                        f"Error reading template file {template_file}: {e}"
                    )
                    continue

            return variables

        except ProjectValidationError:
            # Re-raise specialized exceptions
            raise
        except Exception as e:
            raise TemplateError(
                operation="variable_extraction",
                template_path=str(template_dir),
                reason="Failed to extract template variables",
                details=f"Error extracting variables from template directory: {e}",
            ) from e

    def _get_template_files(self, template_dir: Path) -> List[str]:
        """
        Get list of template files.

        Args:
            template_dir: Template directory to scan

        Returns:
            List[str]: List of template file paths

        Raises:
            TemplateError: If file listing fails
        """
        try:
            if not template_dir:
                raise ProjectValidationError(
                    validation_type="template_dir",
                    value="None",
                    reason="Template directory cannot be None",
                    details="Template directory is required for file listing",
                )

            files = []
            for item in template_dir.rglob("*.template"):
                if item.is_file():
                    # Get relative path from template directory
                    rel_path = item.relative_to(template_dir)
                    # Remove .template extension for output
                    output_path = str(rel_path).replace(".template", "")
                    files.append(output_path)
            return sorted(files)

        except ProjectValidationError:
            # Re-raise specialized exceptions
            raise
        except Exception as e:
            self.logger.warning(f"Error listing template files: {e}")
            return []

    def _process_template_file(
        self,
        template_file: str,
        template_dir: Path,
        target_path: Path,
        template_vars: Optional[Dict[str, str]] = None,
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

        Raises:
            TemplateError: If file processing fails
        """
        try:
            if not template_file:
                raise ProjectValidationError(
                    validation_type="template_file",
                    value="None",
                    reason="Template file name cannot be None or empty",
                    details="Template file name is required for processing",
                )

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
            try:
                target_file.parent.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                raise TemplateError(
                    operation="directory_creation",
                    template_path=str(target_file.parent),
                    reason="Failed to create target directory",
                    details=f"Error creating target directory: {e}",
                ) from e

            # Read template content
            try:
                content = source_file.read_text(encoding="utf-8")
            except (PermissionError, OSError, UnicodeDecodeError) as e:
                raise TemplateError(
                    operation="file_reading",
                    template_path=str(source_file),
                    reason="Failed to read template file",
                    details=f"Error reading template file: {e}",
                ) from e

            # Substitute variables
            if template_vars:
                for var_name, var_value in template_vars.items():
                    content = content.replace(f"{{{{{var_name}}}}}", str(var_value))

            # Write output file
            try:
                target_file.write_text(content, encoding="utf-8")
            except (PermissionError, OSError) as e:
                raise TemplateError(
                    operation="file_writing",
                    template_path=str(target_file),
                    reason="Failed to write output file",
                    details=f"Error writing output file: {e}",
                ) from e

            return True

        except (ProjectValidationError, TemplateError):
            # Re-raise specialized exceptions
            raise
        except Exception as e:
            self.logger.error(f"Error processing template file {template_file}: {e}")
            return False

    def _get_template_info(self, template_name: str) -> Optional[Dict]:
        """
        Get template information.

        Args:
            template_name: Name of the template

        Returns:
            Optional[Dict]: Template information or None

        Raises:
            TemplateError: If template info retrieval fails
        """
        try:
            if not template_name:
                raise ProjectValidationError(
                    validation_type="template_name",
                    value="None",
                    reason="Template name cannot be None or empty",
                    details="Template name is required to get template info",
                )

            template_dir = self.templates_dir / template_name
            template_json = template_dir / "template.json"

            if template_json.exists():
                try:
                    with open(template_json, encoding="utf-8") as f:
                        return json.load(f)
                except (PermissionError, OSError, json.JSONDecodeError) as e:
                    self.logger.warning(
                        f"Error reading template.json for {template_name}: {e}"
                    )
                    return None

            return None

        except ProjectValidationError:
            # Re-raise specialized exceptions
            raise
        except Exception as e:
            self.logger.warning(f"Error getting template info for {template_name}: {e}")
            return None

    def _validate_template(self, template_name: str) -> bool:
        """
        Validate a template.

        Args:
            template_name: Name of the template to validate

        Returns:
            bool: True if template is valid

        Raises:
            TemplateError: If template validation fails
        """
        try:
            if not template_name:
                raise ProjectValidationError(
                    validation_type="template_name",
                    value="None",
                    reason="Template name cannot be None or empty",
                    details="Template name is required for validation",
                )

            template_dir = self.templates_dir / template_name
            template_json = template_dir / "template.json"

            if not template_json.exists():
                raise TemplateError(
                    operation="validation",
                    template_path=str(template_json),
                    reason="Template metadata not found",
                    details=f"Template metadata file not found: {template_json}",
                )

            # Validate template.json
            try:
                with open(template_json, encoding="utf-8") as f:
                    template_data = json.load(f)
            except (PermissionError, OSError, json.JSONDecodeError) as e:
                raise TemplateError(
                    operation="metadata_validation",
                    template_path=str(template_json),
                    reason="Failed to read template metadata",
                    details=f"Error reading template.json: {e}",
                ) from e

            required_fields = ["name", "project_type"]
            for field in required_fields:
                if field not in template_data:
                    raise TemplateError(
                        operation="metadata_validation",
                        template_path=str(template_json),
                        reason=f"Required field missing in template.json: {field}",
                        details=f"Template metadata is missing required field: {field}",
                    )

            return True

        except (ProjectValidationError, TemplateError):
            # Re-raise specialized exceptions
            raise
        except Exception as e:
            self.logger.error(f"Error validating template: {e}")
            return False
