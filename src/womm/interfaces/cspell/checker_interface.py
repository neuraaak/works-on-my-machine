#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CSPELL CHECKER INTERFACE - CSpell Checker Interface
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
CSpell Checker Interface - Interface for spell checking operations.

Handles CSpell installation, project setup, spell checking, and status verification.
Provides unified interface for spell checking operations.

This interface orchestrates CSpellCheckerService and converts service exceptions
to interface exceptions following the MEF pattern.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import time
from pathlib import Path

# Third-party imports
from rich.progress import TaskID

# Local imports
from ...exceptions.cspell import (
    CheckServiceError,
    CSpellInterfaceError,
    CSpellServiceError,
)
from ...services import CSpellCheckerService
from ...shared.results import CSpellInstallResult, CSpellResult
from ...ui.common import ezprinter
from ...ui.cspell import display_spell_status_table
from ...utils.cspell import export_spell_results_to_json, format_project_status

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# MAIN CLASS
# ///////////////////////////////////////////////////////////////


class CSpellCheckerInterface:
    """Interface for managing spell checking operations with CSpell.

    This class provides a high-level interface for CSpell verification operations,
    handling UI interactions and orchestrating the CSpellCheckerService.
    """

    def __init__(self) -> None:
        """
        Initialize CSpell checker interface.

        Raises:
            SpellInterfaceError: If interface initialization fails
        """
        try:
            self._checker_service = CSpellCheckerService()
            self._cspell_available: bool | None = None  # Cached availability check
            self._cache_timestamp: float | None = None  # Cache invalidation timestamp
            self._cache_timeout: int = 30  # Cache timeout in seconds
        except Exception as e:
            logger.error(
                f"Failed to initialize CSpellCheckerInterface: {e}", exc_info=True
            )
            raise CSpellInterfaceError(
                f"Spell checker interface initialization failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    @property
    def cspell_available(self) -> bool:
        """
        Check if CSpell is available (cached with timeout).

        Returns:
            bool: True if CSpell is available, False otherwise

        Raises:
            CSpellInterfaceError: If CSpell availability check fails
        """
        try:
            current_time = time.time()

            # Check if cache is valid (exists and not expired)
            if (
                self._cspell_available is not None
                and self._cache_timestamp is not None
                and (current_time - self._cache_timestamp) < self._cache_timeout
            ):
                return self._cspell_available

            # Cache miss or expired - check with service
            self._cspell_available = self._checker_service.is_installed()
            self._cache_timestamp = current_time
            return self._cspell_available

        except (CheckServiceError, CSpellServiceError) as e:
            logger.error(f"CSpell availability check service error: {e}", exc_info=True)
            raise CSpellInterfaceError(
                f"CSpell availability check failed: {e.message}",
                details=str(e),
            ) from e
        except Exception as e:
            logger.error(
                f"Unexpected error during CSpell availability check: {e}", exc_info=True
            )
            raise CSpellInterfaceError(
                f"An unexpected error occurred during CSpell availability check: {e}",
                details=str(e),
            ) from e

    @cspell_available.setter
    def cspell_available(self, value: bool) -> None:
        """
        Set CSpell availability (updates cache).

        Args:
            value: Availability status
        """
        self._cspell_available = value
        self._cache_timestamp = time.time()

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def invalidate_cspell_cache(self) -> None:
        """Invalidate CSpell availability cache."""
        self._cspell_available = None
        self._cache_timestamp = None

    def install_cspell(self) -> CSpellInstallResult:
        """Install CSpell globally with integrated UI.

        Returns:
            CSpellInstallResult: Result of the installation operation

        Raises:
            CSpellInterfaceError: If CSpell installation fails
        """
        try:
            # Check if CSpell is already available
            if self.cspell_available:
                ezprinter.success("CSpell is already available")
            else:
                ezprinter.error("CSpell is not available")

                # Install CSpell via DevToolsManager
                ezprinter.info("Installing CSpell...")
                try:
                    from ..dependencies.devtools_interface import DevToolsInterface

                    devtools = DevToolsInterface()
                    install_result = devtools._install_javascript_tool("cspell")

                    if not install_result:
                        return CSpellInstallResult(
                            success=False,
                            message="Failed to install CSpell",
                            error="cspell_install_failed",
                            cspell_installed=False,
                            install_time=0.0,
                        )

                    # Update cache
                    self.invalidate_cspell_cache()
                    self._cspell_available = True
                    ezprinter.success("CSpell installed successfully")
                except Exception as e:
                    logger.error(f"Failed to install CSpell: {e}", exc_info=True)
                    raise CSpellInterfaceError(
                        f"Failed to install CSpell: {e}",
                        details=str(e),
                    ) from e

            return CSpellInstallResult(
                success=True,
                message="CSpell is available",
                cspell_installed=self.cspell_available,
                install_time=0.0,
            )

        except CSpellInterfaceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in install_cspell: {e}", exc_info=True)
            raise CSpellInterfaceError(
                f"CSpell installation failed: {e}",
                details=str(e),
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _ensure_cspell_available(self, _operation: str) -> CSpellResult | None:
        """
        Ensure CSpell is available, return error result if not.

        Args:
            operation: Name of operation that requires CSpell

        Returns:
            CSpellResult | None: Error result if not available, None if available
        """
        try:
            if not self.cspell_available:
                ezprinter.error("❌ CSpell is not installed")
                ezprinter.info('💡 Install using: "womm spell install"')
                return CSpellResult(
                    success=False,
                    message="CSpell is not installed",
                    error="cspell_not_installed",
                )
            return None
        except CSpellInterfaceError as e:
            logger.error(f"CSpell availability check failed: {e}", exc_info=True)
            raise CSpellInterfaceError(
                f"CSpell availability check failed: {e}",
                details=str(e),
            ) from e

    def display_project_status(self, project_path: Path | None = None) -> CSpellResult:
        """
        Get and display CSpell configuration status for a project with integrated UI.

        Args:
            project_path: Path to the project (defaults to current directory)

        Returns:
            SpellResult: Result of the status check operation

        Raises:
            CSpellInterfaceError: If status check fails
        """
        try:
            if project_path is None:
                project_path = Path.cwd()

            # Check and display CSpell availability (non-blocking for status command)
            if not self.cspell_available:
                ezprinter.error("❌ CSpell is not installed")
                ezprinter.info('💡 Install using: "womm spell install"')

            # Use spinner for gathering status information
            with ezprinter.create_spinner_with_status("Analyzing project...") as (
                progress,
                task,
            ):
                task_id = TaskID(task)
                progress.update(task_id, status="Gathering project information...")

                # Use CSpellCheckerService for the actual status gathering
                try:
                    status_result = self._checker_service.get_project_status(
                        project_path
                    )
                    # Convert result to dict for compatibility
                    status = {
                        "cspell_installed": self._checker_service.is_installed(),
                        "config_exists": status_result.config_path is not None,
                        "config_path": (
                            str(status_result.config_path)
                            if status_result.config_path
                            else None
                        ),
                        "project_type": status_result.project_type,
                        "words_count": status_result.words_count,
                        "dictionaries": status_result.dictionaries or [],
                        "last_check": None,
                        "issues_count": 0,
                    }
                except (CSpellServiceError, CheckServiceError) as e:
                    logger.error(f"Status check service error: {e}", exc_info=True)
                    raise CSpellInterfaceError(
                        f"Failed to get project status: {e.message}",
                        details=str(e),
                    ) from e
                except Exception as e:
                    logger.error(
                        f"Unexpected error during status check: {e}", exc_info=True
                    )
                    raise CSpellInterfaceError(
                        f"An unexpected error occurred: {e}",
                        details=str(e),
                    ) from e

                progress.update(task_id, status="Analyzing configuration...")

                # Format status with additional information
                status = format_project_status(status)

                progress.update(task_id, status="Status analysis complete!")

            # Display results in panel (AFTER spinner closes)
            print("")
            display_spell_status_table(status)

            return CSpellResult(
                success=True,
                message="Project status retrieved successfully",
                data=status,
            )

        except CSpellInterfaceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in display_project_status: {e}")
            raise CSpellInterfaceError(
                f"Project status check failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def perform_cspell_lint(
        self,
        path: Path | None = None,
        json_export: bool = False,
        directory: Path | None = None,
        add_words: bool = False,
    ) -> CSpellResult:
        """
        Perform spell lint with integrated UI and optional JSON export.

        Lint mode provides a summary of unknown words by file instead of detailed issues.

        Args:
            path: Path to lint (defaults to current directory)
            json_export: Export results to default path ~/.womm/spell-results/
            directory: Custom path to export results as JSON
            add_words: Add detected unknown words to cspell.json

        Returns:
            SpellResult: Result of the spell lint operation

        Raises:
            CSpellInterfaceError: If spell lint fails
        """
        try:
            if path is None:
                path = Path.cwd()

            # Determine JSON export path based on flags
            export_path = None
            if json_export:
                # Use default path ~/.womm/spell-results/
                from ...utils.womm_setup import get_default_womm_path

                export_path = get_default_womm_path() / "spell-results"
            elif directory is not None:
                # Use custom path specified
                export_path = directory

            # Check CSpell availability - early return if not available
            cspell_check = self._ensure_cspell_available("spell lint")
            if cspell_check is not None:  # Error occurred
                return cspell_check

            # Use CSpellCheckerService for the actual spell lint
            with ezprinter.create_spinner_with_status("Running spell lint...") as (
                progress,
                task,
            ):
                task_id = TaskID(task)
                progress.update(task_id, status="Linting files...")

                try:
                    lint_result = self._checker_service.run_spellcheck(path)
                except (CheckServiceError, CSpellServiceError) as e:
                    logger.error(f"Spell lint service error: {e}", exc_info=True)
                    raise CSpellInterfaceError(
                        f"Failed to run spell lint: {e.message}",
                        details=str(e),
                    ) from e
                except Exception as e:
                    logger.error(
                        f"Unexpected error during spell lint: {e}", exc_info=True
                    )
                    raise CSpellInterfaceError(
                        f"An unexpected error occurred: {e}",
                        details=str(e),
                    ) from e

                if not (lint_result.success or lint_result.issues_found > 0):
                    progress.update(task_id, status="Spell lint failed")
                    raise CSpellInterfaceError(
                        "Spell lint failed",
                    )

                progress.update(task_id, status="Spell lint completed!")

            # Process results after spinner is complete
            # Convert to dict format for compatibility
            summary = {
                "files_checked": lint_result.files_checked,
                "issues_found": lint_result.issues_found,
            }
            issues = lint_result.issues or []
            issues_by_file = lint_result.issues_by_file or {}

            if issues_by_file:
                ezprinter.warning(
                    f"⚠️  Spell lint completed with {summary['issues_found']} unknown words found in {summary['files_checked']} files"
                )
                message = f"Spell lint completed with {summary['issues_found']} unknown words found"
            else:
                ezprinter.success(
                    "✅ Spell lint completed successfully - No issues found"
                )
                message = "Spell lint completed successfully - No issues found"

            # Display lint summary if present
            if issues_by_file:
                ezprinter.debug("📋 Unknown words by file:")
                print("")

                # Use the UI function to display the lint summary table
                try:
                    from ...ui.cspell import display_lint_summary

                    display_lint_summary(issues_by_file)
                    print("")
                except ImportError:
                    logger.warning(
                        "display_lint_summary not available, displaying issues list instead"
                    )
                    from ...ui.cspell import display_spell_issues_table

                    display_spell_issues_table(issues)
                    print("")
                except Exception as e:
                    logger.warning(f"Failed to display lint summary table: {e}")

            # Add words to cspell.json if requested
            if add_words and issues_by_file:
                try:
                    from . import CSpellDictionaryInterface

                    all_words = []
                    for words_set in issues_by_file.values():
                        all_words.extend(words_set)

                    if all_words:
                        dictionary = CSpellDictionaryInterface()
                        add_result = dictionary.perform_add_words(
                            words=all_words, project_path=path
                        )
                        if add_result.success:
                            ezprinter.success(
                                f"✅ Added {len(all_words)} words to cspell.json"
                            )
                        else:
                            ezprinter.warning(
                                "⚠️  Failed to add some words to cspell.json"
                            )
                except Exception as e:
                    logger.warning(f"Failed to add words to cspell.json: {e}")
                    ezprinter.warning(f"Could not auto-add words: {e}")

            # Export JSON if requested
            if export_path is not None:
                try:
                    export_file = export_spell_results_to_json(
                        path, summary, issues, export_path
                    )
                    ezprinter.success(f"Results exported to: {export_file}")
                    ezprinter.system(
                        f"Summary: {summary['issues_found']} issues in {summary['files_checked']} files"
                    )
                except Exception as e:
                    logger.warning(f"Failed to export lint results to JSON: {e}")

            return CSpellResult(
                success=True,
                message=message,
                data={
                    "path": str(path),
                    "summary": summary,
                    "issues": issues,
                    "issues_by_file": {
                        file: list(words) for file, words in issues_by_file.items()
                    },
                    "json_output": export_path,
                },
            )

        except CSpellInterfaceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in perform_spell_lint: {e}")
            raise CSpellInterfaceError(
                f"Spell lint failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e
