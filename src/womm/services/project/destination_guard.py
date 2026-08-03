#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DESTINATION GUARD - Pre-flight checks before rendering
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""Destination pre-flight checks run before any Copier invocation.

Copier's ``overwrite`` flag governs conflicting-file overwrites, not the
refusal of a non-empty directory: Copier happily renders into an existing
tree. The "non-empty destination fails without --force" contract is
therefore enforced here, before Copier is ever called.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
from pathlib import Path

from womm.exceptions.project import ProjectServiceError

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# Entries that do not make a destination "occupied": a freshly cloned but
# empty repository is a legitimate target.
IGNORED_ENTRIES = frozenset({".git"})

# Maximum number of occupants listed in the refusal message.
DEFAULT_OCCUPANT_LIMIT = 4

# ///////////////////////////////////////////////////////////////
# PUBLIC FUNCTIONS
# ///////////////////////////////////////////////////////////////


def describe_occupants(
    destination: Path,
    limit: int = DEFAULT_OCCUPANT_LIMIT,
) -> list[str]:
    """List the entries that make a destination non-empty.

    Args:
        destination: Directory to inspect.
        limit: Maximum number of names returned.

    Returns:
        list[str]: Sorted entry names, ignoring tolerated entries.
    """
    if not destination.is_dir():
        return []
    names = sorted(
        entry.name
        for entry in destination.iterdir()
        if entry.name not in IGNORED_ENTRIES
    )
    return names[:limit]


def check_destination(destination: Path, *, force: bool) -> None:
    """Verify that a destination may receive a rendered project.

    Args:
        destination: Target directory, existing or not.
        force: Whether the user explicitly allowed a non-empty destination.

    Raises:
        ProjectServiceError: If the destination is a file, or is a non-empty
            directory and ``force`` is not set.
    """
    if destination.exists() and not destination.is_dir():
        raise ProjectServiceError(
            operation="check_destination",
            reason=f"Destination is not a directory: {destination}",
        )

    occupants = describe_occupants(destination)
    if not occupants or force:
        return

    listed = ", ".join(occupants)
    raise ProjectServiceError(
        operation="check_destination",
        reason=f"Destination is not empty: {destination}",
        details=f"Found: {listed}. Use --force to render anyway.",
    )


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["check_destination", "describe_occupants"]
