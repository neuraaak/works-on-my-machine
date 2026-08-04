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
from .create.create_completion_summaries import render_project_creation_result
from .project_wizard import ProjectWizard
from .setup.setup_completion_summaries import (
    print_project_setup_result,
    print_setup_completion_summary,
)
from .templates.template_store_display import (
    render_template_list,
    render_template_result,
)

# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ProjectWizard",
    "print_project_setup_result",
    "print_setup_completion_summary",
    "render_project_creation_result",
    "render_template_list",
    "render_template_result",
]
