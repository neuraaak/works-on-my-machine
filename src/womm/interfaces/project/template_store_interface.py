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
from pathlib import Path

# Local imports
from ...exceptions.project import ProjectServiceError
from ...services.project.copier_project_creation_service import (
    CopierProjectCreationService,
)
from ...services.project.template_store_service import TemplateStoreService
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


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["TemplateStoreInterface"]
