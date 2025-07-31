#!/usr/bin/env python3
"""
Configuration VSCode Cross-Platform.
Génère automatiquement les configurations VSCode adaptées à l'OS.
"""

import json
import platform
from pathlib import Path
from typing import Any, Dict, Optional


def get_python_interpreter_paths() -> Dict[str, str]:
    """Retourne les chemins d'interpréteur Python selon l'OS."""
    system = platform.system().lower()

    paths = {
        "windows": "./venv/Scripts/python.exe",
        "linux": "./venv/bin/python",
        "darwin": "./venv/bin/python",  # macOS
    }

    return paths.get(system, "./venv/bin/python")


def get_platform_specific_settings(language: str = "python") -> Dict[str, Any]:
    """Génère des paramètres VSCode spécifiques à la plateforme."""
    system = platform.system().lower()

    if language == "python":
        base_settings = {
            # Configuration de base (commune)
            "editor.formatOnSave": True,
            "editor.formatOnPaste": True,
            "editor.codeActionsOnSave": {"source.organizeImports": "explicit"},
            "editor.rulers": [88],
            "editor.tabSize": 4,
            "editor.insertSpaces": True,
            "files.trimTrailingWhitespace": True,
            "files.insertFinalNewline": True,
            "files.trimFinalNewlines": True,
            # Configuration Python
            "python.terminal.activateEnvironment": True,
            "python.linting.enabled": True,
            "python.linting.flake8Enabled": True,
            "python.linting.flake8Args": ["--config=.flake8"],
            "python.formatting.provider": "black",
            "python.formatting.blackArgs": [
                "--line-length=88",
                "--target-version=py39",
            ],
            "python.sortImports.args": ["--profile=black", "--line-length=88"],
            "[python]": {
                "editor.defaultFormatter": "ms-python.black-formatter",
                "editor.formatOnSave": True,
                "editor.codeActionsOnSave": {
                    "source.organizeImports": "explicit",
                },
            },
            "python.testing.pytestEnabled": True,
            "python.testing.pytestArgs": [
                "tests",
                "--tb=short",
                "--strict-markers",
            ],
            "python.testing.autoTestDiscoverOnSaveEnabled": True,
            "python.analysis.extraPaths": ["./src"],
            "python.analysis.autoSearchPaths": True,
            "python.analysis.typeCheckingMode": "basic",
            # Exclusions communes
            "files.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True,
                "**/.pytest_cache": True,
                "**/htmlcov": True,
                "**/.coverage": True,
                "**/build": True,
                "**/dist": True,
                "**/*.egg-info": True,
                "**/.mypy_cache": True,
                "**/.tox": True,
                "**/venv": True,
                "**/.venv": True,
                "**/.env*": True,
                "**/.secret*": True,
                "**/*password*": True,
                "**/*secret*": True,
                "**/*.key": True,
                "**/*.pem": True,
                "**/*.crt": True,
                "**/credentials": True,
            },
            "files.watcherExclude": {
                "**/.git/objects/**": True,
                "**/.git/subtree-cache/**": True,
                "**/venv/**": True,
                "**/.venv/**": True,
                "**/__pycache__/**": True,
                "**/.pytest_cache/**": True,
                "**/htmlcov/**": True,
                "**/.env*": True,
                "**/.secret*": True,
                "**/*password*": True,
                "**/*secret*": True,
                "**/*.key": True,
                "**/*.pem": True,
                "**/*.crt": True,
                "**/credentials/**": True,
            },
            "git.ignoreLimitWarning": True,
        }

        # Ajout du chemin d'interpréteur spécifique à l'OS
        python_path = get_python_interpreter_paths()
        base_settings["python.defaultInterpreterPath"] = python_path

        # Configuration environnement terminal spécifique à l'OS
        if system == "windows":
            base_settings["terminal.integrated.env.windows"] = {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        elif system == "darwin":  # macOS
            base_settings["terminal.integrated.env.osx"] = {
                "PYTHONPATH": "${workspaceFolder}/src"
            }
        else:  # Linux et autres Unix
            base_settings["terminal.integrated.env.linux"] = {
                "PYTHONPATH": "${workspaceFolder}/src"
            }

        return base_settings

    elif language == "javascript":
        return {
            "editor.formatOnSave": True,
            "editor.formatOnPaste": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": "explicit",
                "source.fixAll.eslint": "explicit",
            },
            "editor.rulers": [80],
            "editor.tabSize": 2,
            "editor.insertSpaces": True,
            "files.trimTrailingWhitespace": True,
            "files.insertFinalNewline": True,
            "files.trimFinalNewlines": True,
            # Configuration JavaScript/TypeScript
            "javascript.preferences.includePackageJsonAutoImports": "auto",
            "typescript.preferences.includePackageJsonAutoImports": "auto",
            "javascript.updateImportsOnFileMove.enabled": "always",
            "typescript.updateImportsOnFileMove.enabled": "always",
            # ESLint
            "eslint.enable": True,
            "eslint.format.enable": True,
            "eslint.lintTask.enable": True,
            # Prettier
            "[javascript]": {
                "editor.defaultFormatter": "esbenp.prettier-vscode",
                "editor.formatOnSave": True,
            },
            "[typescript]": {
                "editor.defaultFormatter": "esbenp.prettier-vscode",
                "editor.formatOnSave": True,
            },
            "[json]": {"editor.defaultFormatter": "esbenp.prettier-vscode"},
            # Exclusions
            "files.exclude": {
                "**/node_modules": True,
                "**/dist": True,
                "**/build": True,
                "**/.next": True,
                "**/coverage": True,
                "**/.nyc_output": True,
            },
            "files.watcherExclude": {
                "**/node_modules/**": True,
                "**/dist/**": True,
                "**/build/**": True,
                "**/.next/**": True,
            },
        }

    return {}


def generate_vscode_config(
    target_dir: Path, language: str = "python", project_name: Optional[str] = None
) -> None:
    """Génère la configuration VSCode pour un projet."""
    vscode_dir = target_dir / ".vscode"
    vscode_dir.mkdir(exist_ok=True)

    # Génération settings.json
    settings = get_platform_specific_settings(language)
    settings_file = vscode_dir / "settings.json"

    with open(settings_file, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

    print(f"✅ Configuration VSCode générée pour {language} dans {vscode_dir}")
    print(f"🖥️  Plateforme détectée : {platform.system()}")

    if language == "python":
        python_path = get_python_interpreter_paths()
        print(f"🐍 Chemin Python configuré : {python_path}")


def main():
    """Point d'entrée principal."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Génère une configuration VSCode cross-platform"
    )
    parser.add_argument(
        "--language",
        "-l",
        choices=["python", "javascript"],
        default="python",
        help="Langage cible (default: python)",
    )
    parser.add_argument(
        "--target",
        "-t",
        type=Path,
        default=Path.cwd(),
        help="Répertoire cible (default: répertoire courant)",
    )
    parser.add_argument("--project-name", "-n", help="Nom du projet")

    args = parser.parse_args()

    generate_vscode_config(
        target_dir=args.target,
        language=args.language,
        project_name=args.project_name,
    )


if __name__ == "__main__":
    main()
