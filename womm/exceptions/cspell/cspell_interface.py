#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SPELL INTERFACE EXCEPTIONS - Spell Interface Exception Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Spell interface exceptions for Works On My Machine.

This module contains custom exceptions used specifically by the spell
interfaces, such as:
- CSpellInterface (womm/interfaces/spell/cspell_interface.py)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class CSpellInterfaceError(Exception):
    """Base exception for all spell interface errors.

    This is the main exception class for all spell interface operations.
    Used for general errors like unexpected failures during spell operations.
    """

    def __init__(self, message: str, details: str | None = None) -> None:
        """Initialize the exception with a message and optional details.

        Args:
            message: Human-readable error message
            details: Optional technical details for debugging
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


# ///////////////////////////////////////////////////////////////
# CSPELL INTERFACE EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class CSpellDictionaryInterfaceError(CSpellInterfaceError):
    """Exception raised when dictionary operations fail.

    This exception is raised when dictionary management operations cannot
    be completed successfully, such as adding or listing dictionaries.
    """

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        dictionary_name: str | None = None,
        details: str | None = None,
    ) -> None:
        """Initialize dictionary interface error.

        Args:
            message: Human-readable error message
            operation: Optional operation that failed
            dictionary_name: Optional dictionary name that caused the error
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.dictionary_name = dictionary_name
        super().__init__(message, details)


class CSpellCheckInterfaceError(CSpellInterfaceError):
    """Exception raised when spell checking operations fail.

    This exception is raised when spell checking cannot be completed
    successfully, such as file scanning or result processing.
    """

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        target_path: str | None = None,
        details: str | None = None,
    ) -> None:
        """Initialize spell check interface error.

        Args:
            message: Human-readable error message
            operation: Optional operation that failed
            target_path: Optional path that caused the error
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.target_path = target_path
        super().__init__(message, details)
