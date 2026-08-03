#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# COPIER PROJECT CREATION SERVICE - Copier-backed rendering
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""Project rendering, delegated to Copier.

Copier owns the questionnaire and the rendering. WOMM owns the destination
contract, the security posture (no tasks, no unsafe features) and the
translation of Copier failures into ``ProjectServiceError``.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path

import copier

from womm.exceptions.project import ProjectServiceError

from .destination_guard import check_destination

# ///////////////////////////////////////////////////////////////
# REQUEST
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class ProjectCreationRequest:
    """Everything needed to render one project.

    Attributes:
        template_source: Path to the template root holding ``copier.yml``.
        destination: Directory to render into.
        answers: Pre-filled answers, keyed by Copier question name.
        force: Allow rendering into a non-empty destination.
        pretend: Simulate the rendering without writing anything.
        defaults: Use declared defaults instead of prompting.
    """

    template_source: Path
    destination: Path
    answers: Mapping[str, object] = field(default_factory=dict)
    force: bool = False
    pretend: bool = False
    defaults: bool = False


# ///////////////////////////////////////////////////////////////
# SERVICE
# ///////////////////////////////////////////////////////////////


class CopierProjectCreationService:
    """Render a project from a Copier template."""

    def create(self, request: ProjectCreationRequest) -> Path:
        """Render a template into its destination.

        A simulation never touches the filesystem, so it bypasses the
        destination guard: simulating against an existing project must stay
        possible.

        Args:
            request: Immutable rendering request.

        Returns:
            Path: The destination directory.

        Raises:
            ProjectServiceError: If the destination is refused or Copier fails.
        """
        if not request.pretend:
            check_destination(request.destination, force=request.force)

        try:
            copier.run_copy(
                src_path=str(request.template_source),
                dst_path=str(request.destination),
                data=dict(request.answers),
                overwrite=request.force,
                pretend=request.pretend,
                defaults=request.defaults,
                cleanup_on_error=True,
                unsafe=False,
                skip_tasks=True,
                quiet=True,
            )
        except ProjectServiceError:
            raise
        except Exception as exc:  # noqa: BLE001 - Copier raises many types
            raise ProjectServiceError(
                operation="create_project",
                reason=f"Template rendering failed: {request.template_source}",
                details=str(exc),
            ) from exc

        return request.destination


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["CopierProjectCreationService", "ProjectCreationRequest"]
