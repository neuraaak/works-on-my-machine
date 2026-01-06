#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DICTIONARY UTILS - Dictionary Management Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Dictionary Manager for CSpell - Pure utility functions for dictionary operations.
Used by SpellManager for UI-integrated dictionary management.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path

# Local imports
from ...exceptions.spell import DictionaryError, SpellUtilityError
from .cspell_utils import add_words_from_file

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# DICTIONARY MANAGEMENT UTILITIES
# ///////////////////////////////////////////////////////////////


def add_all_dictionaries_from_dir(project_path: Path) -> bool:
    """
    Add all dictionary files from .cspell-dict/ to CSpell configuration.
    Pure utility function without UI - used by SpellManager.

    Args:
        project_path: Project root path

    Returns:
        bool: True if successful, False otherwise

    Raises:
        SpellUtilityError: If dictionary processing fails unexpectedly
        DictionaryError: If dictionary file operations fail
    """
    try:
        # Input validation
        if not project_path:
            raise SpellUtilityError(
                message="Project path cannot be empty",
                details="Invalid project path provided for dictionary processing",
            )

        cspell_dict_dir = project_path / ".cspell-dict"

        # Check if .cspell-dict directory exists
        if not cspell_dict_dir.exists() or not cspell_dict_dir.is_dir():
            logger.debug(f"CSpell dictionary directory not found: {cspell_dict_dir}")
            return False

        # Find all .txt files
        try:
            dict_files = list(cspell_dict_dir.glob("*.txt"))
        except Exception as e:
            logger.warning(
                f"Failed to scan dictionary directory {cspell_dict_dir}: {e}"
            )
            return False

        if not dict_files:
            logger.debug(f"No dictionary files found in {cspell_dict_dir}")
            return False

        # Process each dictionary file
        success_count = 0

        for dict_file in dict_files:
            try:
                success = add_words_from_file(project_path, dict_file)
                if success:
                    success_count += 1
                    logger.debug(f"Successfully processed dictionary: {dict_file.name}")
                else:
                    logger.warning(f"Failed to process dictionary: {dict_file.name}")
            except (DictionaryError, SpellUtilityError) as e:
                # Re-raise our custom exceptions
                logger.warning(f"Error processing dictionary {dict_file.name}: {e}")
                raise
            except Exception as e:
                logger.debug(f"Unexpected error with {dict_file.name}: {e}")
                # Continue processing other files

        # Return True if at least some dictionaries were added
        logger.info(f"Processed {success_count}/{len(dict_files)} dictionary files")
        return success_count > 0

    except (SpellUtilityError, DictionaryError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise SpellUtilityError(
            message=f"Failed to add dictionaries from directory: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def list_available_dictionaries(project_path: Path | None = None) -> list[Path]:
    """
    List all available dictionary files in .cspell-dict/.

    Args:
        project_path: Project root path (defaults to current directory)

    Returns:
        List[Path]: List of dictionary file paths

    Raises:
        SpellUtilityError: If dictionary listing fails unexpectedly
    """
    try:
        if project_path is None:
            project_path = Path.cwd()

        # Input validation
        if not project_path:
            raise SpellUtilityError(
                message="Project path cannot be empty",
                details="Invalid project path provided for dictionary listing",
            )

        cspell_dict_dir = project_path / ".cspell-dict"

        if not cspell_dict_dir.exists() or not cspell_dict_dir.is_dir():
            logger.debug(f"CSpell dictionary directory not found: {cspell_dict_dir}")
            return []

        try:
            dict_files = list(cspell_dict_dir.glob("*.txt"))
            logger.debug(
                f"Found {len(dict_files)} dictionary files in {cspell_dict_dir}"
            )
            return dict_files
        except Exception as e:
            logger.warning(
                f"Failed to scan dictionary directory {cspell_dict_dir}: {e}"
            )
            return []

    except SpellUtilityError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise SpellUtilityError(
            message=f"Failed to list available dictionaries: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def get_dictionary_info(project_path: Path | None = None) -> dict:
    """
    Get information about available dictionaries.

    Args:
        project_path: Project root path (defaults to current directory)

    Returns:
        dict: Dictionary information

    Raises:
        SpellUtilityError: If dictionary info retrieval fails unexpectedly
        DictionaryError: If dictionary file reading fails
    """
    try:
        if project_path is None:
            project_path = Path.cwd()

        # Input validation
        if not project_path:
            raise SpellUtilityError(
                message="Project path cannot be empty",
                details="Invalid project path provided for dictionary info",
            )

        cspell_dict_dir = project_path / ".cspell-dict"

        info = {
            "directory_exists": cspell_dict_dir.exists(),
            "directory_path": str(cspell_dict_dir),
            "files": [],
            "total_files": 0,
            "total_words": 0,
        }

        if not info["directory_exists"]:
            logger.debug(f"CSpell dictionary directory not found: {cspell_dict_dir}")
            return info

        try:
            dict_files = list_available_dictionaries(project_path)
        except Exception as e:
            logger.warning(f"Failed to list dictionary files: {e}")
            return info

        info["files"] = [str(f) for f in dict_files]
        info["total_files"] = len(dict_files)

        # Count words in each file
        for dict_file in dict_files:
            try:
                with open(dict_file, encoding="utf-8") as f:
                    words = [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]
                    info["total_words"] += len(words)
                    logger.debug(f"Counted {len(words)} words in {dict_file.name}")
            except (PermissionError, OSError) as e:
                raise DictionaryError(
                    operation="file_reading",
                    dictionary_path=str(dict_file),
                    reason=f"Failed to read dictionary file: {e}",
                    details=f"Cannot access dictionary file: {dict_file}",
                ) from e
            except UnicodeDecodeError as e:
                raise DictionaryError(
                    operation="file_reading",
                    dictionary_path=str(dict_file),
                    reason=f"Failed to decode dictionary file: {e}",
                    details=f"Dictionary file encoding issue: {dict_file}",
                ) from e
            except Exception as e:
                logger.debug(f"Failed to read dictionary file {dict_file}: {e}")
                # Continue with other files

        logger.info(
            f"Dictionary info: {info['total_files']} files, {info['total_words']} words"
        )
        return info

    except (SpellUtilityError, DictionaryError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise SpellUtilityError(
            message=f"Failed to get dictionary info: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


# ///////////////////////////////////////////////////////////////
# BACKWARD COMPATIBILITY
# ///////////////////////////////////////////////////////////////


def add_all_dictionaries(project_path: Path | None = None) -> bool:
    """
    Legacy function name for backward compatibility.

    Args:
        project_path: Project root path (defaults to current directory)

    Returns:
        bool: True if successful, False otherwise

    Raises:
        SpellUtilityError: If dictionary processing fails unexpectedly
        DictionaryError: If dictionary file operations fail
    """
    try:
        if project_path is None:
            project_path = Path.cwd()

        # Input validation
        if not project_path:
            raise SpellUtilityError(
                message="Project path cannot be empty",
                details="Invalid project path provided for legacy dictionary processing",
            )

        return add_all_dictionaries_from_dir(project_path)

    except (SpellUtilityError, DictionaryError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise SpellUtilityError(
            message=f"Failed to add all dictionaries (legacy): {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e
