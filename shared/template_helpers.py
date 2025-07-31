#!/usr/bin/env python3
"""
Template Helpers - Utilitaires pour la génération de templates cross-platform.
Génère des templates cross-platform.
Valide les placeholders dans un template.
"""

import os
import platform
import re
from pathlib import Path
from typing import Any, Dict, Optional


def get_platform_info() -> Dict[str, str]:
    """Retourne les informations de plateforme."""
    system = platform.system()
    return {
        "system": system,
        "system_lower": system.lower(),
        "is_windows": system == "Windows",
        "is_linux": system == "Linux",
        "is_macos": system == "Darwin",
        "path_separator": os.sep,
        "line_ending": "\r\n" if system == "Windows" else "\n",
    }


def get_python_paths() -> Dict[str, str]:
    """Retourne les chemins Python selon l'OS."""
    platform_info = get_platform_info()

    if platform_info["is_windows"]:
        return {
            "venv_python": "./venv/Scripts/python.exe",
            "venv_activate": "./venv/Scripts/activate.bat",
            "venv_pip": "./venv/Scripts/pip.exe",
            "python_executable": "python.exe",
        }
    else:  # Linux/macOS
        return {
            "venv_python": "./venv/bin/python",
            "venv_activate": "source ./venv/bin/activate",
            "venv_pip": "./venv/bin/pip",
            "python_executable": "python3",
        }


def get_node_paths() -> Dict[str, str]:
    """Retourne les chemins Node.js selon l'OS."""
    platform_info = get_platform_info()

    if platform_info["is_windows"]:
        return {
            "npm_executable": "npm.cmd",
            "node_executable": "node.exe",
            "npx_executable": "npx.cmd",
        }
    else:  # Linux/macOS
        return {
            "npm_executable": "npm",
            "node_executable": "node",
            "npx_executable": "npx",
        }


def get_shell_commands() -> Dict[str, str]:
    """Retourne les commandes shell selon l'OS."""
    platform_info = get_platform_info()

    if platform_info["is_windows"]:
        return {
            "shell": "cmd",
            "shell_extension": ".bat",
            "remove_dir": "rmdir /s /q",
            "copy_file": "copy",
            "move_file": "move",
            "make_executable": "rem",  # Pas nécessaire sur Windows
            "which": "where",
        }
    else:  # Linux/macOS
        return {
            "shell": "bash",
            "shell_extension": ".sh",
            "remove_dir": "rm -rf",
            "copy_file": "cp",
            "move_file": "mv",
            "make_executable": "chmod +x",
            "which": "which",
        }


def replace_platform_placeholders(text: str, **extra_vars) -> str:
    r"""
    Replace platform-specific placeholders in a text.

    Placeholders supportés:
    - {{PYTHON_PATH}} - Chemin vers l'exécutable Python
    - {{VENV_ACTIVATE}} - Commande d'activation de l'environnement virtuel
    - {{SHELL_EXT}} - Extension des scripts shell (.bat ou .sh)
    - {{PATH_SEP}} - Séparateur de chemin (/ ou \\)
    - {{LINE_ENDING}} - Fin de ligne (\\r\\n ou \\n)
    """
    platform_info = get_platform_info()
    python_paths = get_python_paths()
    node_paths = get_node_paths()
    shell_commands = get_shell_commands()

    # Dictionnaire de remplacement
    replacements = {
        # Informations de plateforme
        "PLATFORM_SYSTEM": platform_info["system"],
        "PLATFORM_SYSTEM_LOWER": platform_info["system_lower"],
        "IS_WINDOWS": str(platform_info["is_windows"]).lower(),
        "IS_LINUX": str(platform_info["is_linux"]).lower(),
        "IS_MACOS": str(platform_info["is_macos"]).lower(),
        "PATH_SEP": platform_info["path_separator"],
        "LINE_ENDING": platform_info["line_ending"],
        # Chemins Python
        "PYTHON_PATH": python_paths["venv_python"],
        "VENV_ACTIVATE": python_paths["venv_activate"],
        "VENV_PIP": python_paths["venv_pip"],
        "PYTHON_EXECUTABLE": python_paths["python_executable"],
        # Chemins Node.js
        "NPM_EXECUTABLE": node_paths["npm_executable"],
        "NODE_EXECUTABLE": node_paths["node_executable"],
        "NPX_EXECUTABLE": node_paths["npx_executable"],
        # Commandes shell
        "SHELL": shell_commands["shell"],
        "SHELL_EXT": shell_commands["shell_extension"],
        "REMOVE_DIR": shell_commands["remove_dir"],
        "COPY_FILE": shell_commands["copy_file"],
        "MOVE_FILE": shell_commands["move_file"],
        "MAKE_EXECUTABLE": shell_commands["make_executable"],
        "WHICH": shell_commands["which"],
        # Variables supplémentaires
        **extra_vars,
    }

    # Remplacement des placeholders
    result = text
    for key, value in replacements.items():
        placeholder = f"{{{{{key}}}}}"
        result = result.replace(placeholder, str(value))

    return result


def generate_cross_platform_template(
    template_path: Path,
    output_path: Path,
    template_vars: Optional[Dict[str, str]] = None,
) -> None:
    """
    Génère un fichier à partir d'un template en remplaçant les placeholders.

    Args:
        template_path: Chemin vers le template à utiliser.
        output_path: Chemin vers le fichier de sortie.
        template_vars: Variables à remplacer dans le template.

    Returns:
        None
    """
    if template_vars is None:
        template_vars = {}

    # Lecture du template
    with open(template_path, "r", encoding="utf-8") as f:
        template_content = f.read()

    # Remplacement des placeholders
    result_content = replace_platform_placeholders(template_content, **template_vars)

    # Création du répertoire de sortie si nécessaire
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Écriture du fichier de sortie
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result_content)

    print(f"✅ Template généré : {output_path}")


def validate_template_placeholders(template_path: Path) -> Dict[str, Any]:
    """
    Validate placeholders in a template and return statistics.

    Args:
        template_path: Chemin vers le template à valider.

    Returns:
        Un dictionnaire contenant les statistiques de validation.
    """
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Recherche des placeholders
    placeholder_pattern = r"\{\{([A-Z_]+)\}\}"
    placeholders = re.findall(placeholder_pattern, content)

    # Placeholders supportés
    supported_placeholders = {
        "PLATFORM_SYSTEM",
        "PLATFORM_SYSTEM_LOWER",
        "IS_WINDOWS",
        "IS_LINUX",
        "IS_MACOS",
        "PATH_SEP",
        "LINE_ENDING",
        "PYTHON_PATH",
        "VENV_ACTIVATE",
        "VENV_PIP",
        "PYTHON_EXECUTABLE",
        "NPM_EXECUTABLE",
        "NODE_EXECUTABLE",
        "NPX_EXECUTABLE",
        "SHELL",
        "SHELL_EXT",
        "REMOVE_DIR",
        "COPY_FILE",
        "MOVE_FILE",
        "MAKE_EXECUTABLE",
        "WHICH",
        # Placeholders de projet standards
        "PROJECT_NAME",
        "PROJECT_DESCRIPTION",
        "AUTHOR_NAME",
        "AUTHOR_EMAIL",
        "PROJECT_URL",
        "PROJECT_REPOSITORY",
        "PROJECT_DOCS_URL",
        "PROJECT_KEYWORDS",
    }

    # Classification des placeholders
    found_placeholders = set(placeholders)
    supported_found = found_placeholders & supported_placeholders
    unsupported_found = found_placeholders - supported_placeholders

    return {
        "total_placeholders": len(found_placeholders),
        "supported_placeholders": list(supported_found),
        "unsupported_placeholders": list(unsupported_found),
        "is_valid": len(unsupported_found) == 0,
        "template_path": str(template_path),
    }


def main():
    """Point d'entrée principal pour les tests."""
    platform_info = get_platform_info()
    python_paths = get_python_paths()
    node_paths = get_node_paths()
    shell_commands = get_shell_commands()

    print("🌍 Informations de plateforme :")
    for key, value in platform_info.items():
        print(f"  {key}: {value}")

    print("\n🐍 Chemins Python :")
    for key, value in python_paths.items():
        print(f"  {key}: {value}")

    print("\n🟨 Chemins Node.js :")
    for key, value in node_paths.items():
        print(f"  {key}: {value}")

    print("\n💻 Commandes shell :")
    for key, value in shell_commands.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
