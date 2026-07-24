#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# RESULTS BASE - Base Result Classes
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Base result classes for Works On My Machine.

This module provides the base result class and common result types
used across both services and interfaces.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from pathlib import Path

# ///////////////////////////////////////////////////////////////
# BASE RESULT CLASSES
# ///////////////////////////////////////////////////////////////


@dataclass
class BaseResult:
    """Base result class with common attributes."""

    success: bool
    message: str = ""
    error: str = ""

    def __bool__(self) -> bool:
        """Return success status as boolean."""
        return self.success

    def __str__(self) -> str:
        """Return string representation."""
        if self.success:
            return f"Success: {self.message}"
        else:
            return f"Failed: {self.error}"


@dataclass
class CommandResult:
    """Result for command execution."""

    returncode: int
    stdout: str = ""
    stderr: str = ""
    command: list[str] | None = None
    cwd: Path | None = None
    security_validated: bool = False
    execution_time: float = 0.0

    def __post_init__(self) -> None:
        """Initialize derived fields."""
        if self.command is None:
            self.command = []

    def __bool__(self) -> bool:
        """Return success status as boolean."""
        return self.returncode == 0

    def __str__(self) -> str:
        """Return string representation."""
        return (
            f"CommandResult(success={bool(self)}, "
            f"validated={self.security_validated}, "
            f"time={self.execution_time:.2f}s)"
        )


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = [
    "BaseResult",
    "CommandResult",
]
