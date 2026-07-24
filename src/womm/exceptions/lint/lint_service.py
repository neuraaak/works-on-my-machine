#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# LINT SERVICE EXCEPTIONS - Lint Service Exception Class
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception class for the linting services.

A single exception covers the whole lint service layer; the failing step is
carried by a structured field rather than by a class hierarchy.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# SERVICE EXCEPTION
# ///////////////////////////////////////////////////////////////


class LintServiceError(Exception):
    """Single exception for ``LintService`` and ``PythonLintService``.

    Covers every linting failure (invalid input, no tool available, tool
    execution, timeout, JSON output parsing, ...). The failing step is carried
    by the ``operation`` field rather than by per-step subclasses, since no
    caller branches on the specific failure kind.
    """

    def __init__(
        self,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize a lint service error.

        Args:
            operation: Lint step that failed (e.g. "run_tool_check",
                "get_tool_version", "fix_python_code")
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.reason = reason
        self.details = details
        message = f"Lint service error during {operation}: {reason}"
        if details:
            message = f"{message} | Details: {details}"
        super().__init__(message)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["LintServiceError"]
