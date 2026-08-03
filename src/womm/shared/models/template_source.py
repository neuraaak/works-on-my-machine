#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEMPLATE SOURCE - Template catalog entry model
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""Immutable model describing a Copier template known to WOMM."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# MODELS
# ///////////////////////////////////////////////////////////////


class TemplateOrigin(StrEnum):
    """Where a template comes from.

    Official templates ship inside the wheel and are read-only. User
    templates are registered by the user and stored in the catalog.
    """

    OFFICIAL = "official"
    USER = "user"


@dataclass(frozen=True)
class TemplateEntry:
    """A Copier template known to WOMM.

    Attributes:
        id: Short identifier, unique within an origin (e.g. "python").
        origin: Whether the template ships with WOMM or was registered.
        source: Absolute path to the template root holding ``copier.yml``.
        version: Declared template version, empty when unknown.
        description: One-line human description, empty when unknown.
    """

    id: str
    origin: TemplateOrigin
    source: Path
    version: str = ""
    description: str = ""

    @property
    def qualified_id(self) -> str:
        """Get the fully-qualified, unambiguous identifier."""
        return f"{self.origin.value}/{self.id}"


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["TemplateEntry", "TemplateOrigin"]
