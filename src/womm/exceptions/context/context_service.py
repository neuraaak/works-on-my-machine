#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT SERVICE EXCEPTIONS - Context Service Exception Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception classes for context service operations.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# SERVICE EXCEPTION
# ///////////////////////////////////////////////////////////////


class ContextServiceError(Exception):
    """Single exception for ``ContextValidationService``, ``ContextParametersService``
    and ``ContextRegistryService``.

    Covers every context menu service failure (invalid input, registry access,
    system compatibility, ...). The failing step is carried by the
    ``operation`` field rather than by per-step subclasses, since no caller
    branches on the specific failure kind.
    """

    def __init__(
        self,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize a context service error.

        Args:
            operation: Service step that failed (e.g. "script_path",
                "registry_entry", "command_parameter")
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.reason = reason
        self.details = details
        message = f"Context service error during {operation}: {reason}"
        if details:
            message = f"{message} | Details: {details}"
        super().__init__(message)


# ///////////////////////////////////////////////////////////////
# INTERFACE-LEVEL LEFTOVER (still used by interfaces/context, not yet
# converted to Result — see [[womm-exception-rework]] stage 3)
# ///////////////////////////////////////////////////////////////


class ContextUtilityError(Exception):
    """Exception raised for unexpected errors at the context interface level."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize context utility error.

        Args:
            message: Error message
            operation: Operation that failed
            details: Additional error details
        """
        self.message = message or "Context service error occurred"
        self.operation = operation
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of error."""
        parts = [self.message]
        if self.operation:
            parts.append(f"Operation: {self.operation}")
        if self.details:
            parts.append(f"Details: {self.details}")
        return " | ".join(parts)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["ContextServiceError", "ContextUtilityError"]
