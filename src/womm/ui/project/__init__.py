#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# UI PROJECT - Project UI Components
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project UI components package.

This package provides UI components for project creation and management,
following the established patterns in the WOMM codebase.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from .create.create_completion_summaries import print_new_project_summary
from .project_wizard import ProjectWizard
from .setup.setup_completion_summaries import print_setup_completion_summary
from .templates.template_project_configurator import configure_project_options
from .templates.template_selector import display_template_selection
from .templates.template_ui import (
    interactive_template_create,
    interactive_template_delete,
    print_template_creation_summary,
    print_template_deletion_summary,
    print_template_deletion_summary_multiple,
    print_template_info,
    print_template_list,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ProjectWizard",
    "configure_project_options",
    "display_template_selection",
    "interactive_template_create",
    "interactive_template_delete",
    "print_new_project_summary",
    "print_setup_completion_summary",
    "print_template_creation_summary",
    "print_template_deletion_summary",
    "print_template_deletion_summary_multiple",
    "print_template_info",
    "print_template_list",
]
