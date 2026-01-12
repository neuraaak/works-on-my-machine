#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CSPELL CHECKER SERVICE - CSpell Checker Service
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
CSpell Checker Service - Singleton service for CSpell verification operations.

Handles CSpell installation checks, project setup, spell checking,
and project status verification.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import logging
import shutil
import time
from pathlib import Path
from threading import Lock
from typing import ClassVar

# Local imports
from ...exceptions.cspell import CheckServiceError, CSpellServiceError
from ...shared.results import CSpellCheckResult, CSpellConfigResult
from ...utils.womm_setup import get_womm_installation_path
from ..common.command_runner_service import CommandRunnerService

# ///////////////////////////////////////////////////////////////
# MODULE LOGGER
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# CSPELL CHECKER SERVICE CLASS
# ///////////////////////////////////////////////////////////////


class CSpellCheckerService:
    """Singleton service for CSpell verification operations."""

    _instance: ClassVar[CSpellCheckerService | None] = None
    _initialized: ClassVar[bool] = False
    _lock: ClassVar[Lock] = Lock()

    def __new__(cls) -> CSpellCheckerService:
        """Create or return the singleton instance.

        Returns:
            CSpellCheckerService: The singleton instance
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize CSpell checker service (only once)."""
        if CSpellCheckerService._initialized:
            return

        self.logger = logging.getLogger(__name__)
        self._command_runner = CommandRunnerService()
        CSpellCheckerService._initialized = True

    # ///////////////////////////////////////////////////////////////
    # PRIVATE HELPER METHODS - Inlined from cspell utils
    # ///////////////////////////////////////////////////////////////

    @staticmethod
    def _get_template_path(project_type: str) -> Path:
        """Get template path for project type."""
        devtools_path = get_womm_installation_path()

        if project_type == "python":
            return (
                devtools_path
                / "languages"
                / "python"
                / "templates"
                / "cspell.json.template"
            )
        elif project_type == "javascript":
            return (
                devtools_path
                / "languages"
                / "javascript"
                / "templates"
                / "cspell.json.template"
            )
        else:
            raise CSpellServiceError(
                message=f"Project type not supported: {project_type}",
                operation="get_template_path",
                details="Only 'python' and 'javascript' project types are supported",
            )

    @staticmethod
    def _read_template(template_path: Path) -> str:
        """Read template file content."""
        if not template_path.exists():
            raise CheckServiceError(
                message=f"Template not found: {template_path}",
                operation="template_loading",
                reason=f"Template not found: {template_path}",
                details="CSpell template file is missing from devtools installation",
            )

        try:
            return template_path.read_text(encoding="utf-8")
        except (PermissionError, OSError) as e:
            raise CheckServiceError(
                message=f"Failed to read template file: {e}",
                operation="template_reading",
                reason=f"Failed to read template file: {e}",
                details=f"Cannot access template file: {template_path}",
            ) from e

    @staticmethod
    def _process_template(template_content: str, project_name: str) -> str:
        """Process template by replacing placeholders."""
        return template_content.replace("{{PROJECT_NAME}}", project_name)

    @staticmethod
    def _read_cspell_config(config_path: Path) -> dict[str, object]:
        """Read CSpell configuration from JSON file."""
        import json

        try:
            if not config_path.exists():
                raise CheckServiceError(
                    message="CSpell configuration file does not exist",
                    operation="config_access",
                    reason="CSpell configuration file does not exist",
                    details="Run setup_project first to create configuration",
                )
            return json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise CheckServiceError(
                message=f"Failed to parse configuration file: {e}",
                operation="config_parsing",
                reason=f"Failed to parse configuration file: {e}",
                details=f"Invalid JSON in configuration file: {config_path}",
            ) from e

    @staticmethod
    def _get_config_words_count(config: dict[str, object]) -> int:
        """Get words count from configuration."""
        return len(config.get("words", []))

    @staticmethod
    def _get_config_dictionaries(config: dict[str, object]) -> list[str]:
        """Get dictionaries list from configuration."""
        return config.get("dictionaries", [])

    @staticmethod
    def _parse_config_from_content(config_content: str) -> dict[str, object]:
        """Parse configuration from content string."""
        import json

        try:
            return json.loads(config_content)
        except json.JSONDecodeError as e:
            raise CheckServiceError(
                message=f"Failed to parse configuration content: {e}",
                operation="config_parsing",
                reason=str(e),
                details="Invalid JSON in configuration content",
            ) from e

    @staticmethod
    def _check_cspell_installed(command_runner: CommandRunnerService) -> bool:
        """Check if CSpell is installed using multiple methods."""
        import shutil

        from ...shared.configs.dependencies.devtools_config import DevToolsConfig

        cspell_config = DevToolsConfig.TOOL_CONFIGS.get("cspell", {})
        check_commands = cspell_config.get("check_commands", [])

        # Try each check command in order
        for cmd in check_commands:
            try:
                # Handle both string and list formats
                if isinstance(cmd, str):
                    # Direct command check via PATH
                    if shutil.which(cmd):
                        return True
                else:
                    # Command list (e.g., ["npx", "cspell"])
                    result = command_runner.run_silent([*cmd, "--version"])
                    if bool(result) and result.stdout.strip():
                        return True
            except Exception as e:
                logger.debug(f"Failed to check CSpell via {cmd}: {e}")
                continue

        # Fallback: check via npm global list
        try:
            result = command_runner.run_silent(["npm", "list", "-g", "cspell"])
            return bool(result) and "cspell@" in result.stdout
        except Exception as e:
            logger.debug(f"Failed to check CSpell via npm: {e}")
            return False

    @staticmethod
    def _detect_project_type(project_path: Path) -> str | None:
        """Detect project type."""
        # Python
        if any(
            (project_path / f).exists()
            for f in ["setup.py", "pyproject.toml", "requirements.txt"]
        ):
            return "python"

        # JavaScript/Node.js
        if any((project_path / f).exists() for f in ["package.json", "node_modules"]):
            return "javascript"

        return None

    @staticmethod
    def _parse_cspell_output(output: str) -> list[dict[str, str | int]]:
        """Parse CSpell output to extract spell checking issues.

        Expected format:
        womm/bin/refresh_env.cmd:105:100 - Unknown word (HKLM)
        womm/cli.py:129:72 - Unknown word (ezpl)
        """
        issues: list[dict[str, str | int]] = []

        if not output:
            return issues

        try:
            lines = output.strip().split("\n")
            for line in lines:
                if not line.strip():
                    continue

                # Parse line format: file:line:col - Unknown word (word)
                if "- Unknown word" in line:
                    # Split by first colon to get file path
                    if ":" not in line:
                        continue

                    parts = line.split(":", 2)
                    if len(parts) < 3:
                        continue

                    file_path = parts[0]

                    try:
                        line_num = int(parts[1])
                        col_num_str = parts[2].split(" ")[0]
                        col_num = int(col_num_str)
                    except ValueError:
                        line_num = 0
                        col_num = 0

                    # Extract word from parentheses
                    word = ""
                    if "(" in line and ")" in line:
                        word = line.split("(")[1].split(")")[0]

                    if word:  # Only add if we extracted a word
                        issues.append(
                            {
                                "file": file_path,
                                "line": line_num,
                                "column": col_num,
                                "word": word,
                            }
                        )
        except Exception as e:
            logging.warning(f"Failed to parse CSpell output: {e}")

        return issues

    # ///////////////////////////////////////////////////////////////
    # PUBLIC METHODS
    # ///////////////////////////////////////////////////////////////

    def is_installed(self) -> bool:
        """Check if CSpell is installed.

        Returns:
            bool: True if CSpell is available, False otherwise

        Raises:
            CSpellError: If CSpell detection fails unexpectedly
        """
        try:
            return self._check_cspell_installed(self._command_runner)
        except CheckServiceError:
            raise
        except Exception as e:
            raise CheckServiceError(
                message=f"Failed to check CSpell installation: {e}",
                operation="detection",
                reason=f"Failed to check CSpell installation: {e}",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def run_spellcheck(self, path: Path) -> CSpellCheckResult:
        """Run spell check and return detailed results.

        Args:
            path: Path to check for spelling errors

        Returns:
            SpellCheckResult: Spell check results with issues and summary

        Raises:
            CSpellError: If spell checking fails
            SpellServiceError: If spell check setup fails
        """
        start_time = time.time()
        try:
            # Input validation
            if not path:
                raise CSpellServiceError(
                    message="Path cannot be empty",
                    operation="run_spellcheck",
                    details="Invalid path provided for spell checking",
                )

            if not self.is_installed():
                return CSpellCheckResult(
                    success=False,
                    error="CSpell not installed - use: spellcheck --install",
                    target_path=path,
                    files_checked=0,
                    issues_found=0,
                    issues=[],
                    raw_output="",
                    raw_stderr="",
                    check_time=time.time() - start_time,
                )

            # Check if cspell is directly available in PATH
            cspell_path = shutil.which("cspell")
            cspell_direct_available = cspell_path is not None

            # Choose appropriate command
            if cspell_direct_available:
                cmd = [str(cspell_path), "lint", str(path)]
            else:
                cmd = ["npx", "cspell", "lint", str(path)]

            cmd.extend(["--no-progress", "--no-summary"])
            self.logger.debug(f"Checking: {path}")

            # Execute command
            try:
                result = self._command_runner.run_silent(cmd)
            except Exception as e:
                raise CheckServiceError(
                    message=f"Failed to execute CSpell command: {e}",
                    operation="execution",
                    reason=f"Failed to execute CSpell command: {e}",
                    details=f"Command: {' '.join(cmd)}",
                ) from e

            self.logger.debug(
                f"CSpell command result: success={bool(result)}, "
                f"returncode={result.returncode}"
            )
            self.logger.debug(f"CSpell stdout: {result.stdout}")
            self.logger.debug(f"CSpell stderr: {result.stderr}")

            # Parse output
            issues = self._parse_cspell_output(result.stdout) if result.stdout else []

            # Build issues_by_file dict: file -> set of unknown words
            issues_by_file: dict[str, set[str]] = {}
            for issue in issues:
                file_path = issue["file"]
                word = issue.get("word", "")
                if word:
                    if file_path not in issues_by_file:
                        issues_by_file[file_path] = set()
                    issues_by_file[file_path].add(word)

            # Count files and issues
            files_checked = len({issue["file"] for issue in issues}) if issues else 0
            issues_found = len(issues)

            # CSpell returns code 1 when errors are found, which is normal
            success = bool(result) or result.returncode == 1

            check_time = time.time() - start_time

            return CSpellCheckResult(
                success=success,
                message=f"Spell check completed: {issues_found} issues found in {files_checked} files",
                target_path=path,
                files_checked=files_checked,
                issues_found=issues_found,
                issues=issues,
                issues_by_file=issues_by_file,
                raw_output=result.stdout,
                raw_stderr=result.stderr,
                check_time=check_time,
            )

        except (CheckServiceError, CSpellServiceError):
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise CSpellServiceError(
                message=f"Spell checking failed: {e}",
                operation="run_spellcheck",
                details=f"Exception type: {type(e).__name__}",
            ) from e

    def get_project_status(self, project_path: Path) -> CSpellConfigResult:
        """Get detailed status of CSpell project configuration.

        Args:
            project_path: Path to the project directory

        Returns:
            CSpellConfigResult: Project status information

        Raises:
            SpellServiceError: If status retrieval fails unexpectedly
        """
        try:
            # Input validation
            if not project_path:
                raise CSpellServiceError(
                    message="Project path cannot be empty",
                    operation="get_project_status",
                    details="Invalid project path provided for status check",
                )

            # Check if CSpell config exists
            config_file = project_path / "cspell.json"
            if not config_file.exists():
                return CSpellConfigResult(
                    success=False,
                    error="CSpell configuration file does not exist",
                    config_path=None,
                    project_type=self._detect_project_type(project_path),
                    words_count=0,
                    dictionaries=[],
                )

            try:
                config_data = self._read_cspell_config(config_file)
                words_count = self._get_config_words_count(config_data)
                dictionaries = self._get_config_dictionaries(config_data)
            except Exception as e:
                self.logger.debug(f"Failed to read CSpell config: {e}")
                # Don't fail the entire status check for config reading issues
                words_count = 0
                dictionaries = []

            # Detect project type
            project_type = self._detect_project_type(project_path)

            return CSpellConfigResult(
                success=True,
                message="CSpell configuration found",
                config_path=config_file,
                project_type=project_type,
                words_count=words_count,
                dictionaries=dictionaries,
            )

        except CSpellServiceError:
            # Re-raise our custom exceptions
            raise
        except Exception as e:
            # Wrap unexpected external exceptions
            raise CSpellServiceError(
                message=f"Failed to get project status: {e}",
                operation="get_project_status",
                details=f"Exception type: {type(e).__name__}",
            ) from e
