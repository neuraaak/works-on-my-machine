#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SPELL SERVICE EXCEPTIONS - Spell Service Exception Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Exception classes for spell checking service operations.

Provides specialized exceptions for CSpell operations, dictionary management,
and spell checking errors.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION CLASSES
# ///////////////////////////////////////////////////////////////


class CSpellServiceError(Exception):
    """Base exception for spell service errors."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        details: str = "",
    ) -> None:
        """Initialize spell service error.

        Args:
            message: Error message
            operation: Operation that failed
            details: Additional error details
        """
        self.message = message or "Spell service error occurred"
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
# SPECIALIZED EXCEPTION CLASSES
# ///////////////////////////////////////////////////////////////


class CheckServiceError(CSpellServiceError):
    """Exception raised when checker operations fail."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        reason: str = "",
        details: str = "",
    ) -> None:
        """Initialize CSpell error.

        Args:
            message: Error message
            operation: Operation that failed
            reason: Reason for failure
            details: Additional error details
        """
        self.reason = reason
        super().__init__(message, operation, details)


class DictionaryServiceError(CSpellServiceError):
    """Exception raised when dictionary operations fail."""

    def __init__(
        self,
        message: str = "",
        operation: str = "",
        dictionary_path: str = "",
        reason: str = "",
        details: str = "",
    ) -> None:
        """Initialize dictionary error.

        Args:
            message: Error message
            operation: Operation that failed
            dictionary_path: Path to dictionary file
            reason: Reason for failure
            details: Additional error details
        """
        self.dictionary_path = dictionary_path
        self.reason = reason
        super().__init__(message, operation, details)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "CSpellServiceError",
    "CheckServiceError",
    "DictionaryServiceError",
]
