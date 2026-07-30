#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONFLICTS - Conflict resolution vocabulary
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Shared vocabulary for file and directory conflict resolution.

The enum and the protocol live here so that the service layer (which applies a
resolution) and the UI layer (which may ask the user for one) can both speak
about conflicts without depending on each other.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from enum import StrEnum
from pathlib import Path
from typing import Protocol

# ///////////////////////////////////////////////////////////////
# ENUMS
# ///////////////////////////////////////////////////////////////


class ConflictAction(StrEnum):
    """Actions available for conflict resolution."""

    OVERWRITE = "overwrite"
    SKIP = "skip"
    MERGE = "merge"
    CANCEL = "cancel"


# ///////////////////////////////////////////////////////////////
# PROTOCOLS
# ///////////////////////////////////////////////////////////////


class ConflictResolver(Protocol):
    """Decides what to do about an existing target.

    Implementations may be interactive; callers that have no terminal simply
    omit the resolver and get the service's deterministic policy instead.
    """

    def resolve_file(self, target_file: Path, context: str) -> ConflictAction: ...

    def resolve_directory(self, target_dir: Path, context: str) -> ConflictAction: ...


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ConflictAction",
    "ConflictResolver",
]
