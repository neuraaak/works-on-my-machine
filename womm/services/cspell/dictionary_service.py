#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CSPELL DICTIONARY SERVICE - CSpell Dictionary Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
CSpell Dictionary Service - Singleton service for word and dictionary management.

Handles adding words to configuration, managing dictionary files,
and listing available dictionaries.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.cspell import CSpellServiceError, DictionaryServiceError
from ...shared.results.cspell_results import DictionaryResult

# ///////////////////////////////////////////////////////////////
# MODULE LOGGER
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# CSPELL DICTIONARY SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class CSpellDictionaryService:
    """Singleton service for word and dictionary management."""

    _instance: ClassVar[CSpellDictionaryService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> CSpellDictionaryService:
        """Create or return the singleton instance.

        Returns:
            CSpellDictionaryService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize CSpell dictionary service (only once)."""
        if CSpellDictionaryService._initialized:
            return

        self.logger = logging.getLogger(__name__)
        CSpellDictionaryService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PRIVATE HELPER METHODS - Inlined from cspell utils
    # ///////////////////////////////////////////////////////////////

    @staticmethod
    def _read_cspell_config(config_path: Path) -> dict[str, object]:
        """Read CSpell configuration from JSON file."""
        import json

        try:
            if not config_path.exists():
                raise DictionaryServiceError(
                    message="CSpell configuration file does not exist",
                    operation="config_access",
                    dictionary_path=str(config_path),
                    reason="CSpell configuration file does not exist",
                    details="Run setup_project first to create configuration",
                )
            return json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise DictionaryServiceError(
                message=f"Failed to parse configuration file: {e}",
                operation="config_parsing",
                dictionary_path=str(config_path),
                reason=f"Failed to parse configuration file: {e}",
                details=f"Invalid JSON in configuration file: {config_path}",
            ) from e

    @staticmethod
    def _write_cspell_config(config_path: Path, config: dict[str, object]) -> None:
        """Write CSpell configuration to JSON file."""
        import json

        try:
            config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        except (PermissionError, OSError) as e:
            raise DictionaryServiceError(
                message=f"Failed to write configuration file: {e}",
                operation="config_writing",
                dictionary_path=str(config_path),
                reason=f"Failed to write configuration file: {e}",
                details=f"Cannot write to configuration file: {config_path}",
            ) from e

    @staticmethod
    def _get_config_words_count(config: dict[str, object]) -> int:
        """Get words count from configuration."""
        return len(config.get("words", []))

    @staticmethod
    def _add_words_to_config_data(
        config: dict[str, object], words: list[str]
    ) -> tuple[dict[str, object], int]:
        """Add words to configuration data (in-memory)."""
        if "words" not in config:
            config["words"] = []

        added_count = 0
        for word in words:
            if word not in config["words"]:
                config["words"].append(word)
                added_count += 1

        return config, added_count

    @staticmethod
    def _read_words_from_file(file_path: Path) -> list[str]:
        """Read words from a file (one word per line, comments with #)."""
        try:
            if not file_path.exists():
                raise DictionaryServiceError(
                    message="Word file does not exist",
                    operation="file_access",
                    dictionary_path=str(file_path),
                    reason="Word file does not exist",
                    details=f"Cannot access word file: {file_path}",
                )

            words = []
            try:
                with open(file_path, encoding="utf-8") as f:
                    for line in f:
                        stripped_line = line.strip()
                        if stripped_line and not stripped_line.startswith("#"):
                            words.extend(stripped_line.split())
            except (PermissionError, OSError) as e:
                raise DictionaryServiceError(
                    message=f"Failed to read word file: {e}",
                    operation="file_reading",
                    dictionary_path=str(file_path),
                    reason=f"Failed to read word file: {e}",
                    details=f"Cannot access word file: {file_path}",
                ) from e
            except UnicodeDecodeError as e:
                raise DictionaryServiceError(
                    message=f"Failed to decode word file: {e}",
                    operation="file_reading",
                    dictionary_path=str(file_path),
                    reason=f"Failed to decode word file: {e}",
                    details=f"Word file encoding issue: {file_path}",
                ) from e

            return words

        except DictionaryServiceError:
            raise
        except Exception as e:
            raise DictionaryServiceError(
                message=f"Unexpected error reading word file: {e}",
                operation="file_reading",
                dictionary_path=str(file_path),
                reason=str(e),
                details=f"Exception type: {type(e).__name__}",
            ) from e

    @staticmethod
    def _list_available_dictionaries(project_path: Path | None = None) -> list[Path]:
        """List all available dictionary files in .cspell-dict/."""
        try:
            if project_path is None:
                project_path = Path.cwd()

            if not project_path:
                raise CSpellServiceError(
                    message="Project path cannot be empty",
                    operation="list_dictionaries",
                    details="Invalid project path provided for dictionary listing",
                )

            cspell_dict_dir = project_path / ".cspell-dict"

            if not cspell_dict_dir.exists() or not cspell_dict_dir.is_dir():
                return []

            try:
                return list(cspell_dict_dir.glob("*.txt"))
            except Exception:
                return []

        except CSpellServiceError:
            raise
        except Exception as e:
            raise CSpellServiceError(
                message=f"Failed to list available dictionaries: {e}",
                operation="list_dictionaries",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    @staticmethod
    def _get_dictionary_info(project_path: Path | None = None) -> dict[str, object]:
        """Get information about available dictionaries."""
        try:
            if project_path is None:
                project_path = Path.cwd()

            if not project_path:
                raise CSpellServiceError(
                    message="Project path cannot be empty",
                    operation="get_dictionary_info",
                    details="Invalid project path provided for dictionary info",
                )

            cspell_dict_dir = project_path / ".cspell-dict"

            info: dict[str, object] = {
                "directory_exists": cspell_dict_dir.exists(),
                "directory_path": str(cspell_dict_dir),
                "files": [],
                "total_files": 0,
                "total_words": 0,
            }

            if not info["directory_exists"]:
                return info

            try:
                dict_files = CSpellDictionaryService._list_available_dictionaries(
                    project_path
                )
            except Exception:
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
                        info["total_words"] = (
                            int(info["total_words"])
                            if isinstance(info["total_words"], int)
                            else 0
                        ) + len(words)
                except (PermissionError, OSError) as e:
                    raise DictionaryServiceError(
                        message=f"Failed to read dictionary file: {e}",
                        operation="file_reading",
                        dictionary_path=str(dict_file),
                        reason=f"Failed to read dictionary file: {e}",
                        details=f"Cannot access dictionary file: {dict_file}",
                    ) from e
                except Exception as e:
                    logger.debug(f"Failed to access dictionary file {dict_file}: {e}")

            return info

        except (CSpellServiceError, DictionaryServiceError):
            raise
        except Exception as e:
            raise CSpellServiceError(
                message=f"Failed to get dictionary info: {e}",
                operation="get_dictionary_info",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    @staticmethod
    def _add_all_dictionaries_from_dir(project_path: Path) -> bool:
        """Check if dictionary files exist in .cspell-dict/."""
        try:
            if not project_path:
                raise CSpellServiceError(
                    message="Project path cannot be empty",
                    operation="add_dictionaries",
                    details="Invalid project path provided for dictionary processing",
                )

            cspell_dict_dir = project_path / ".cspell-dict"

            if not cspell_dict_dir.exists() or not cspell_dict_dir.is_dir():
                return False

            try:
                dict_files = list(cspell_dict_dir.glob("*.txt"))
            except Exception:
                return False

            return len(dict_files) > 0

        except (CSpellServiceError, DictionaryServiceError):
            raise
        except Exception as e:
            raise CSpellServiceError(
                message=f"Failed to add dictionaries from directory: {e}",
                operation="add_dictionaries",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def add_words_to_config(
        self, project_path: Path, words: list[str]
    ) -> DictionaryResult:
        """Add words to CSpell configuration.

        Args:
            project_path: Path to the project directory
            words: List of words to add to configuration

        Returns:
            DictionaryResult: Result of word addition operation

        Raises:
            DictionaryError: If configuration modification fails
            SpellServiceError: If configuration setup fails
        """
        try:
            # Input validation
            if not project_path:
                raise CSpellServiceError(
                    message="Project path cannot be empty",
                    operation="add_words",
                    details="Invalid project path provided for word addition",
                )
            if not words:
                raise CSpellServiceError(
                    message="Words list cannot be empty",
                    operation="add_words",
                    details="Invalid words list provided for configuration",
                )

            config_path = project_path / "cspell.json"

            # Read configuration
            config = self._read_cspell_config(config_path)

            # Add words to config data
            config, added_count = self._add_words_to_config_data(config, words)

            # Write updated configuration
            self._write_cspell_config(config_path, config)

            self.logger.info(f"Added {added_count} words to CSpell configuration")

            return DictionaryResult(
                success=True,
                message=f"Successfully added {added_count} words to configuration",
                dictionary_path=config_path,
                words_added=added_count,
                total_words=self._get_config_words_count(config),
                files_processed=1,
            )

        except (DictionaryServiceError, CSpellServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise CSpellServiceError(
                message=f"Failed to add words to configuration: {e}",
                operation="add_words",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def add_words_from_file(
        self, project_path: Path, file_path: Path
    ) -> DictionaryResult:
        """Add words from a file to CSpell configuration.

        Args:
            project_path: Path to the project directory
            file_path: Path to the file containing words

        Returns:
            DictionaryResult: Result of word addition operation

        Raises:
            DictionaryError: If file reading or word addition fails
            SpellServiceError: If file processing fails
        """
        try:
            # Input validation
            if not project_path:
                raise CSpellServiceError(
                    message="Project path cannot be empty",
                    operation="add_words_from_file",
                    details="Invalid project path provided for word addition",
                )
            if not file_path:
                raise CSpellServiceError(
                    message="File path cannot be empty",
                    operation="add_words_from_file",
                    details="Invalid file path provided for word reading",
                )

            # Read words from file
            words = self._read_words_from_file(file_path)

            if not words:
                self.logger.warning("No words found in file")
                return DictionaryResult(
                    success=False,
                    error="No words found in file",
                    dictionary_path=file_path,
                    words_added=0,
                    total_words=0,
                    files_processed=0,
                )

            # Add words using the main method
            result = self.add_words_to_config(project_path, words)
            result.dictionary_path = file_path
            result.files_processed = 1
            return result

        except (DictionaryServiceError, CSpellServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise CSpellServiceError(
                message=f"Failed to add words from file: {e}",
                operation="add_words_from_file",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def add_all_dictionaries(self, project_path: Path) -> DictionaryResult:
        """Add all dictionary files from .cspell-dict/ to CSpell configuration.

        Args:
            project_path: Project root path

        Returns:
            DictionaryResult: Result of dictionary addition operation

        Raises:
            DictionaryError: If dictionary file operations fail
            SpellServiceError: If dictionary processing fails
        """
        try:
            # Input validation
            if not project_path:
                raise CSpellServiceError(
                    message="Project path cannot be empty",
                    operation="add_all_dictionaries",
                    details="Invalid project path provided for dictionary processing",
                )

            # Check if directory exists
            if not self._add_all_dictionaries_from_dir(project_path):
                return DictionaryResult(
                    success=False,
                    error="No dictionary files found or directory does not exist",
                    dictionary_path=project_path / ".cspell-dict",
                    words_added=0,
                    total_words=0,
                    files_processed=0,
                )

            # Process each dictionary file
            dict_files = self._list_available_dictionaries(project_path)
            success_count = 0
            total_words_added = 0

            for dict_file in dict_files:
                try:
                    result = self.add_words_from_file(project_path, dict_file)
                    if result.success:
                        success_count += 1
                        total_words_added += result.words_added
                        self.logger.debug(
                            f"Successfully processed dictionary: {dict_file.name}"
                        )
                    else:
                        self.logger.warning(
                            f"Failed to process dictionary: {dict_file.name}"
                        )
                except (DictionaryServiceError, CSpellServiceError) as e:
                    # Re-raise our custom exceptions
                    self.logger.warning(
                        f"Error processing dictionary {dict_file.name}: {e}"
                    )
                    raise
                except Exception as e:
                    self.logger.debug(f"Unexpected error with {dict_file.name}: {e}")
                    # Continue processing other files

            # Get total words count from config
            config_path = project_path / "cspell.json"
            total_words = 0
            if config_path.exists():
                try:
                    config = self._read_cspell_config(config_path)
                    total_words = self._get_config_words_count(config)
                except Exception as e:
                    self.logger.debug(
                        f"Failed to read config for total words count: {e}"
                    )

            self.logger.info(
                f"Processed {success_count}/{len(dict_files)} dictionary files"
            )

            return DictionaryResult(
                success=success_count > 0,
                message=f"Processed {success_count}/{len(dict_files)} dictionary files",
                dictionary_path=project_path / ".cspell-dict",
                words_added=total_words_added,
                total_words=total_words,
                files_processed=success_count,
            )

        except (CSpellServiceError, DictionaryServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise CSpellServiceError(
                message=f"Failed to add dictionaries from directory: {e}",
                operation="add_all_dictionaries",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_dictionary_info(
        self, project_path: Path | None = None
    ) -> dict[str, object]:
        """Get information about available dictionaries.

        Args:
            project_path: Project root path (defaults to current directory)

        Returns:
            dict: Dictionary information

        Raises:
            SpellServiceError: If dictionary info retrieval fails unexpectedly
            DictionaryError: If dictionary file reading fails
        """
        return self._get_dictionary_info(project_path)

    def list_available_dictionaries(
        self, project_path: Path | None = None
    ) -> list[Path]:
        """List all available dictionary files in .cspell-dict/.

        Args:
            project_path: Project root path (defaults to current directory)

        Returns:
            list[Path]: List of dictionary file paths

        Raises:
            SpellServiceError: If dictionary listing fails unexpectedly
        """
        return self._list_available_dictionaries(project_path)
