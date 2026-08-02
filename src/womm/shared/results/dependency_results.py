#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPENDENCY RESULTS - Dependency Diagnostic Result Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dependency result classes for Works On My Machine.

This module contains result classes for the read-only dependency diagnostic
across the two strata WOMM depends on (runtimes, runtime package managers):
- Availability check
- Status report
- Static inventory
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass, field

# Local imports
from .base import BaseResult

# ///////////////////////////////////////////////////////////////
# PLAIN RECORDS
# ///////////////////////////////////////////////////////////////


@dataclass
class DependencyProbe:
    """A single probed dependency (plain record, not a Result)."""

    name: str
    available: bool
    path: str | None = None
    version: str | None = None


@dataclass
class DependencyInventoryEntry:
    """A statically configured dependency (no probing involved)."""

    name: str
    detail: str = ""


# ///////////////////////////////////////////////////////////////
# DEPENDENCY CHECK RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class DependencyCheckResult(BaseResult):
    """Result for probing every dependency across both strata."""

    runtime: list[DependencyProbe] = field(default_factory=list)
    package_managers: list[DependencyProbe] = field(default_factory=list)

    @property
    def runtime_ok(self) -> bool:
        """Every configured runtime is available."""
        return all(entry.available for entry in self.runtime)

    @property
    def package_managers_ok(self) -> bool:
        """At least one runtime package manager is available."""
        return any(entry.available for entry in self.package_managers)


# ///////////////////////////////////////////////////////////////
# DEPENDENCY STATUS RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class DependencyStatusResult(BaseResult):
    """Result for the comprehensive dependency status report."""

    runtime: list[DependencyProbe] = field(default_factory=list)
    package_managers: list[DependencyProbe] = field(default_factory=list)


# ///////////////////////////////////////////////////////////////
# DEPENDENCY INVENTORY RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class DependencyInventoryResult(BaseResult):
    """Result for the static dependency inventory (no probing)."""

    runtime: list[DependencyInventoryEntry] = field(default_factory=list)
    package_managers: list[DependencyInventoryEntry] = field(default_factory=list)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "DependencyCheckResult",
    "DependencyInventoryEntry",
    "DependencyInventoryResult",
    "DependencyProbe",
    "DependencyStatusResult",
]
