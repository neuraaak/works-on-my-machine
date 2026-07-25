#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SECURITY SERVICE EXCEPTIONS - Security Service Exceptions
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Security service exceptions for Works On My Machine.

This module contains custom exceptions used specifically by the security service:
- SecurityValidatorService (womm/services/security/security_validator_service.py)
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# BASE EXCEPTION
# ///////////////////////////////////////////////////////////////


class SecurityServiceError(Exception):
    """Base exception for all security service errors.

    This is the main exception class for all security service operations.
    Used for general errors like unexpected failures during validation.
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
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["SecurityServiceError"]
