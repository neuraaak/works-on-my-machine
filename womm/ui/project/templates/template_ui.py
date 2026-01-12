#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEMPLATE UI - Template Management UI Components
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Template UI components for WOMM CLI.
Provides Rich-based UI for template management.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from pathlib import Path
from typing import Any

# Third-party imports
from InquirerPy import inquirer
from InquirerPy.validator import PathValidator
from rich.panel import Panel
from rich.table import Table

# Local imports
from ....utils.womm_setup import get_womm_installation_path
from ...common.ezpl_bridge import ezconsole

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////


def print_template_list(templates: dict[str, list[str]]) -> None:
    """Display templates in a Rich table."""
    table = Table(title="Available Templates")
    table.add_column("Project Type", style="cyan", width=15)
    table.add_column("Template Name", style="green", width=25)
    table.add_column("Description", style="white", width=40)
    table.add_column("Files", style="yellow", width=8, justify="center")

    for project_type, template_names in templates.items():
        for template_name in template_names:
            # Get template info for description
            template_info = _get_template_info(template_name)
            description = (
                template_info.get("description", "No description")
                if template_info
                else "No description"
            )
            file_count = len(template_info.get("files", [])) if template_info else 0

            table.add_row(project_type, template_name, description, str(file_count))

    ezconsole.print(table)


def print_template_info(template_name: str, template_info: dict[str, Any]) -> None:
    """Display detailed template information in a Rich panel."""
    content = f"""
[b]Name:[/b] {template_info.get("name", "N/A")}
[b]Description:[/b] {template_info.get("description", "No description")}
[b]Project Type:[/b] {template_info.get("project_type", "unknown")}
[b]Version:[/b] {template_info.get("version", "N/A")}
[b]Author:[/b] {template_info.get("author", "N/A")}
[b]Source Project:[/b] {template_info.get("source_project", "N/A")}

[b]Template Variables:[/b]
"""

    variables = template_info.get("variables", {})
    for var_name, var_desc in variables.items():
        content += f"  • {var_name}: {var_desc}\n"

    content += f"\n[b]Files ({len(template_info.get('files', []))}):[/b]\n"
    for file_path in template_info.get("files", []):
        content += f"  • {file_path}\n"

    panel = Panel(content, title=f"Template: {template_name}", border_style="blue")
    ezconsole.print(panel)


def print_template_creation_summary(
    template_name: str, source_project: str, file_count: int
) -> None:
    """Display a summary of template creation in a Rich panel."""
    content = f"""
Template '{template_name}' created successfully!

Source Project: {source_project}
Files Processed: {file_count}
Location: ~/.womm/.templates/{template_name}

Next Steps:
• Use 'womm template list' to see all templates
• Use 'womm template info {template_name}' for details
• Use 'womm template use {template_name}' to create projects from this template
"""

    panel = Panel(content, title="Template Creation Complete", border_style="green")
    ezconsole.print(panel)


def print_template_deletion_summary(template_name: str) -> None:
    """Display a summary of template deletion in a Rich panel."""
    content = f"""
Template '{template_name}' deleted successfully!

Note: This action cannot be undone.
The template and all its files have been permanently removed.
"""

    panel = Panel(content, title="Template Deletion Complete", border_style="red")
    ezconsole.print(panel)


def print_template_deletion_summary_multiple(
    successful_templates: list[str], failed_templates: list[str]
) -> None:
    """Display a summary of multiple template deletions in a Rich panel."""
    if not successful_templates and not failed_templates:
        return

    content = ""

    if successful_templates:
        content += f"Successfully deleted {len(successful_templates)} template(s):\n"
        for template_name in successful_templates:
            content += f"  • {template_name}\n"
        content += "\n"

    if failed_templates:
        content += f"Failed to delete {len(failed_templates)} template(s):\n"
        for template_name in failed_templates:
            content += f"  • {template_name}\n"
        content += "\n"

    content += "Note: This action cannot be undone.\n"
    content += "The templates and all their files have been permanently removed."

    title = "Template Deletion Summary"
    border_style = "green" if not failed_templates else "yellow"

    panel = Panel(content, title=title, border_style=border_style)
    ezconsole.print(panel)


def interactive_template_create() -> dict[str, str] | None:
    """
    Interactive form for creating a template.

    Returns:
        Dictionary with template creation parameters or None if cancelled
    """
    try:
        # Select source project
        class DirectoryValidator(PathValidator):
            def validate(self, document):
                result = super().validate(document)
                if result:
                    path = Path(document.text)
                    return path.exists() and path.is_dir()
                return False

        source_project = inquirer.filepath(
            message="Select the source project to create template from:",
            validate=DirectoryValidator(),
        ).execute()

        if not source_project:
            return None

        # Get template name
        template_name = inquirer.text(
            message="Enter template name (leave empty for auto-generation):",
            default="",
        ).execute()

        # Get description
        description = inquirer.text(
            message="Enter template description:",
            default="",
        ).execute()

        answers = {
            "source_project": source_project,
            "template_name": template_name or "",
            "description": description or "",
        }
        if not answers:
            return None

        # Auto-generate template name if not provided
        if not answers["template_name"]:
            source_path = Path(answers["source_project"])
            answers["template_name"] = source_path.name

        # Auto-generate description if not provided
        if not answers["description"]:
            source_path = Path(answers["source_project"])
            answers["description"] = f"Template generated from {source_path.name}"

        return answers

    except Exception as e:
        ezconsole.print(f"[red]Error in interactive form: {e}[/red]")
        return None


def interactive_template_delete(templates: dict[str, list[str]]) -> list[str] | None:
    """
    Interactive form for deleting templates.

    Args:
        templates: Dictionary of available templates

    Returns:
        List of template names to delete or None if cancelled
    """
    if not templates:
        ezconsole.print("[yellow]No templates available to delete.[/yellow]")
        return None

    # Flatten templates list for selection
    all_templates = []
    for project_type, template_names in templates.items():
        for template_name in template_names:
            template_info = _get_template_info(template_name)
            description = (
                template_info.get("description", "No description")
                if template_info
                else "No description"
            )
            all_templates.append(f"{template_name} ({project_type}) - {description}")

    try:
        # Select templates to delete
        selected_items = inquirer.checkbox(
            message="Select templates to delete (use space to select/deselect):",
            choices=all_templates,
        ).execute()

        if not selected_items:
            return None

        # Confirm deletion
        confirm = inquirer.confirm(
            message="Are you sure you want to delete the selected templates?",
            default=False,
        ).execute()

        if not confirm:
            return None

        # Extract template names from selected items
        selected_templates = []
        for selected_item in selected_items:
            template_name = selected_item.split(" (")[
                0
            ]  # Extract name before first parenthesis
            selected_templates.append(template_name)

        return selected_templates

    except Exception as e:
        ezconsole.print(f"[red]Error in interactive form: {e}[/red]")
        return None


def _get_template_info(template_name: str) -> dict[str, str | list | int] | None:
    """Get template information from template.json file."""
    try:
        installation_path = get_womm_installation_path()
        template_dir = installation_path / ".templates" / template_name
        template_json = template_dir / "template.json"

        if template_json.exists():
            import json

            with open(template_json, encoding="utf-8") as f:
                return json.load(f)
        return None
    except Exception:
        return None


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "interactive_template_create",
    "interactive_template_delete",
    "print_template_creation_summary",
    "print_template_deletion_summary",
    "print_template_deletion_summary_multiple",
    "print_template_info",
    "print_template_list",
]
