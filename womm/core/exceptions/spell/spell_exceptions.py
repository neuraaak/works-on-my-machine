#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SPELL EXCEPTIONS - Spell Checking Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Spell checking exceptions for Works On My Machine.

This module contains custom exceptions used specifically by spell checking modules:
- SpellManager (womm/core/managers/spell/spell_manager.py)
- Spell utilities (womm/core/utils/spell/cspell_utils.py, dictionary_utils.py)

Following a pragmatic approach with focused exception types:
1. SpellUtilityError - Base exception for spell checking utilities
2. CSpellError - CSpell-specific errors
3. DictionaryError - Dictionary management errors
4. SpellManagerError - Base exception for spell manager
5. SpellValidationError - Spell validation errors
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////

# ///////////////////////////////////////////////////////////////
# UTILITY EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class SpellUtilityError(Exception):
    """Base exception for all spell checking utility errors.

    This is the main exception class for all spell checking utility operations.
    Used for general errors like invalid arguments, unexpected failures, etc.
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
# CSPELL EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class CSpellError(SpellUtilityError):
    """CSpell-specific errors for spell checking operations.

    This exception is raised when CSpell operations fail,
    such as installation, configuration, or execution errors.
    """

    def __init__(
        self,
        operation: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize CSpell error with specific context.

        Args:
            operation: The operation being performed (e.g., "installation", "execution")
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.reason = reason
        message = f"CSpell {operation} failed: {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# DICTIONARY EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class DictionaryError(SpellUtilityError):
    """Dictionary management errors for spell checking operations.

    This exception is raised when dictionary operations fail,
    such as loading, parsing, or managing dictionary files.
    """

    def __init__(
        self,
        operation: str,
        dictionary_path: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize dictionary error with specific context.

        Args:
            operation: The operation being performed (e.g., "load", "parse")
            dictionary_path: The dictionary file being operated on
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.operation = operation
        self.dictionary_path = dictionary_path
        self.reason = reason
        message = f"Dictionary {operation} failed for '{dictionary_path}': {reason}"
        super().__init__(message, details)


# ///////////////////////////////////////////////////////////////
# MANAGER EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class SpellManagerError(Exception):
    """Base exception for SpellManager errors.

    This exception is raised when SpellManager operations fail,
    such as process orchestration, progress tracking, or state management.
    """

    def __init__(self, message: str, details: str | None = None) -> None:
        """Initialize the manager error with a message and optional details.

        Args:
            message: Human-readable error message
            details: Optional technical details for debugging
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


# ///////////////////////////////////////////////////////////////
# VALIDATION EXCEPTIONS
# ///////////////////////////////////////////////////////////////


class SpellValidationError(SpellManagerError):
    """Spell validation errors during spell checking process.

    This exception is raised when spell validation operations fail,
    such as checking word validity or processing spell check results.
    """

    def __init__(
        self,
        validation_type: str,
        word: str,
        reason: str,
        details: str | None = None,
    ) -> None:
        """Initialize spell validation error with specific context.

        Args:
            validation_type: Type of validation being performed (e.g., "word_check", "result_processing")
            word: The word being validated
            reason: Human-readable reason for the failure
            details: Optional technical details for debugging
        """
        self.validation_type = validation_type
        self.word = word
        self.reason = reason
        message = f"Spell validation '{validation_type}' failed for '{word}': {reason}"
        super().__init__(message, details)
