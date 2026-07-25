#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SYSTEM SERVICE EXCEPTIONS - System Service Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
System service exception for Works On My Machine.

A single exception covers every system-service failure — detection, PATH
management, registry access, filesystem operations and environment refresh.
The failing step is carried by ``operation`` and any extra context by
``details``, rather than by per-step subclasses: no caller branches on the
specific failure kind, they only distinguish "ours" from "unexpected".
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# SYSTEM SERVICE EXCEPTION
# ///////////////////////////////////////////////////////////////


class SystemServiceError(Exception):
    """Single exception for all system service errors.

    Args:
        operation: Step that failed (e.g. ``"platform_info"``, ``"path_add"``,
            ``"registry_read"``, ``"environment_refresh"``)
        reason: Human-readable reason for the failure
        details: Optional technical context for debugging (paths, registry
            keys, exception types — conventionally ``"key=value | note"``)
    """

    def __init__(
        self,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize a system service error."""
        self.operation = operation
        self.reason = reason
        self.details = details
        self.message = f"System service error during {operation}: {reason}"
        super().__init__(self.message)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["SystemServiceError"]
