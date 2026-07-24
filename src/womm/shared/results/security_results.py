#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SECURITY RESULTS - Security Result Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Security result classes for Works On My Machine.

This module contains result classes for security operations:
- Security validation
- Input validation
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass

# Local imports
from .base import BaseResult

# ///////////////////////////////////////////////////////////////
# VALIDATION RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class ValidationResult(BaseResult):
    """Result for input validation operations."""

    input_type: str = ""
    input_value: str = ""
    validation_rules: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.validation_rules is None:
            self.validation_rules = []


# ///////////////////////////////////////////////////////////////
# SECURITY RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class SecurityResult(BaseResult):
    """Result for security validation operations."""

    security_level: str = "low"  # low, medium, high
    threats_detected: list[str] | None = None
    recommendations: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.threats_detected is None:
            self.threats_detected = []
        if self.recommendations is None:
            self.recommendations = []


# ///////////////////////////////////////////////////////////////
# COMMAND VALIDATION RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class CommandValidationResult(BaseResult):
    """Result for command security validation."""

    command: str = ""
    is_valid: bool = False
    validation_reason: str = ""


# ///////////////////////////////////////////////////////////////
# PATH VALIDATION RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class PathValidationResult(BaseResult):
    """Result for file/directory path security validation."""

    path: str = ""
    is_valid: bool = False
    validation_reason: str = ""


# ///////////////////////////////////////////////////////////////
# SECURITY REPORT RESULT
# ///////////////////////////////////////////////////////////////


@dataclass
class SecurityReportResult(BaseResult):
    """Result for security report generation."""

    command: str = ""
    is_safe: bool = False
    reason: str = ""
    base_command: str = ""
    arguments: list[str] | None = None
    checks_performed: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.arguments is None:
            self.arguments = []
        if self.checks_performed is None:
            self.checks_performed = []


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "CommandValidationResult",
    "PathValidationResult",
    "SecurityReportResult",
    "SecurityResult",
    "ValidationResult",
]
