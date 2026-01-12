#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CSPELL DICTIONARY INTERFACE - CSpell Dictionary Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
CSpell Dictionary Interface - Interface for word and dictionary management.

Handles adding words to configuration, managing dictionary files,
and listing available dictionaries.

This interface orchestrates CSpellDictionaryService and converts service exceptions
to interface exceptions following the MEF pattern.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
from pathlib import Path

# Local imports
from ...exceptions.cspell import (
    CSpellDictionaryInterfaceError,
    CSpellInterfaceError,
    CSpellServiceError,
    DictionaryServiceError,
)
from ...services import CSpellDictionaryService
from ...shared.results import AddWordsResult, CSpellResult, DictionarySetupResult
from ...ui.common import ezconsole, ezprinter
from ...utils.cspell import format_dictionary_info

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class CSpellDictionaryInterface:
    """Interface for managing words and dictionaries with CSpell.

    This class provides a high-level interface for CSpell dictionary operations,
    handling UI interactions and orchestrating the CSpellDictionaryService.
    """

    def __init__(self) -> None:
        """
        Initialize CSpell dictionary interface.

        Raises:
            SpellInterfaceError: If interface initialization fails
        """
        try:
            self._dictionary_service = CSpellDictionaryService()
        except Exception as e:
            logger.error(
                f"Failed to initialize CSpellDictionaryInterface: {e}", exc_info=True
            )
            raise CSpellInterfaceError(
                f"Spell dictionary interface initialization failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def setup_dictionaries(self) -> DictionarySetupResult:
        """
        Install essential CSpell dictionaries globally with integrated UI.

        Returns:
            DictionarySetupResult: Result of the dictionary setup operation

        Raises:
            DictionaryInterfaceError: If dictionary setup fails
        """
        try:
            with ezprinter.create_spinner_with_status("Setting up dictionaries...") as (
                progress,
                task,
            ):
                progress.update(task, status="Installing dictionaries...")

                try:
                    from ..dependencies.devtools_interface import DevToolsInterface

                    dev_tools_manager = DevToolsInterface()
                    # Install essential dictionaries
                    dict_success = dev_tools_manager._install_javascript_tool(
                        "cspell-dicts"
                    )

                    if not dict_success:
                        progress.update(task, status="Dictionary installation failed")
                        ezprinter.error("❌ Failed to install dictionaries")
                        return DictionarySetupResult(
                            success=False,
                            message="Failed to install dictionaries",
                            error="dictionary_install_failed",
                            dictionaries_installed=False,
                            dictionaries_count=0,
                            setup_time=0.0,
                        )

                    progress.update(task, status="Dictionaries installed successfully!")
                    ezprinter.success("✅ Dictionaries installed successfully")
                    return DictionarySetupResult(
                        success=True,
                        message="Dictionaries installed successfully",
                        dictionaries_installed=True,
                        dictionaries_count=1,
                        setup_time=0.0,
                    )

                except Exception as e:
                    logger.error(f"Dictionary setup error: {e}", exc_info=True)
                    raise CSpellDictionaryInterfaceError(
                        f"Failed to setup dictionaries: {e}",
                        operation="setup_dictionaries",
                        details=str(e),
                    ) from e

        except CSpellDictionaryInterfaceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in setup_dictionaries: {e}", exc_info=True)
            raise CSpellDictionaryInterfaceError(
                f"Dictionary setup failed: {e}",
                operation="setup_dictionaries",
                details=str(e),
            ) from e

    def add_words(
        self, words: list[str], project_path: Path | None = None
    ) -> AddWordsResult:
        """
        Add words to CSpell configuration with integrated UI.

        Args:
            words: List of words to add
            project_path: Path to the project (defaults to current directory)

        Returns:
            AddWordsResult: Result of the word addition operation

        Raises:
            DictionaryInterfaceError: If word addition fails
        """
        try:
            if project_path is None:
                project_path = Path.cwd()

            ezprinter.system(f"Adding {len(words)} words to CSpell configuration...")

            with ezprinter.create_spinner_with_status(
                "Adding words to configuration..."
            ) as (
                progress,
                task,
            ):
                progress.update(task, status="Validating configuration...")

                # Use CSpellDictionaryService for the actual operation
                try:
                    progress.update(task, status="Adding words...")
                    result = self._dictionary_service.add_words_to_config(
                        project_path, words
                    )
                    success = result.success
                except (CSpellServiceError, DictionaryServiceError) as e:
                    logger.error(f"Add words service error: {e}", exc_info=True)
                    raise CSpellDictionaryInterfaceError(
                        f"Failed to add words to configuration: {e.message}",
                        operation="add_words",
                        details=str(e),
                    ) from e
                except Exception as e:
                    logger.error(
                        f"Unexpected error during word addition: {e}", exc_info=True
                    )
                    raise CSpellDictionaryInterfaceError(
                        f"An unexpected error occurred: {e}",
                        operation="add_words",
                        details=str(e),
                    ) from e

                if success:
                    progress.update(task, status="Words added successfully!")
                    ezprinter.success("✅ Added words to CSpell configuration")
                    return AddWordsResult(
                        success=True,
                        message=f"Added {len(words)} words to configuration",
                        project_path=project_path,
                        words=words,
                        words_added=len(words),
                        addition_time=0.0,
                    )
                else:
                    progress.update(task, status="Failed to add words")
                    ezprinter.error("❌ Failed to add words to configuration")
                    return AddWordsResult(
                        success=False,
                        message="Failed to add words to configuration",
                        error="add_words_failed",
                        project_path=project_path,
                        words=words,
                        words_added=0,
                        addition_time=0.0,
                    )

        except CSpellDictionaryInterfaceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in add_words: {e}")
            raise CSpellDictionaryInterfaceError(
                f"Word addition failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def perform_add_words(
        self,
        words: list[str] | None = None,
        file_path: Path | None = None,
        interactive: bool = False,
        project_path: Path | None = None,
        dry_run: bool = False,
    ) -> AddWordsResult:
        """
        Add words to CSpell configuration with integrated UI and option handling.

        Args:
            words: List of words to add
            file_path: Path to file containing words
            interactive: Whether to run in interactive mode
            project_path: Path to the project (defaults to current directory)
            dry_run: Show what would be done without making changes

        Returns:
            AddWordsResult: Result of the word addition operation

        Raises:
            DictionaryInterfaceError: If word addition fails
        """
        try:
            if project_path is None:
                project_path = Path.cwd()

            if dry_run:
                ezprinter.print_dry_run_warning()

                # Simulate word addition process
                if interactive:
                    ezprinter.print_dry_run_message(
                        "run interactive mode", "prompt user for word input"
                    )
                elif file_path:
                    ezprinter.print_dry_run_message(
                        "read words from file", f"file: {file_path}"
                    )
                elif words:
                    ezprinter.print_dry_run_message(
                        "add words", f"words: {', '.join(words)}"
                    )
                else:
                    ezprinter.print_dry_run_message(
                        "process input", "handle word addition request"
                    )

                ezprinter.print_dry_run_message(
                    "update CSpell configuration", f"project: {project_path}"
                )
                ezprinter.print_dry_run_success()

                return AddWordsResult(
                    success=True,
                    message="Dry run completed - no words were actually added",
                    project_path=project_path,
                    words=words or [],
                    words_added=0,
                    addition_time=0.0,
                )

            # Handle interactive mode
            if interactive:
                ezprinter.info("📝 Interactive mode: Enter word to add")
                word = input("Enter word to add: ").strip()
                if word:
                    words = [word]
                    ezprinter.success(f"✅ Word '{word}' queued for addition")
                else:
                    ezprinter.error("❌ No word provided")
                    return AddWordsResult(
                        success=False,
                        message="No word provided",
                        error="no_word_provided",
                        project_path=project_path,
                        words=[],
                        words_added=0,
                        addition_time=0.0,
                    )

            # Handle file input
            if file_path:
                ezprinter.info(f"📄 Adding words from file: {file_path}")

                if not file_path.exists():
                    ezprinter.error(f"❌ File not found: {file_path}")
                    return AddWordsResult(
                        success=False,
                        message=f"File not found: {file_path}",
                        error="file_not_found",
                        project_path=project_path,
                        words=[],
                        words_added=0,
                        addition_time=0.0,
                    )

                try:
                    return self.add_words_from_file(file_path, project_path)
                except Exception as e:
                    raise CSpellDictionaryInterfaceError(
                        f"Failed to read words from file: {e}",
                        details=f"Exception type: {type(e).__name__}",
                    ) from e

            # Handle command line words
            elif words:
                ezprinter.info(f"📝 Adding {len(words)} words from command line")
                return self.add_words(words, project_path)

            # No input provided
            else:
                ezprinter.error("❌ No input provided")
                ezprinter.info("💡 Specify words, --file, or --interactive")
                return AddWordsResult(
                    success=False,
                    message="Specify words, --file, or --interactive",
                    error="no_input_provided",
                    project_path=project_path,
                    words=[],
                    words_added=0,
                    addition_time=0.0,
                )

        except CSpellDictionaryInterfaceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in perform_add_words: {e}")
            raise CSpellDictionaryInterfaceError(
                f"Word addition failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def add_words_from_file(
        self, file_path: Path, project_path: Path | None = None
    ) -> AddWordsResult:
        """
        Add words from a file to CSpell configuration.

        Args:
            file_path: Path to file containing words
            project_path: Path to the project (defaults to current directory)

        Returns:
            AddWordsResult: Result of the word addition operation

        Raises:
            DictionaryInterfaceError: If word addition fails
        """
        try:
            if project_path is None:
                project_path = Path.cwd()

            # Use CSpellDictionaryService for the actual operation
            try:
                result = self._dictionary_service.add_words_from_file(
                    project_path, file_path
                )
            except (CSpellServiceError, DictionaryServiceError) as e:
                logger.error(f"Add words from file service error: {e}", exc_info=True)
                raise CSpellDictionaryInterfaceError(
                    f"Failed to add words from file: {e.message}",
                    operation="add_words_from_file",
                    details=str(e),
                ) from e
            except Exception as e:
                logger.error(
                    f"Unexpected error during word addition from file: {e}",
                    exc_info=True,
                )
                raise CSpellDictionaryInterfaceError(
                    f"An unexpected error occurred: {e}",
                    operation="add_words_from_file",
                    details=str(e),
                ) from e

            if result.success:
                ezprinter.success(
                    f"✅ Added {result.words_added} words from {file_path.name}"
                )
                return AddWordsResult(
                    success=True,
                    message=f"Added {result.words_added} words from file",
                    project_path=project_path,
                    words=[],
                    words_added=result.words_added,
                    addition_time=0.0,
                )
            else:
                ezprinter.error(f"❌ Failed to add words from file: {result.error}")
                return AddWordsResult(
                    success=False,
                    message=result.error or "Failed to add words from file",
                    error="add_words_from_file_failed",
                    project_path=project_path,
                    words=[],
                    words_added=0,
                    addition_time=0.0,
                )

        except CSpellDictionaryInterfaceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in add_words_from_file: {e}")
            raise CSpellDictionaryInterfaceError(
                f"Word addition from file failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def perform_add_all_dictionaries(
        self,
        force: bool = False,
        project_path: Path | None = None,
        dict_dir: Path | None = None,
    ) -> CSpellResult:
        """
        Add all dictionaries to CSpell configuration with integrated UI.

        Scans the specified directory (or .cspell-dict/ by default) for dictionary files.

        Args:
            force: Whether to force the operation without confirmation
            project_path: Path to the project (defaults to current directory)
            dict_dir: Path to dictionary directory (defaults to .cspell-dict/ in project)

        Returns:
            SpellResult: Result of the dictionary addition operation

        Raises:
            DictionaryInterfaceError: If dictionary addition fails
        """
        try:
            if project_path is None:
                project_path = Path.cwd()

            # Determine which directory to scan
            if dict_dir is None:
                dict_dir = project_path / ".cspell-dict"

            # Get dictionary information
            try:
                dict_info_raw = self._dictionary_service.get_dictionary_info(
                    project_path, dict_dir
                )
                dict_info = format_dictionary_info(dict_info_raw)
            except (DictionaryServiceError, CSpellServiceError) as e:
                logger.error(f"Dictionary info service error: {e}", exc_info=True)
                raise CSpellDictionaryInterfaceError(
                    f"Failed to get dictionary information: {e.message}",
                    operation="get_dictionary_info",
                    details=str(e),
                ) from e
            except Exception as e:
                logger.error(
                    f"Unexpected error getting dictionary info: {e}", exc_info=True
                )
                raise CSpellDictionaryInterfaceError(
                    f"An unexpected error occurred: {e}",
                    operation="get_dictionary_info",
                    details=str(e),
                ) from e

            # Check if directory exists
            if not dict_info["directory_exists"]:
                ezprinter.error("❌ .cspell-dict directory not found")
                ezprinter.info(
                    "💡 Create the directory and add dictionary files (.txt)"
                )
                return CSpellResult(
                    success=False,
                    message=".cspell-dict directory not found",
                    error="dict_dir_not_found",
                )

            # Check if directory is empty
            if dict_info["total_files"] == 0:
                ezprinter.error("❌ .cspell-dict directory is empty")
                ezprinter.info("💡 Add .txt files with one word per line")
                return CSpellResult(
                    success=False,
                    message=".cspell-dict directory is empty",
                    error="dict_dir_empty",
                )

            # Show what will be added
            ezprinter.info("📚 Dictionary Information")
            status_text = "✅" if dict_info["directory_exists"] else "❌"
            ezprinter.system(f"  Directory exists: {status_text}")
            ezprinter.system(f"  Total files: {dict_info['total_files']}")
            if dict_info["files"]:
                ezprinter.system("  Files:")
                for file_path in dict_info["files"]:
                    ezprinter.system(f"    - {file_path}")

            # Confirm unless --force
            if not force:
                response = (
                    input("Continue with adding all dictionaries? (y/N): ")
                    .lower()
                    .strip()
                )
                if response not in ["y", "yes"]:
                    ezprinter.info("ℹ️ Operation cancelled by user")
                    return CSpellResult(
                        success=False,
                        message="Operation cancelled by user",
                        error="user_cancelled",
                    )

            # Add all dictionaries
            ezprinter.info(
                f"🔄 Processing {dict_info['total_files']} dictionary files..."
            )

            try:
                result = self._dictionary_service.add_all_dictionaries(project_path)
            except (DictionaryServiceError, CSpellServiceError) as e:
                logger.error(f"Add all dictionaries service error: {e}", exc_info=True)
                raise CSpellDictionaryInterfaceError(
                    f"Failed to add all dictionaries: {e.message}",
                    operation="add_all_dictionaries",
                    details=str(e),
                ) from e
            except Exception as e:
                logger.error(
                    f"Unexpected error during dictionary addition: {e}", exc_info=True
                )
                raise CSpellDictionaryInterfaceError(
                    f"An unexpected error occurred: {e}",
                    operation="add_all_dictionaries",
                    details=str(e),
                ) from e

            # Return results
            if result.success:
                ezprinter.success(
                    f"✅ {result.files_processed} dictionaries added successfully"
                )
                return CSpellResult(
                    success=True,
                    message=f"{result.files_processed} dictionaries added successfully",
                )
            else:
                ezprinter.error("❌ No dictionaries could be added")
                return CSpellResult(
                    success=False,
                    message="No dictionaries could be added",
                    error="all_dictionaries_failed",
                )

        except CSpellDictionaryInterfaceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in perform_add_all_dictionaries: {e}")
            raise CSpellDictionaryInterfaceError(
                f"Dictionary addition failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def perform_list_dictionaries(
        self, project_path: Path | None = None
    ) -> CSpellResult:
        """
        List all available dictionaries with integrated UI.

        Args:
            project_path: Path to the project (defaults to current directory)

        Returns:
            SpellResult: Result of the dictionary listing operation

        Raises:
            DictionaryInterfaceError: If dictionary listing fails
        """
        try:
            if project_path is None:
                project_path = Path.cwd()

            # Get dictionary information
            try:
                dict_info_raw = self._dictionary_service.get_dictionary_info(
                    project_path
                )
                dict_info = format_dictionary_info(dict_info_raw)
            except (DictionaryServiceError, CSpellServiceError) as e:
                logger.error(f"Dictionary info service error: {e}", exc_info=True)
                raise CSpellDictionaryInterfaceError(
                    f"Failed to get dictionary information: {e.message}",
                    operation="get_dictionary_info",
                    details=str(e),
                ) from e
            except Exception as e:
                logger.error(
                    f"Unexpected error getting dictionary info: {e}", exc_info=True
                )
                raise CSpellDictionaryInterfaceError(
                    f"An unexpected error occurred: {e}",
                    operation="get_dictionary_info",
                    details=str(e),
                ) from e

            # Display dictionary information
            if not dict_info["directory_exists"]:
                ezprinter.error("❌ .cspell-dict directory not found")
                ezprinter.info(
                    "💡 Create the directory and add dictionary files (.txt)"
                )
                return CSpellResult(
                    success=False,
                    message=".cspell-dict directory not found",
                    error="dict_dir_not_found",
                )

            if dict_info["total_files"] == 0:
                ezprinter.warning("⚠️  .cspell-dict directory is empty")
                ezprinter.info("💡 Add .txt files with one word per line")
                return CSpellResult(
                    success=True,
                    message="No dictionaries found",
                    data={"dictionaries": []},
                )

            # Display dictionaries
            ezprinter.success(f"📚 Found {dict_info['total_files']} dictionary files")
            print("")

            # Format dictionary list for panel display
            dict_list = "\n".join(f"📄 {file_path}" for file_path in dict_info["files"])

            # Display in a panel
            content = ezprinter.create_info_panel(
                title="Available Dictionaries",
                content=dict_list,
                border_style="cyan",
                width=90,
            )
            ezconsole.print(content)

            return CSpellResult(
                success=True,
                message=f"Found {dict_info['total_files']} dictionary files",
                data={
                    "dictionaries": dict_info["files"],
                    "total_files": dict_info["total_files"],
                    "total_words": dict_info.get("total_words", 0),
                },
            )

        except CSpellDictionaryInterfaceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in perform_list_dictionaries: {e}")
            raise CSpellDictionaryInterfaceError(
                f"Dictionary listing failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e
