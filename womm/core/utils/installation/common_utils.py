#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# COMMON UTILS - Common Installation Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Common utilities for Works On My Machine installation operations.

This module provides shared utility functions used by both installation
and uninstallation operations.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import sys
from pathlib import Path

# Local imports
from ...exceptions.installation import InstallationUtilityError

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# COMMON PATH UTILITIES
# ///////////////////////////////////////////////////////////////


def get_target_womm_path() -> Path:
    """
    Get the standard target path for Works On My Machine.

    Returns:
        Path: Path object pointing to the .womm directory in user's home.

    Raises:
        InstallationUtilityError: If the home directory cannot be determined.
    """
    try:
        return Path.home() / ".womm"
    except Exception as e:
        # Wrap unexpected external exceptions
        raise InstallationUtilityError(
            message="Failed to determine target WOMM path",
            details=f"Exception type: {type(e).__name__}, Error: {e}",
        ) from e


def get_current_womm_path() -> Path:
    """
    Get the womm package directory by finding __main__.py.

    Returns:
        Path: Path object pointing to the womm package directory (parent of __main__.py).

    Raises:
        InstallationUtilityError: If the womm package directory cannot be found.
    """
    try:
        # Try to find __main__.py in the womm package
        try:
            import womm.__main__

            __main__path = Path(womm.__main__.__file__)
            womm_dir = __main__path.parent
            return womm_dir
        except ImportError as e:
            logger.warning(f"Failed to import womm.__main__: {e}")
            # Fallback: search in sys.path for __main__.py
            for path in sys.path:
                if path:
                    try:
                        potential_main = Path(path) / "womm" / "__main__.py"
                        if potential_main.exists():
                            return potential_main.parent
                    except Exception as e:
                        logger.warning(f"Failed to check path {path}: {e}")
                        continue

            # Last resort: try to find from current file location
            try:
                current_file = Path(__file__)
                # Navigate up to find womm directory
                for parent in current_file.parents:
                    try:
                        if (parent / "__main__.py").exists():
                            return parent
                    except Exception as e:
                        logger.warning(f"Failed to check parent {parent}: {e}")
                        continue
            except Exception as e:
                logger.warning(f"Failed to get current file path: {e}")

            # If all methods fail, raise the exception
            raise InstallationUtilityError(
                message="Could not find womm package directory (__main__.py not found)",
                details=f"All search methods failed, Import error: {e}",
            ) from e

    except InstallationUtilityError:
        # Re-raise specialized exceptions as-is
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise InstallationUtilityError(
            message=f"Unexpected error while finding womm package directory: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e
