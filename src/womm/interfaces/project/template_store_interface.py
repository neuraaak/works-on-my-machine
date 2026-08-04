#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEMPLATE STORE INTERFACE - Template Catalog Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Template store interface for WOMM CLI.

Orchestrates catalog operations (list, show, add, remove, update) against
``TemplateStoreService`` and template scaffolding against
``CopierProjectCreationService``. This interface never raises: service
exceptions are converted into a typed Result.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from collections.abc import Mapping
from pathlib import Path

# Local imports
from ...exceptions.project import ProjectServiceError
from ...services.project.copier_project_creation_service import (
    CopierProjectCreationService,
    ProjectCreationRequest,
)
from ...services.project.template_store_service import TemplateStoreService
from ...shared.paths import packaged_copier_meta
from ...shared.results.project_results import ProjectCreationResult
from ...shared.results.template_results import TemplateListResult, TemplateStoreResult

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class TemplateStoreInterface:
    """Orchestrate catalog operations and template scaffolding."""

    def __init__(self) -> None:
        """Initialize the template store interface."""
        self._store = TemplateStoreService()
        self._creator = CopierProjectCreationService()

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def list_templates(self) -> TemplateListResult:
        """List every known template.

        Returns:
            TemplateListResult: Typed outcome, never raises.
        """
        try:
            entries = self._store.list_templates()
        except ProjectServiceError as exc:
            return TemplateListResult(success=False, error=str(exc))
        return TemplateListResult(
            success=True,
            message=f"{len(entries)} template(s) available",
            entries=entries,
        )

    def show_template(self, identifier: str) -> TemplateStoreResult:
        """Show a single catalog entry.

        Args:
            identifier: Qualified or short template identifier.

        Returns:
            TemplateStoreResult: Typed outcome, never raises.
        """
        try:
            entry = self._store.resolve(identifier)
        except ProjectServiceError as exc:
            return TemplateStoreResult(success=False, error=str(exc))
        return TemplateStoreResult(
            success=True,
            message=f"Template found: {entry.qualified_id}",
            entry=entry,
        )

    def add_template(self, identifier: str, source: Path) -> TemplateStoreResult:
        """Register a local template under the user namespace.

        Args:
            identifier: Short identifier, without any separator.
            source: Directory holding ``copier.yml``.

        Returns:
            TemplateStoreResult: Typed outcome, never raises.
        """
        try:
            entry = self._store.add(identifier, source)
        except ProjectServiceError as exc:
            return TemplateStoreResult(success=False, error=str(exc))
        return TemplateStoreResult(
            success=True,
            message=f"Template registered: {entry.qualified_id}",
            entry=entry,
        )

    def remove_template(self, identifier: str) -> TemplateStoreResult:
        """Unregister a user template.

        Args:
            identifier: Qualified or short identifier.

        Returns:
            TemplateStoreResult: Typed outcome, never raises.
        """
        try:
            entry = self._store.remove(identifier)
        except ProjectServiceError as exc:
            return TemplateStoreResult(success=False, error=str(exc))
        return TemplateStoreResult(
            success=True,
            message=f"Template removed: {entry.qualified_id}",
            entry=entry,
        )

    def update_template(self, identifier: str, source: Path) -> TemplateStoreResult:
        """Point an existing user template at a new source.

        Args:
            identifier: Qualified or short identifier.
            source: New directory holding ``copier.yml``.

        Returns:
            TemplateStoreResult: Typed outcome, never raises.
        """
        try:
            entry = self._store.update(identifier, source)
        except ProjectServiceError as exc:
            return TemplateStoreResult(success=False, error=str(exc))
        return TemplateStoreResult(
            success=True,
            message=f"Template updated: {entry.qualified_id}",
            entry=entry,
        )

    def init_template(
        self,
        destination: Path,
        *,
        answers: Mapping[str, str],
        force: bool = False,
        defaults: bool = False,
    ) -> ProjectCreationResult:
        """Scaffold a new Copier template skeleton.

        The skeleton is rendered by the same service as projects: WOMM has no
        second rendering engine. It carries no inference — questions, conditions
        and structure are the template author's responsibility.

        Args:
            destination: Directory to scaffold into.
            answers: Pre-filled meta-template answers.
            force: Allow a non-empty destination.
            defaults: Use defaults instead of prompting.

        Returns:
            ProjectCreationResult: Typed outcome, never raises.
        """
        try:
            self._creator.create(
                ProjectCreationRequest(
                    template_source=Path(str(packaged_copier_meta())),
                    destination=destination,
                    answers=dict(answers),
                    force=force,
                    defaults=defaults,
                )
            )
        except ProjectServiceError as exc:
            return ProjectCreationResult(
                success=False, error=str(exc), project_path=destination
            )
        return ProjectCreationResult(
            success=True,
            message=f"Template skeleton created at {destination}",
            project_path=destination,
            project_name=destination.name,
        )


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["TemplateStoreInterface"]
