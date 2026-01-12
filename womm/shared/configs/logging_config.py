#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# LOGGING CONFIG - Global logging configuration for WOMM
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Global logging and ezpl configuration values.

This config class centralizes default log directory, file name and
rotation/retention/compression so they can be reused consistently
across the application.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar

# Local imports
from ...utils.womm_setup import get_womm_installation_path

# ///////////////////////////////////////////////////////////////
# CLASS DEFINITION
# ///////////////////////////////////////////////////////////////


@dataclass(frozen=True)
class LoggingConfig:
    """Logging configuration (static, read-only).

    Contains logging constants and path methods for WOMM logging system.
    """

    # ///////////////////////////////////////////////////////////
    # LOG DIRECTORY AND FILE
    # ///////////////////////////////////////////////////////////

    LOG_DIR_NAME: ClassVar[str] = ".logs"
    LOG_FILE_NAME: ClassVar[str] = "womm.log"

    # ///////////////////////////////////////////////////////////
    # ROTATION / RETENTION / COMPRESSION
    # ///////////////////////////////////////////////////////////

    ROTATION: ClassVar[str] = "10 MB"
    RETENTION: ClassVar[str] = "30 days"
    COMPRESSION: ClassVar[str] = "zip"

    # ///////////////////////////////////////////////////////////
    # LOG LEVELS
    # ///////////////////////////////////////////////////////////

    DEFAULT_LEVEL: ClassVar[str] = "INFO"

    # ///////////////////////////////////////////////////////////
    # PATH METHODS
    # ///////////////////////////////////////////////////////////

    @classmethod
    def get_log_dir(cls) -> Path:
        """Return the default directory used for WOMM log files.

        Uses the installation path and stores logs under ``.logs/``.

        Returns:
            Path to log directory
        """
        return get_womm_installation_path() / cls.LOG_DIR_NAME

    @classmethod
    def get_log_file(cls) -> Path:
        """Return the default log file path for WOMM.

        By default this is ``<install>/.logs/womm.log``.

        Returns:
            Path to log file
        """
        return cls.get_log_dir() / cls.LOG_FILE_NAME


__all__ = ["LoggingConfig"]
