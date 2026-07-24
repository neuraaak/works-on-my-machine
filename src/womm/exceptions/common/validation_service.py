#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# VALIDATION SERVICE EXCEPTIONS - Validation Service Exception Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception classes for validation service operations.

Provides a unified validation exception used across all services.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class ValidationServiceError(Exception):
    """Base exception for validation errors across all services."""

    def __init__(
        self,
        operation: str,
        field: str,
        reason: str,
        details: str = "",
        **kwargs: str,
    ) -> None:
        """Initialize validation error.

        Args:
            operation: Operation that failed
            field: Field that failed validation
            reason: Reason for validation failure
            details: Additional error details
            **kwargs: Additional context-specific attributes
        """
        self.operation = operation
        self.field = field
        self.reason = reason
        self.details = details

        # Store additional context-specific attributes
        for key, value in kwargs.items():
            setattr(self, key, value)

        message = f"Validation failed for {field} in {operation}: {reason}"
        if details:
            message = f"{message} | Details: {details}"
        super().__init__(message)

    def __str__(self) -> str:
        """Return string representation of error."""
        parts = [
            f"Validation failed for {self.field} in {self.operation}: {self.reason}"
        ]
        if self.details:
            parts.append(f"Details: {self.details}")
        return " | ".join(parts)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "ValidationServiceError",
]
