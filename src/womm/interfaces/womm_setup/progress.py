#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DEPLOYMENT PROGRESS - Progress Reporting Protocol
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Progress reporting protocol for the WOMM deployment interfaces.

Install/uninstall report fine-grained, per-stage progress (file counts,
stage transitions) as they run, unlike the single top-level spinner used by
other verticals. Defining that surface as a ``Protocol`` here lets the
interfaces stay UI-free: the command layer supplies a concrete
implementation (``ui.common.ezpl_bridge.DynamicLayeredProgress`` structurally
satisfies it) while tests can pass ``NullProgressReporter``.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from typing import Protocol

# ///////////////////////////////////////////////////////////////
# PROTOCOL
# ///////////////////////////////////////////////////////////////


class DeploymentProgressReporter(Protocol):
    """Surface the deployment interfaces call into for progress feedback."""

    def update_layer(
        self, layer_name: str, progress_value: int | None = None, message: str = ""
    ) -> None:
        """Update a stage's progress value and/or status message."""
        ...

    def complete_layer(self, layer_name: str) -> None:
        """Mark a stage as complete."""
        ...

    def emergency_stop(self, _message: str = "Operation stopped") -> None:
        """Stop the progress display after an unrecoverable error."""
        ...


# ///////////////////////////////////////////////////////////////
# NULL IMPLEMENTATION
# ///////////////////////////////////////////////////////////////


class NullProgressReporter:
    """No-op reporter used when no UI progress is supplied (e.g. tests)."""

    def update_layer(
        self, layer_name: str, progress_value: int | None = None, message: str = ""
    ) -> None:
        """Discard the progress update."""

    def complete_layer(self, layer_name: str) -> None:
        """Discard the stage completion."""

    def emergency_stop(self, _message: str = "Operation stopped") -> None:
        """Discard the emergency stop."""


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["DeploymentProgressReporter", "NullProgressReporter"]
