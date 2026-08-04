#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT CREATION INTERFACE - Project Creation Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Project creation interface for WOMM CLI.

Orchestrates Copier template resolution, rendering, and optional environment
setup. This interface never raises: service exceptions are converted into a
typed ``ProjectCreationResult``.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from collections.abc import Mapping
from pathlib import Path

# Local imports
from ...exceptions.project import ProjectServiceError
from ...services.project.copier_project_creation_service import (
    CopierProjectCreationService,
    ProjectCreationRequest,
)
from ...services.project.template_store_service import TemplateStoreService
from ...shared.results import ProjectCreationResult

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class ProjectCreateInterface:
    """Orchestrate template resolution, rendering and optional setup."""

    def __init__(self) -> None:
        """Initialize the project creation interface."""
        self._store = TemplateStoreService()
        self._creator = CopierProjectCreationService()

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def create_project(
        self,
        template: str,
        destination: Path,
        *,
        answers: Mapping[str, str],
        force: bool = False,
        pretend: bool = False,
        defaults: bool = False,
        setup: bool = False,
    ) -> ProjectCreationResult:
        """Create a project from a catalog template.

        Args:
            template: Qualified or short template identifier.
            destination: Directory to render into.
            answers: Pre-filled Copier answers, values as raw strings.
            force: Allow a non-empty destination.
            pretend: Simulate without writing.
            defaults: Use template defaults instead of prompting.
            setup: Run the setup vertical after a successful render.

        Returns:
            ProjectCreationResult: Typed outcome, never raises.
        """
        try:
            entry = self._store.resolve(template)
            self._creator.create(
                ProjectCreationRequest(
                    template_source=entry.source,
                    destination=destination,
                    answers=dict(answers),
                    force=force,
                    pretend=pretend,
                    defaults=defaults,
                )
            )
        except ProjectServiceError as exc:
            return ProjectCreationResult(
                success=False,
                error=str(exc),
                project_path=destination,
                project_name=destination.name,
            )

        warnings: list[str] = []
        if setup and not pretend:
            warnings = self._run_setup(destination, entry.id)

        return ProjectCreationResult(
            success=True,
            message=f"Project created from {entry.qualified_id}",
            project_path=destination,
            project_name=destination.name,
            project_type=entry.qualified_id,
            warnings=warnings or None,
        )

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _run_setup(self, destination: Path, project_type: str) -> list[str]:
        """Delegate environment setup to the setup vertical.

        Setup failures never fail the creation: the project is rendered, and
        the user is told what could not be prepared.

        Args:
            destination: Path to the rendered project.
            project_type: Template id, used to select the setup path
                (e.g. "python").

        Returns:
            list[str]: Warnings to surface, empty when setup succeeded.
        """
        from ...interfaces.project.setup_interface import ProjectSetupInterface

        result = ProjectSetupInterface().setup_project(
            destination,
            project_type=project_type,
            virtual_env=True,
            install_deps=True,
            setup_dev_tools=True,
            setup_git_hooks=True,
        )
        if result and result.success:
            return []
        return [f"Setup step failed: {result.error or 'unknown error'}"]


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["ProjectCreateInterface"]
