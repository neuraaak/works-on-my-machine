#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# COMPLETION SUMMARIES - Project Creation Completion Summaries
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Completion summaries for new project creation.

This module renders the outcome of ``ProjectCreateInterface.create_project``
for the CLI, following the established rendering pattern used by ``path``,
``context``, ``deps`` and ``doctor``.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from ....shared.results import ProjectCreationResult
from ...common.ezpl_bridge import ezprinter

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def render_project_creation_result(
    result: ProjectCreationResult, *, verbose: bool = False
) -> None:
    """Render the outcome of a template-driven project creation.

    Args:
        result: Outcome returned by ``ProjectCreateInterface.create_project``.
        verbose: Whether to also print the project template identifier.
    """
    if not result.success:
        ezprinter.error(result.error or "Project creation failed")
        return

    ezprinter.success(result.message or "Project created successfully")
    if result.project_path is not None:
        ezprinter.info(f"Project path: {result.project_path}")
    if verbose and result.project_type:
        ezprinter.info(f"Template: {result.project_type}")
    for warning in result.warnings or []:
        ezprinter.warning(warning)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["render_project_creation_result"]
