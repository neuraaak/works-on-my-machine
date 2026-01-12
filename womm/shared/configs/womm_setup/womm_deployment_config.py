#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# WOMM DEPLOYMENT CONFIG
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
WOMM deployment configuration.

Defines essential files, paths, and validation requirements
for WOMM installation and uninstallation operations.
"""

from __future__ import annotations

from typing import ClassVar

# ///////////////////////////////////////////////////////////////
# WOMM DEPLOYMENT CONFIGURATION
# ///////////////////////////////////////////////////////////////


class WOMMDeploymentConfig:
    """Configuration for WOMM deployment operations."""

    # ///////////////////////////////////////////////////////////
    # ESSENTIAL FILES
    # ///////////////////////////////////////////////////////////

    ESSENTIAL_FILES: ClassVar[list[str]] = ["womm.py", "womm.bat"]

    # ///////////////////////////////////////////////////////////
    # BACKUP VALIDATION
    # ///////////////////////////////////////////////////////////

    BACKUP_REQUIRED_KEYS: ClassVar[list[str]] = ["metadata", "entries"]

    BACKUP_REQUIRED_METADATA: ClassVar[list[str]] = [
        "version",
        "timestamp",
        "total_entries",
    ]

    # ///////////////////////////////////////////////////////////
    # UI DISPLAY STRINGS
    # ///////////////////////////////////////////////////////////

    PANEL_TITLE_INSTALLATION_INSTRUCTIONS: ClassVar[str] = (
        "Instructions d'installation de WOMM"
    )

    PANEL_TITLE_UNINSTALLATION_INSTRUCTIONS: ClassVar[str] = (
        "Instructions de désinstallation de WOMM"
    )

    # ///////////////////////////////////////////////////////////
    # HELPER METHODS
    # ///////////////////////////////////////////////////////////

    @classmethod
    def get_essential_files(cls) -> list[str]:
        """Get list of essential WOMM files.

        Returns:
            List of essential file names
        """
        return cls.ESSENTIAL_FILES.copy()

    @classmethod
    def get_backup_required_keys(cls) -> list[str]:
        """Get list of required keys in backup data.

        Returns:
            List of required backup keys
        """
        return cls.BACKUP_REQUIRED_KEYS.copy()

    @classmethod
    def get_backup_required_metadata(cls) -> list[str]:
        """Get list of required metadata fields in backup.

        Returns:
            List of required metadata fields
        """
        return cls.BACKUP_REQUIRED_METADATA.copy()


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["WOMMDeploymentConfig"]
