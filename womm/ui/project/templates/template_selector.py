#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEMPLATE SELECTOR - Template Selection UI Components
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Template selector UI components for Works On My Machine.

This module provides UI components for template selection and management,
following the established patterns in the WOMM codebase.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Third-party imports
try:
    from InquirerPy import inquirer
    from InquirerPy.base.control import Choice

    INQUIRERPY_AVAILABLE = True
except ImportError:
    INQUIRERPY_AVAILABLE = False

# Local imports
from ...common.ezpl_bridge import ezprinter
from ...common.interactive_menu import InteractiveMenu

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////


def display_template_selection(templates: list[str], project_type: str) -> str | None:
    """
    Display interactive template selection menu.

    Args:
        templates: List of available template names
        project_type: Type of project (python, javascript, etc.)

    Returns:
        Selected template name or None if cancelled
    """
    if not templates:
        ezprinter.info(f"No templates available for {project_type} projects")
        return None

    ezprinter.info(f"Available templates for {project_type} projects:")
    ezprinter.info("=" * 50)

    if INQUIRERPY_AVAILABLE:
        choices = [Choice(value=template, name=template) for template in templates]
        selected = inquirer.select(
            message="Select a template:",
            choices=choices,
            pointer="→",
        ).execute()
        return selected
    else:
        # Fallback to simple menu
        menu = InteractiveMenu("Select a template:")
        items = [{"name": template, "description": template} for template in templates]
        selected = menu.select_from_list(items, display_func=lambda x: x["description"])
        return selected["name"] if selected else None


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["display_template_selection"]
