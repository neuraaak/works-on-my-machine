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

# Local imports
from ...exceptions.cspell import (
    CheckServiceError,
    CSpellInterfaceError,
    CSpellServiceError,
)
from ...services import CSpellCheckerService
from ...shared.results.cspell_results import (
    CSpellInstallResult,
    ProjectSetupResult,
    SpellResult,
)
from ...ui.common.ezpl_bridge import ezprinter
from ...utils.cspell import (
    export_spell_results_to_json,
    format_project_status,
)

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
                operation="check_availability",
                details=str(e),
            ) from e
        except Exception as e:
            logger.error(
                f"Unexpected error during CSpell availability check: {e}", exc_info=True
            )
            raise CSpellInterfaceError(
                f"An unexpected error occurred during CSpell availability check: {e}",
                operation="check_availability",
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
            ezprinter.print_header("CSpell Installation")

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
                        operation="install_cspell",
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
                operation="install_cspell",
                details=str(e),
            ) from e

    # ///////////////////////////////////////////////////////////////
    # PRIVATE METHODS
    # ///////////////////////////////////////////////////////////////

    def _ensure_cspell_available(self, _operation: str) -> CSpellInstallResult | None:
        """
        Ensure CSpell is available, return error result if not.

        Args:
            operation: Name of operation that requires CSpell

        Returns:
            CSpellInstallResult | None: Error result if not available, None if available
        """
        try:
            if not self.cspell_available:
                ezprinter.error("❌ CSpell is not installed")
                ezprinter.info('💡 Install using: "womm spell install"')
                return CSpellInstallResult(
                    success=False,
                    message="CSpell is not installed",
                    error="cspell_not_installed",
                    cspell_installed=False,
                    install_time=0.0,
                )
            return None
        except CSpellInterfaceError as e:
            logger.error(f"CSpell availability check failed: {e}", exc_info=True)
            raise CSpellInterfaceError(
                f"CSpell availability check failed: {e}",
                operation="ensure_availability",
                details=str(e),
            ) from e

    def perform_setup_project(
        self, project_name: str, project_type: str | None = None
    ) -> ProjectSetupResult:
        """
        Set up CSpell configuration for a project with integrated UI.

        Args:
            project_name: Name of the project
            project_type: Type of the project (optional)

        Returns:
            ProjectSetupResult: Result of the project setup operation

        Raises:
            CSpellInterfaceError: If project setup fails
        """
        try:
            ezprinter.print_header("CSpell Project Setup")

            # Check CSpell availability - early return if not available
            cspell_check = self._ensure_cspell_available("project setup")
            if cspell_check is not None:  # Error occurred
                return cspell_check

            with ezprinter.create_spinner_with_status(
                "Setting up CSpell configuration..."
            ) as (
                progress,
                task,
            ):
                # Determine project path
                progress.update(task, status="Determining project path...")
                project_path = (
                    Path.cwd() / project_name if project_name != "." else Path.cwd()
                )

                # Use CSpellCheckerService for setup
                progress.update(task, status="Creating CSpell configuration...")
                try:
                    result = self._checker_service.setup_project(
                        project_path, project_type, project_name
                    )
                    success = result.success
                except (CSpellServiceError, CheckServiceError) as e:
                    logger.error(f"Project setup service error: {e}", exc_info=True)
                    raise CSpellInterfaceError(
                        f"Failed to setup project CSpell configuration: {e.message}",
                        operation="setup_project",
                        details=str(e),
                    ) from e
                except Exception as e:
                    logger.error(
                        f"Unexpected error during project setup: {e}", exc_info=True
                    )
                    raise CSpellInterfaceError(
                        f"An unexpected error occurred: {e}",
                        operation="setup_project",
                        details=str(e),
                    ) from e

                if success:
                    progress.update(task, status="Configuration created successfully!")
                    ezprinter.success(
                        f"✅ CSpell configured for {project_name} ({result.project_type})"
                    )
                    ezprinter.success("✅ CSpell setup completed successfully")
                    return ProjectSetupResult(
                        success=True,
                        message=f"CSpell configured for {project_name} ({result.project_type})",
                        project_path=project_path,
                        project_type=result.project_type,
                        config_created=True,
                        setup_time=0.0,
                    )
                else:
                    progress.update(task, status="Configuration failed")
                    ezprinter.error("❌ Failed to setup CSpell configuration")
                    return ProjectSetupResult(
                        success=False,
                        message="Failed to create CSpell configuration",
                        error="setup_failed",
                        project_path=project_path,
                        config_created=False,
                        setup_time=0.0,
                    )

        except CSpellInterfaceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in perform_setup_project: {e}")
            raise CSpellInterfaceError(
                f"Project setup failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def display_project_status(self, project_path: Path | None = None) -> SpellResult:
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

            ezprinter.print_header("CSpell Project Status")

            # Check and display CSpell availability (non-blocking for status command)
            if not self.cspell_available:
                ezprinter.error("❌ CSpell is not installed")
                ezprinter.info('💡 Install using: "womm spell install"')

            with ezprinter.create_spinner_with_status("Analyzing project...") as (
                progress,
                task,
            ):
                progress.update(task, status="Gathering project information...")

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
                        operation="get_project_status",
                        details=str(e),
                    ) from e
                except Exception as e:
                    logger.error(
                        f"Unexpected error during status check: {e}", exc_info=True
                    )
                    raise CSpellInterfaceError(
                        f"An unexpected error occurred: {e}",
                        operation="get_project_status",
                        details=str(e),
                    ) from e

                progress.update(task, status="Analyzing configuration...")

                # Format status with additional information
                status = format_project_status(status)

                progress.update(task, status="Status analysis complete!")

            # Display results with nice UI (AFTER spinner closes)
            print("")
            if status["config_exists"]:
                ezprinter.success("✅ CSpell configuration found")
                ezprinter.system(f"📁 Words count: {status.get('words_count', 0)}")
            else:
                ezprinter.error("❌ No CSpell configuration found")
                ezprinter.system("💡 Run: womm spell setup <project_name>")

            # Display status with nice formatting
            print("")
            configured_text = "✅" if status.get("config_exists") else "❌"
            ezprinter.system(f"Project configured: {configured_text}")

            if status.get("config_path"):
                ezprinter.system(f"Config file: {status['config_path']}")

            if status.get("words_count"):
                ezprinter.info(f"Custom words: {status['words_count']}")

            return SpellResult(
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

    def perform_spell_check(
        self,
        path: Path | None = None,
        json_output: Path | None = None,
    ) -> SpellResult:
        """
        Perform spell check with integrated UI.

        Args:
            path: Path to check (defaults to current directory)
            json_output: Optional path to export results as JSON

        Returns:
            SpellResult: Result of the spell check operation

        Raises:
            CSpellInterfaceError: If spell check fails
        """
        try:
            if path is None:
                path = Path.cwd()

            ezprinter.print_header("Spell Check")

            # Check CSpell availability - early return if not available
            cspell_check = self._ensure_cspell_available("spell check")
            if cspell_check is not None:  # Error occurred
                return cspell_check

            with ezprinter.create_spinner_with_status("Running spell check...") as (
                progress,
                task,
            ):
                progress.update(task, status="Checking files...")

                # Use CSpellCheckerService for the actual spell check
                try:
                    spell_result = self._checker_service.run_spellcheck(path)
                except (CheckServiceError, CSpellServiceError) as e:
                    logger.error(f"Spell check service error: {e}", exc_info=True)
                    raise CSpellInterfaceError(
                        f"Failed to run spell check: {e.message}",
                        operation="run_spellcheck",
                        details=str(e),
                    ) from e
                except Exception as e:
                    logger.error(
                        f"Unexpected error during spell check: {e}", exc_info=True
                    )
                    raise CSpellInterfaceError(
                        f"An unexpected error occurred: {e}",
                        operation="run_spellcheck",
                        details=str(e),
                    ) from e

                if spell_result.success or spell_result.issues_found > 0:
                    progress.update(task, status="Spell check completed!")

                    # Convert to dict format for compatibility
                    summary = {
                        "files_checked": spell_result.files_checked,
                        "issues_found": spell_result.issues_found,
                    }
                    issues = spell_result.issues or []

                    if issues:
                        ezprinter.warning(
                            f"⚠️  Spell check completed with {summary['issues_found']} issues found in {summary['files_checked']} files"
                        )
                        message = f"Spell check completed with {summary['issues_found']} issues found"
                    else:
                        ezprinter.success(
                            "✅ Spell check completed successfully - No issues found"
                        )
                        message = "Spell check completed successfully - No issues found"

                    # Display issues if present
                    if issues:
                        ezprinter.debug(f"📋 Found {len(issues)} spelling issues:")
                        print("")

                        # Use the function UI dedicated to display the table
                        try:
                            from ...ui import display_spell_issues_table

                            display_spell_issues_table(issues)
                            print("")
                        except Exception as e:
                            logger.warning(f"Failed to display spell issues table: {e}")

                    # Export JSON if requested
                    if json_output is not None:
                        try:
                            export_file = export_spell_results_to_json(
                                path, summary, issues, json_output
                            )
                            ezprinter.success(f"Results exported to: {export_file}")
                            ezprinter.system(
                                f"Summary: {summary['issues_found']} issues in {summary['files_checked']} files"
                            )
                        except Exception as e:
                            logger.warning(
                                f"Failed to export spell results to JSON: {e}"
                            )

                    return SpellResult(
                        success=True,
                        message=message,
                        data={
                            "path": str(path),
                            "summary": summary,
                            "issues": issues,
                            "json_output": json_output,
                        },
                    )
                else:
                    progress.update(task, status="Spell check failed")
                    ezprinter.error("❌ Spell check failed")
                    message = "Spell check failed"

                    return SpellResult(
                        success=False,
                        message=message,
                        error="spellcheck_failed",
                        data={"path": str(path)},
                    )

        except CSpellInterfaceError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error in perform_spell_check: {e}")
            raise CSpellInterfaceError(
                f"Spell check failed: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e
