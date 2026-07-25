#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# PROJECT SERVICE EXCEPTIONS - Project Service Exception Class
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception class for the project services.

A single exception covers the whole project service layer (detection,
validation, conflict resolution, template processing, Python/JavaScript
project creation); the failing step is carried by a structured field
rather than by a class hierarchy.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# SERVICE EXCEPTION
# ///////////////////////////////////////////////////////////////


class ProjectServiceError(Exception):
    """Single exception for every ``services/project`` service.

    Covers project detection, validation, conflict resolution, template
    processing, and Python/JavaScript project creation failures. The failing
    step is carried by the ``operation`` field rather than by per-service
    subclasses, since no caller branches on the specific failure kind.
    """

    def __init__(
        self,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize a project service error.

        Args:
            operation: Service step that failed (e.g. "detect_project_type",
                "create_project_structure", "resolve_file_conflict")
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.reason = reason
        self.details = details
        message = f"Project service error during {operation}: {reason}"
        if details:
            message = f"{message} | Details: {details}"
        super().__init__(message)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["ProjectServiceError"]
