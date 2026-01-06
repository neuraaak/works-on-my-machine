#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CSPELL UTILS - CSpell Configuration Utilities
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
CSpell Utils - Utility functions for CSpell configuration and operations.
Pure utility functions without UI - used by SpellManager.
Handles CSpell configuration, project detection, and file operations.
"""

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import logging
import os
import platform
import shutil
from pathlib import Path

# Local imports
from ....common.security import run_silent

# Import specialized exceptions
from ...exceptions.spell import CSpellError, DictionaryError, SpellUtilityError
from ..system.user_path_utils import (
    deduplicate_path_entries,
    extract_path_from_reg_output,
)

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# CSPELL DETECTION UTILITIES
# ///////////////////////////////////////////////////////////////


def check_cspell_installed() -> bool:
    """
    Check if CSpell is installed.

    Returns:
        bool: True if CSpell is available, False otherwise

    Raises:
        CSpellError: If CSpell detection fails unexpectedly
    """
    try:
        # Check via shutil.which (PATH)
        cspell_path = shutil.which("cspell")

        if cspell_path is not None:
            logger.debug("CSpell found via shutil.which")
            return True

        # Check via npx (common fallback) - direct subprocess for Windows compatibility
        try:
            result = run_silent(
                "npx cspell --version",
                timeout=10,
            )

            logger.debug(
                f"npx cspell --version result: returncode={result.returncode}, stdout='{result.stdout.strip()}'"
            )
            if result.returncode == 0 and result.stdout.strip():
                logger.debug("CSpell found via npx")
                # Tentative d'ajout au PATH pour les futures utilisations
                try:
                    _try_add_cspell_to_path_if_found_via_npx()
                except Exception as e:
                    logger.debug(f"Failed to add CSpell to PATH: {e}")
                return True
        except Exception as e:
            logger.debug(f"npx cspell check failed: {e}")

        # Check via npm (final fallback)
        try:
            result = run_silent(["npm", "list", "-g", "cspell"])

            logger.debug(
                f"npm list -g cspell result: success={result.success}, stdout='{result.stdout}'"
            )
            return result.success and "cspell@" in result.stdout
        except Exception as e:
            logger.debug(f"npm list check failed: {e}")
            return False

    except Exception as e:
        # Wrap unexpected external exceptions
        raise CSpellError(
            operation="detection",
            reason=f"Failed to detect CSpell installation: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def _try_add_cspell_to_path_if_found_via_npx() -> bool:
    """
    Tente d'ajouter CSpell au PATH utilisateur si trouvé via npx pour optimiser les futures utilisations.

    Returns:
        bool: True if CSpell was added to PATH, False otherwise

    Raises:
        CSpellError: If PATH modification fails unexpectedly
    """
    try:
        # Vérifier que npm est disponible d'abord
        npm_path = shutil.which("npm")
        if not npm_path:
            logger.debug("npm not found in PATH")
            return False

        # Méthode 1: Utiliser 'npx --no-install cspell --version' pour vérifier si CSpell est déjà installé
        try:
            result = run_silent(
                ["npx", "--no-install", "cspell", "--version"],
                timeout=10,
            )

            if result.returncode == 0:
                logger.debug("CSpell already accessible via npx")
                # CSpell est déjà accessible, pas besoin de modifier le PATH
                return True
        except Exception as e:
            logger.debug(f"npx check failed: {e}")

        # Méthode 2: Vérifier dans npm list globalement installé
        try:
            result = run_silent(
                [npm_path, "config", "get", "prefix"],
                timeout=5,
            )

            if result.returncode == 0 and result.stdout.strip():
                npm_prefix = Path(result.stdout.strip())
                # Sur Windows, les binaires npm globaux sont dans prefix/bin ou prefix
                npm_bin_path = (
                    npm_prefix / "bin" if (npm_prefix / "bin").exists() else npm_prefix
                )
                logger.debug(f"Found npm global bin path: {npm_bin_path}")

                # Ajouter au PATH si CSpell y est présent
                return _add_npm_bin_to_path(npm_bin_path)

        except Exception as e:
            logger.debug(f"npm list check failed: {e}")

        # Méthode 3: Utiliser 'npm root -g' pour trouver le dossier node_modules global
        try:
            result = run_silent(
                [npm_path, "root", "-g"],
                timeout=5,
            )

            if result.returncode == 0 and result.stdout.strip():
                global_modules = Path(result.stdout.strip())
                cspell_module = global_modules / "cspell"

                if cspell_module.exists():
                    logger.debug(f"Found CSpell module at: {cspell_module}")
                    # Dériver le chemin bin à partir du node_modules global
                    npm_bin_path = global_modules.parent / "bin"
                    return _add_npm_bin_to_path(npm_bin_path)

        except Exception as e:
            logger.debug(f"npm root check failed: {e}")

        logger.warning("Could not locate CSpell installation through npm methods")
        return False

    except Exception as e:
        # Wrap unexpected external exceptions
        raise CSpellError(
            operation="path_detection",
            reason=f"Error in CSpell PATH detection: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def _add_npm_bin_to_path(npm_bin_path: Path) -> bool:
    """
    Ajoute le dossier bin npm au PATH si CSpell y est trouvé.

    Args:
        npm_bin_path: Path to npm bin directory

    Returns:
        bool: True if CSpell was added to PATH, False otherwise

    Raises:
        CSpellError: If PATH modification fails unexpectedly
    """
    try:
        if not npm_bin_path.exists():
            logger.warning(f"npm bin path does not exist: {npm_bin_path}")
            return False

        # Sur Windows, npm crée des fichiers .cmd
        cspell_path = npm_bin_path / "cspell.cmd"
        if not cspell_path.exists():
            # Fallback pour autres OS
            cspell_path = npm_bin_path / "cspell"
            if not cspell_path.exists():
                logger.warning(f"CSpell binary not found in: {npm_bin_path}")
                return False

        logger.info(f"Found CSpell binary: {cspell_path}")

        # Ajouter au PATH utilisateur en utilisant la même logique que l'installer
        logger.debug(f"Adding to PATH: {npm_bin_path}")
        success = _add_directory_to_user_path(str(npm_bin_path))

        if success:
            logger.debug(
                f"Successfully added CSpell directory to user PATH: {npm_bin_path}"
            )
            return True
        else:
            logger.warning(f"Failed to add CSpell directory to PATH: {npm_bin_path}")
            return False

    except Exception as e:
        # Wrap unexpected external exceptions
        raise CSpellError(
            operation="path_addition",
            reason=f"Error adding npm bin to PATH: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def _add_directory_to_user_path(directory_path: str) -> bool:
    """
    Ajoute un répertoire au PATH utilisateur.

    Args:
        directory_path: Directory path to add to PATH

    Returns:
        bool: True if directory was added to PATH, False otherwise

    Raises:
        CSpellError: If PATH modification fails unexpectedly
    """
    try:
        if platform.system() == "Windows":
            # Méthode Windows : modifier le registre utilisateur
            result = run_silent(
                ["reg", "query", "HKCU\\Environment", "/v", "PATH"],
            )

            if result.returncode == 0:
                current_user_path = extract_path_from_reg_output(result.stdout)
                if not current_user_path:
                    current_user_path = ""

                # Vérifier si déjà présent
                if directory_path in current_user_path:
                    logger.debug("Directory already in user PATH")
                    return True

                # Ajouter le nouveau chemin
                new_user_path = (
                    f"{current_user_path};{directory_path}"
                    if current_user_path
                    else directory_path
                )
                new_user_path = deduplicate_path_entries(new_user_path)

                # Modifier le registre
                reg_result = run_silent(
                    [
                        "reg",
                        "add",
                        "HKCU\\Environment",
                        "/v",
                        "PATH",
                        "/t",
                        "REG_EXPAND_SZ",
                        "/d",
                        new_user_path,
                        "/f",
                    ],
                )

                if reg_result.returncode == 0:
                    # Mettre à jour la session courante aussi
                    current_session_path = os.environ.get("PATH", "")
                    if directory_path not in current_session_path:
                        os.environ["PATH"] = f"{current_session_path};{directory_path}"
                    return True

            return False

        else:
            # Méthode Unix : ajouter au shell profile
            shell_profiles = ["~/.bashrc", "~/.zshrc", "~/.profile"]

            for profile_file in shell_profiles:
                profile_path = Path(profile_file).expanduser()
                if profile_path.exists():
                    content = profile_path.read_text()
                    export_line = f'export PATH="$PATH:{directory_path}"'

                    if directory_path not in content:
                        # Ajouter la ligne d'export
                        profile_path.write_text(content + f"\n{export_line}\n")

                    # Mettre à jour la session courante
                    current_path = os.environ.get("PATH", "")
                    if directory_path not in current_path:
                        os.environ["PATH"] = f"{current_path}:{directory_path}"
                    return True

            return False

    except Exception as e:
        # Wrap unexpected external exceptions
        raise CSpellError(
            operation="path_modification",
            reason=f"Error adding directory to PATH: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


# ///////////////////////////////////////////////////////////////
# PROJECT CONFIGURATION UTILITIES
# ///////////////////////////////////////////////////////////////


def setup_project_cspell(
    project_path: Path, project_type: str, project_name: str
) -> bool:
    """
    Configure CSpell for a specific project.

    Args:
        project_path: Path to the project directory
        project_type: Type of project (python, javascript)
        project_name: Name of the project

    Returns:
        bool: True if configuration was successful, False otherwise

    Raises:
        SpellUtilityError: If project setup fails
        CSpellError: If CSpell configuration fails
    """
    try:
        # Input validation
        if not project_path:
            raise SpellUtilityError(
                message="Project path cannot be empty",
                details="Invalid project path provided for CSpell setup",
            )
        if not project_type:
            raise SpellUtilityError(
                message="Project type cannot be empty",
                details="Invalid project type provided for CSpell setup",
            )
        if not project_name:
            raise SpellUtilityError(
                message="Project name cannot be empty",
                details="Invalid project name provided for CSpell setup",
            )

        devtools_path = Path.home() / ".womm"

        if project_type == "python":
            template_path = (
                devtools_path
                / "languages"
                / "python"
                / "templates"
                / "cspell.json.template"
            )
        elif project_type == "javascript":
            template_path = (
                devtools_path
                / "languages"
                / "javascript"
                / "templates"
                / "cspell.json.template"
            )
        else:
            raise SpellUtilityError(
                message=f"Project type not supported: {project_type}",
                details="Only 'python' and 'javascript' project types are supported",
            )

        if not template_path.exists():
            raise CSpellError(
                operation="template_loading",
                reason=f"Template not found: {template_path}",
                details="CSpell template file is missing from devtools installation",
            )

        # Lire le template
        try:
            template_content = template_path.read_text(encoding="utf-8")
        except (PermissionError, OSError) as e:
            raise CSpellError(
                operation="template_reading",
                reason=f"Failed to read template file: {e}",
                details=f"Cannot access template file: {template_path}",
            ) from e
        except UnicodeDecodeError as e:
            raise CSpellError(
                operation="template_reading",
                reason=f"Failed to decode template file: {e}",
                details=f"Template file encoding issue: {template_path}",
            ) from e

        # Replace placeholders
        config_content = template_content.replace("{{PROJECT_NAME}}", project_name)

        # Write configuration
        config_file = project_path / "cspell.json"
        try:
            config_file.write_text(config_content, encoding="utf-8")
        except (PermissionError, OSError) as e:
            raise CSpellError(
                operation="config_writing",
                reason=f"Failed to write configuration file: {e}",
                details=f"Cannot write to project directory: {project_path}",
            ) from e

        logger.info(f"CSpell configuration created: {config_file}")
        return True

    except (SpellUtilityError, CSpellError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise SpellUtilityError(
            message=f"Project CSpell setup failed: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def detect_project_type(project_path: Path) -> str | None:
    """
    Detect project type.

    Args:
        project_path: Path to the project directory

    Returns:
        Optional[str]: Project type ('python', 'javascript') or None if not detected

    Raises:
        SpellUtilityError: If project detection fails unexpectedly
    """
    try:
        # Input validation
        if not project_path:
            raise SpellUtilityError(
                message="Project path cannot be empty",
                details="Invalid project path provided for type detection",
            )

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

    except SpellUtilityError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise SpellUtilityError(
            message=f"Project type detection failed: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


# ///////////////////////////////////////////////////////////////
# SPELL CHECKING UTILITIES
# ///////////////////////////////////////////////////////////////


def run_spellcheck(path: Path) -> dict:
    """
    Run spell check and return detailed results.

    Args:
        path: Path to check for spelling errors

    Returns:
        dict: Spell check results with issues and summary

    Raises:
        CSpellError: If spell checking fails
        SpellUtilityError: If spell check setup fails
    """
    try:
        # Input validation
        if not path:
            raise SpellUtilityError(
                message="Path cannot be empty",
                details="Invalid path provided for spell checking",
            )

        if not check_cspell_installed():
            logger.error("CSpell not installed - use: spellcheck --install")
            return {
                "success": False,
                "error": "CSpell not installed",
                "issues": [],
                "summary": {"files_checked": 0, "issues_found": 0},
            }

        # Utiliser le CLI manager standard
        try:
            from ..cli_utils import run_command
        except ImportError as e:
            raise SpellUtilityError(
                message="Failed to import CLI utilities",
                details=f"Cannot import run_command: {e}",
            ) from e

        # Vérifier si cspell est directement disponible dans le PATH
        cspell_path = shutil.which("cspell")
        cspell_direct_available = cspell_path is not None

        # Choisir la commande appropriée
        if cspell_direct_available:
            # Utiliser le chemin complet pour éviter les problèmes Windows
            cmd = [str(cspell_path), "lint", str(path)]
            cmd_description = f"Spell check - {path.name}"
        else:
            cmd = ["npx", "cspell", "lint", str(path)]
            cmd_description = f"Spell check - {path.name} (via npx)"

        cmd.extend(["--no-progress", "--show-context"])
        logger.debug(f"Checking: {path}")
        interactive_mode = False

        # Exécution avec shell=True pour Windows (nécessaire pour les commandes .cmd/.bat)
        try:
            result = run_command(cmd, cmd_description, shell=True)  # noqa: S604
        except Exception as e:
            raise CSpellError(
                operation="execution",
                reason=f"Failed to execute CSpell command: {e}",
                details=f"Command: {' '.join(cmd)}",
            ) from e

        logger.debug(
            f"CSpell command result: success={result.success}, returncode={result.returncode}"
        )
        logger.debug(f"CSpell stdout: {result.stdout}")
        logger.debug(f"CSpell stderr: {result.stderr}")

        # Analyser les résultats
        issues = []
        summary = {"files_checked": 0, "issues_found": 0}

        if interactive_mode:
            # En mode interactif, on ne parse pas la sortie car elle est gérée par CSpell
            # On considère que l'opération a réussi si CSpell s'est terminé normalement
            summary = {"files_checked": 1, "issues_found": 0}  # Valeur par défaut
        elif result.stdout:
            # Parser la sortie de CSpell pour extraire les erreurs (mode normal)
            try:
                lines = result.stdout.strip().split("\n")
                for line in lines:
                    if ":" in line and (
                        "Unknown word" in line or "Spelling error" in line
                    ):
                        # Format: file:line:col - Error message -- Context
                        parts = line.split(":", 3)
                        if len(parts) >= 4:
                            file_path = parts[0]
                            try:
                                line_num = int(parts[1])
                                col_num = int(parts[2])
                            except ValueError:
                                line_num = 0
                                col_num = 0

                            error_info = parts[3].strip()
                            # Extraire le mot et le contexte
                            if "--" in error_info:
                                error_parts = error_info.split("--", 1)
                                word_info = error_parts[0].strip()
                                context = (
                                    error_parts[1].strip()
                                    if len(error_parts) > 1
                                    else ""
                                )
                            else:
                                word_info = error_info
                                context = ""

                            # Extraire le mot problématique
                            word = ""
                            if "(" in word_info and ")" in word_info:
                                word = word_info.split("(")[1].split(")")[0]
                            elif "Unknown word" in word_info:
                                word = word_info.replace("Unknown word", "").strip()

                            issues.append(
                                {
                                    "file": file_path,
                                    "line": line_num,
                                    "column": col_num,
                                    "word": word,
                                    "message": word_info,
                                    "context": context,
                                }
                            )

                # Compter les fichiers et erreurs
                files_checked = len({issue["file"] for issue in issues})
                summary = {"files_checked": files_checked, "issues_found": len(issues)}
            except Exception as e:
                logger.warning(f"Failed to parse CSpell output: {e}")
                # Continue with empty issues list

        # CSpell retourne code 1 quand des erreurs sont trouvées, ce qui est normal
        success = result.success or result.returncode == 1

        return {
            "success": success,
            "issues": issues,
            "summary": summary,
            "raw_output": result.stdout,
            "raw_stderr": result.stderr,
        }

    except (CSpellError, SpellUtilityError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise SpellUtilityError(
            message=f"Spell checking failed: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


# ///////////////////////////////////////////////////////////////
# CONFIGURATION MANAGEMENT UTILITIES
# ///////////////////////////////////////////////////////////////


def add_words_to_config(project_path: Path, words: list[str]) -> bool:
    """
    Add words to CSpell configuration.

    Args:
        project_path: Path to the project directory
        words: List of words to add to configuration

    Returns:
        bool: True if words were added successfully, False otherwise

    Raises:
        DictionaryError: If configuration modification fails
        SpellUtilityError: If configuration setup fails
    """
    try:
        # Input validation
        if not project_path:
            raise SpellUtilityError(
                message="Project path cannot be empty",
                details="Invalid project path provided for word addition",
            )
        if not words:
            raise SpellUtilityError(
                message="Words list cannot be empty",
                details="Invalid words list provided for configuration",
            )

        config_path = project_path / "cspell.json"

        if not config_path.exists():
            raise DictionaryError(
                operation="config_access",
                dictionary_path=str(config_path),
                reason="CSpell configuration file does not exist",
                details="Run setup_project_cspell first to create configuration",
            )

        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except (PermissionError, OSError) as e:
            raise DictionaryError(
                operation="config_reading",
                dictionary_path=str(config_path),
                reason=f"Failed to read configuration file: {e}",
                details=f"Cannot access configuration file: {config_path}",
            ) from e
        except json.JSONDecodeError as e:
            raise DictionaryError(
                operation="config_parsing",
                dictionary_path=str(config_path),
                reason=f"Failed to parse configuration file: {e}",
                details=f"Invalid JSON in configuration file: {config_path}",
            ) from e

        if "words" not in config:
            config["words"] = []

        # Add new words
        added_count = 0
        for word in words:
            if word not in config["words"]:
                config["words"].append(word)
                added_count += 1

        try:
            config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        except (PermissionError, OSError) as e:
            raise DictionaryError(
                operation="config_writing",
                dictionary_path=str(config_path),
                reason=f"Failed to write configuration file: {e}",
                details=f"Cannot write to configuration file: {config_path}",
            ) from e

        logger.info(f"Added {added_count} words to CSpell configuration")
        return True

    except (DictionaryError, SpellUtilityError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise SpellUtilityError(
            message=f"Failed to add words to configuration: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def get_project_status(project_path: Path) -> dict:
    """
    Get detailed status of CSpell project configuration.

    Args:
        project_path: Path to the project directory

    Returns:
        dict: Project status information

    Raises:
        SpellUtilityError: If status retrieval fails unexpectedly
    """
    try:
        # Input validation
        if not project_path:
            raise SpellUtilityError(
                message="Project path cannot be empty",
                details="Invalid project path provided for status check",
            )

        status = {
            "cspell_installed": check_cspell_installed(),
            "config_exists": False,
            "config_path": None,
            "project_type": None,
            "words_count": 0,
            "dictionaries": [],
            "last_check": None,
            "issues_count": 0,
        }

        # Check if CSpell config exists
        config_file = project_path / "cspell.json"
        if config_file.exists():
            status["config_exists"] = True
            status["config_path"] = str(config_file)

            try:
                config_data = json.loads(config_file.read_text(encoding="utf-8"))
                status["words_count"] = len(config_data.get("words", []))
                status["dictionaries"] = config_data.get("dictionaries", [])
            except Exception as e:
                logger.debug(f"Failed to read CSpell config: {e}")
                # Don't fail the entire status check for config reading issues

        # Detect project type
        status["project_type"] = detect_project_type(project_path)

        return status

    except SpellUtilityError:
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise SpellUtilityError(
            message=f"Failed to get project status: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e


def add_words_from_file(project_path: Path, file_path: Path) -> bool:
    """
    Add words from a file to CSpell configuration.

    Args:
        project_path: Path to the project directory
        file_path: Path to the file containing words

    Returns:
        bool: True if words were added successfully, False otherwise

    Raises:
        DictionaryError: If file reading or word addition fails
        SpellUtilityError: If file processing fails
    """
    try:
        # Input validation
        if not project_path:
            raise SpellUtilityError(
                message="Project path cannot be empty",
                details="Invalid project path provided for word addition",
            )
        if not file_path:
            raise SpellUtilityError(
                message="File path cannot be empty",
                details="Invalid file path provided for word reading",
            )

        if not file_path.exists():
            raise DictionaryError(
                operation="file_access",
                dictionary_path=str(file_path),
                reason="Word file does not exist",
                details=f"Cannot access word file: {file_path}",
            )

        try:
            words = []
            with open(file_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        words.extend(line.split())

            if not words:
                logger.warning("No words found in file")
                return False

            return add_words_to_config(project_path, words)

        except (PermissionError, OSError) as e:
            raise DictionaryError(
                operation="file_reading",
                dictionary_path=str(file_path),
                reason=f"Failed to read word file: {e}",
                details=f"Cannot access word file: {file_path}",
            ) from e
        except UnicodeDecodeError as e:
            raise DictionaryError(
                operation="file_reading",
                dictionary_path=str(file_path),
                reason=f"Failed to decode word file: {e}",
                details=f"Word file encoding issue: {file_path}",
            ) from e

    except (DictionaryError, SpellUtilityError):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        # Wrap unexpected external exceptions
        raise SpellUtilityError(
            message=f"Failed to add words from file: {e}",
            details=f"Exception type: {type(e).__name__}",
        ) from e
