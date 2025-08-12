#!/usr/bin/env python3
"""
Spell Manager - Centralized spell checking logic for WOMM projects.
Handles CSpell installation, configuration, and spell checking operations.
"""

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .results import BaseResult as Result


@dataclass
class SpellResult(Result):
    """Result of a spell checking operation."""

    data: dict = None

    def __post_init__(self):
        if self.data is None:
            self.data = {}


@dataclass
class SpellSummary(Result):
    """Summary of spell checking operations."""

    total_files: int = 0
    files_with_errors: int = 0
    total_errors: int = 0
    errors_by_file: dict = None
    suggestions: List[str] = None

    def __post_init__(self):
        if self.errors_by_file is None:
            self.errors_by_file = {}
        if self.suggestions is None:
            self.suggestions = []


class SpellManager:
    """Manages spell checking operations with CSpell."""

    def __init__(self):
        self._cspell_available = None  # Lazy-loaded availability check

    @property
    def cspell_available(self) -> bool:
        """Check if CSpell is available (lazy-loaded)."""
        if self._cspell_available is None:
            self._cspell_available = self._check_cspell_availability()
        return self._cspell_available

    @cspell_available.setter
    def cspell_available(self, value: bool):
        """Allow manual override of cspell availability."""
        self._cspell_available = value

    def _check_cspell_availability(self) -> bool:
        """Check if CSpell is available in the system."""
        try:
            # Check via shutil.which (PATH) - fastest check
            if shutil.which("cspell") is not None:
                return True

            # Check via npx (modern npm approach) with shorter timeout
            import platform

            from .cli_manager import CLIManager

            # Use shorter timeout for availability checks to avoid blocking startup
            cli = CLIManager(timeout=5)  # 5 seconds timeout instead of 30

            if platform.system() == "Windows":
                result = cli.run_silent(["cmd", "/c", "npx", "cspell", "--version"])
            else:
                result = cli.run_silent(["npx", "cspell", "--version"])

            if result.success:
                return True

            # Check via npm (fallback) with short timeout
            if platform.system() == "Windows":
                result = cli.run_silent(["cmd", "/c", "npm", "list", "-g", "cspell"])
            else:
                result = cli.run_silent(["npm", "list", "-g", "cspell"])
            return result.success and "cspell@" in result.stdout
        except Exception:
            # If any exception occurs (including timeout), assume CSpell is not available
            return False

    def setup_dictionaries(self) -> SpellResult:
        """Install essential CSpell dictionaries globally."""
        try:
            # Ensure CSpell is available first
            if not self.cspell_available:
                return SpellResult(
                    success=False,
                    message="CSpell must be installed before setting up dictionaries",
                    error="cspell_not_available",
                )

            from .cli_manager import run_command

            # Install essential dictionaries
            dictionaries = [
                "@cspell/dict-typescript",
                "@cspell/dict-node",
                "@cspell/dict-npm",
                "@cspell/dict-html",
                "@cspell/dict-css",
                "@cspell/dict-python",
                "@cspell/dict-django",
                "@cspell/dict-flask",
                "@cspell/dict-companies",
                "@cspell/dict-software-terms",
                "@cspell/dict-lorem-ipsum",
            ]

            failed_dictionaries = []
            installed_count = 0

            for dictionary in dictionaries:
                try:
                    dict_result = run_command(
                        ["npm", "install", "-g", dictionary],
                        f"Installing dictionary {dictionary}",
                    )
                    if dict_result.success:
                        installed_count += 1
                    else:
                        failed_dictionaries.append(dictionary)
                except Exception:
                    failed_dictionaries.append(dictionary)

            # Return results based on success rate
            if installed_count == 0:
                return SpellResult(
                    success=False,
                    message="Failed to install any dictionaries",
                    error="all_dictionaries_failed",
                )
            elif failed_dictionaries:
                return SpellResult(
                    success=True,
                    message=f"Installed {installed_count}/{len(dictionaries)} dictionaries successfully",
                    error=f"failed_dictionaries:{','.join(failed_dictionaries)}",
                )
            else:
                return SpellResult(
                    success=True,
                    message=f"All {installed_count} essential dictionaries installed successfully",
                )

        except Exception as e:
            return SpellResult(
                success=False,
                message=f"Dictionary setup error: {e}",
                error="dictionary_setup_error",
            )

    def setup_project(
        self, project_name: str, project_type: Optional[str] = None
    ) -> SpellResult:
        """Set up CSpell configuration for a project."""
        try:
            project_path = (
                Path.cwd() / project_name if project_name != "." else Path.cwd()
            )

            # Detect project type if not provided
            if not project_type:
                project_type = self._detect_project_type(project_path)

            # Create cspell.json configuration
            config = self._create_cspell_config(project_type)
            config_path = project_path / "cspell.json"

            import json

            config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

            return SpellResult(
                success=True,
                message=f"CSpell configured for {project_name} ({project_type})",
            )

        except Exception as e:
            return SpellResult(
                success=False,
                message=f"Failed to setup CSpell: {e}",
                error="setup_failed",
            )

    def get_project_status(self, project_path: Optional[Path] = None) -> SpellResult:
        """Get CSpell configuration status for a project."""
        if project_path is None:
            project_path = Path.cwd()

        try:
            config_path = project_path / "cspell.json"
            dict_dir = project_path / ".cspell-dict"

            status = {
                "config_exists": config_path.exists(),
                "dict_dir_exists": dict_dir.exists(),
                "dict_files": [],
                "total_words": 0,
            }

            if dict_dir.exists():
                dict_files = list(dict_dir.glob("*.txt"))
                status["dict_files"] = [f.name for f in dict_files]
                status["total_words"] = sum(
                    len(f.read_text().splitlines()) for f in dict_files
                )

            return SpellResult(
                success=True, message="Project status retrieved", data=status
            )

        except Exception as e:
            return SpellResult(
                success=False,
                message=f"Failed to get status: {e}",
                error="status_failed",
            )

    def add_words(
        self, words: List[str], project_path: Optional[Path] = None
    ) -> SpellResult:
        """Add words to CSpell configuration."""
        if project_path is None:
            project_path = Path.cwd()

        try:
            config_path = project_path / "cspell.json"

            if not config_path.exists():
                return SpellResult(
                    success=False,
                    message="No cspell.json found. Run 'womm spell setup' first.",
                    error="no_config",
                )

            import json

            config = json.loads(config_path.read_text(encoding="utf-8"))

            if "words" not in config:
                config["words"] = []

            # Add new words
            added_count = 0
            for word in words:
                if word not in config["words"]:
                    config["words"].append(word)
                    added_count += 1

            config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

            return SpellResult(
                success=True, message=f"Added {added_count} new words to configuration"
            )

        except Exception as e:
            return SpellResult(
                success=False,
                message=f"Failed to add words: {e}",
                error="add_words_failed",
            )

    def add_words_from_file(
        self, file_path: Path, project_path: Optional[Path] = None
    ) -> SpellResult:
        """Add words from a file to CSpell configuration."""
        if project_path is None:
            project_path = Path.cwd()

        try:
            if not file_path.exists():
                return SpellResult(
                    success=False,
                    message=f"File not found: {file_path}",
                    error="file_not_found",
                )

            words = file_path.read_text(encoding="utf-8").splitlines()
            words = [w.strip() for w in words if w.strip()]

            return self.add_words(words, project_path)

        except Exception as e:
            return SpellResult(
                success=False,
                message=f"Failed to add words from file: {e}",
                error="file_read_failed",
            )

    def check_spelling(
        self, path: Path, fix_mode: bool = False, json_output: bool = False
    ) -> SpellSummary:
        """Check spelling in files using CSpell."""
        if not self.cspell_available:
            return SpellSummary(
                success=False,
                message="CSpell is not available. Run 'womm spell install' first.",
                error="cspell_not_available",
            )

        from .cli_manager import run_command

        # Build CSpell command
        cmd = ["cspell"]
        if fix_mode:
            cmd.extend(["--fix"])
        else:
            cmd.extend(["--check"])
            if json_output:
                # CSpell JSON output
                cmd.extend(["--no-progress", "--show-context", "--json"])

        cmd.append(str(path))

        result = run_command(cmd, f"Spell checking {path}")

        # Parse CSpell output
        summary = self._parse_cspell_output(result, path, json_output=json_output)
        summary.success = summary.total_errors == 0

        return summary

    def _detect_project_type(self, project_path: Path) -> str:
        """Detect project type based on files present."""
        if (project_path / "package.json").exists():
            return "javascript"
        elif (project_path / "pyproject.toml").exists() or (
            project_path / "setup.py"
        ).exists():
            return "python"
        else:
            return "generic"

    def _create_cspell_config(self, project_type: str) -> dict:
        """Create CSpell configuration for project type."""
        config = {
            "version": "0.2",
            "language": "en",
            "words": [],
            "ignoreWords": [],
            "patterns": [],
        }

        if project_type == "python":
            config.update(
                {
                    "language": "en",
                    "dictionaries": ["python", "softwareTerms"],
                    "ignorePaths": [
                        "venv/",
                        ".venv/",
                        "__pycache__/",
                        "*.pyc",
                        "*.pyo",
                        "*.pyd",
                        ".pytest_cache/",
                        ".coverage",
                        "htmlcov/",
                    ],
                }
            )
        elif project_type == "javascript":
            config.update(
                {
                    "language": "en",
                    "dictionaries": ["typescript", "node", "npm", "html", "css"],
                    "ignorePaths": [
                        "node_modules/",
                        "dist/",
                        "build/",
                        ".next/",
                        "coverage/",
                    ],
                }
            )

        return config

    def _parse_cspell_output(
        self, result, _path: Path, json_output: bool = False
    ) -> SpellSummary:
        """Parse CSpell command output to extract errors and suggestions."""
        summary = SpellSummary(success=True, message="No spelling errors found")

        if result.success and not json_output:
            return summary

        if json_output and result.stdout:
            try:
                import json

                data = json.loads(result.stdout)
                # Expecting an array of issues or an object depending on cspell version
                items = data if isinstance(data, list) else data.get("issues") or []
                summary.data = data
                summary.total_errors = len(items)
                summary.files_with_errors = len(
                    {it.get("filename") for it in items if isinstance(it, dict)}
                )
                summary.message = "JSON diagnostics available"
                return summary
            except Exception as e:
                # Fall back to stderr parsing
                import logging

                logging.debug(f"Failed to parse CSpell JSON output: {e}")

        # Parse error output (stderr) fallback
        lines = (result.stderr or "").splitlines()
        current_file = None
        errors_by_file = {}

        for line in lines:
            if ":" in line and Path(line.split(":")[0]).exists():
                parts = line.split(":")
                current_file = parts[0]
                if current_file not in errors_by_file:
                    errors_by_file[current_file] = []
                errors_by_file[current_file].append(line.strip())

        summary.errors_by_file = errors_by_file
        summary.files_with_errors = len(errors_by_file)
        summary.total_errors = sum(len(errors) for errors in errors_by_file.values())
        summary.total_files = 1  # Simplified for now

        if summary.total_errors > 0:
            summary.success = False
            summary.message = f"Found {summary.total_errors} spelling errors in {summary.files_with_errors} files"
            summary.suggestions = [
                "Run 'womm spell check --fix' to interactively fix errors",
                "Run 'womm spell add <word>' to add words to dictionary",
                "Check .cspell-dict/ directory for custom dictionaries",
            ]
        else:
            summary.success = True
            summary.message = "No spelling errors found"

        return summary


# GLOBAL INSTANCE
########################################################

spell_manager = SpellManager()
