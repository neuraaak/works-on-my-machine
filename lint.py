#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de linting pour le projet works-on-my-machine.

Ce script automatise les vérifications de qualité du code :
- flake8 pour la vérification de style
- black pour le formatage
- isort pour l'organisation des imports

Adapté du script original dans languages/python/scripts/lint.py
"""

import argparse
import sys
from pathlib import Path

# Importer le nouveau gestionnaire CLI
from shared.cli_manager import run_command_legacy as run_command


def is_security_excluded(path):
    """Vérifie si un fichier ou dossier est exclu pour sécurité."""
    import fnmatch

    security_patterns = [
        ".env*",
        ".secret*",
        "*password*",
        "*secret*",
        "*.key",
        "*.pem",
        "*.crt",
        "credentials",
        "keys",
    ]

    path_str = str(path).lower()
    name = path.name.lower()

    for pattern in security_patterns:
        if fnmatch.fnmatch(name, pattern) or pattern in path_str:
            return True
    return False


def detect_project_dirs(base_path=None):
    """Détecte les dossiers Python du projet works-on-my-machine."""
    current_dir = Path(base_path) if base_path else Path.cwd()
    target_dirs = []

    # Dossiers spécifiques au projet works-on-my-machine
    project_dirs = ["shared", "languages"]

    for dir_name in project_dirs:
        dir_path = current_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            # Vérifier s'il contient des fichiers Python (non-sensibles)
            has_python_files = False
            try:
                for py_file in dir_path.glob("**/*.py"):
                    if not is_security_excluded(py_file):
                        has_python_files = True
                        break
                if has_python_files:
                    target_dirs.append(str(dir_path))
            except OSError:
                # Ignorer les erreurs d'accès aux fichiers (inclut PermissionError)
                pass

    # Ajouter les fichiers Python à la racine (init.py, etc.)
    root_python_files = []
    try:
        for py_file in current_dir.glob("*.py"):
            if not is_security_excluded(py_file):
                root_python_files.append(str(py_file))
    except OSError:
        pass

    if root_python_files:
        target_dirs.extend(root_python_files)

    return target_dirs


def main(target_path=None):
    """Fonction principale du script de linting."""
    target_dir = Path(target_path) if target_path else Path.cwd()

    print("🎨 works-on-my-machine - Script de Linting")
    print("=" * 50)
    print(f"📂 Répertoire cible: {target_dir}")

    # Vérifier que les outils sont installés
    tools = ["flake8", "black", "isort"]
    missing_tools = []

    from shared.cli_manager import run_silent

    for tool in tools:
        try:
            result = run_silent([tool, "--version"])
            if not result.success:
                raise Exception(f"Tool {tool} not available")
        except Exception:
            missing_tools.append(tool)

    if missing_tools:
        print(f"❌ Outils manquants: {', '.join(missing_tools)}")
        print("Installez-les avec: pip install -e '.[dev]'")
        return 1

    # Détecter automatiquement les dossiers à analyser
    target_dirs = detect_project_dirs(target_dir)
    if not target_dirs:
        print("❌ Aucun dossier Python trouvé")
        return 1

    print(f"📁 Analyse: {', '.join(target_dirs)}")

    success = True

    # 1. Vérifier le style avec flake8
    flake8_success = run_command(
        ["flake8"] + target_dirs + ["--count", "--statistics"],
        "Vérification du style (flake8)",
        cwd=target_dir,
    )
    success = success and flake8_success

    # 2. Vérifier le formatage avec black
    black_success = run_command(
        ["black", "--check", "--diff"] + target_dirs,
        "Vérification du formatage (black)",
        cwd=target_dir,
    )
    success = success and black_success

    # 3. Vérifier l'organisation des imports avec isort
    isort_success = run_command(
        ["isort", "--check-only", "--diff"] + target_dirs,
        "Vérification des imports (isort)",
        cwd=target_dir,
    )
    success = success and isort_success

    # Résumé
    print("\n" + "=" * 50)
    if success:
        print("🎉 Toutes les vérifications ont réussi !")
        print("✅ Le code respecte les standards de qualité.")
        return 0
    else:
        print("⚠️  Certaines vérifications ont échoué.")
        print("💡 Utilisez les commandes suivantes pour corriger :")
        print(f"   cd {target_dir}")
        print(f"   black {' '.join(target_dirs)}")
        print(f"   isort {' '.join(target_dirs)}")
        print(f"   flake8 {' '.join(target_dirs)}")
        return 1


def fix_whitespace_issues(target_path=None):
    """Corrige les problèmes d'espaces (W293, W291, W292)."""
    target_dir = Path(target_path) if target_path else Path.cwd()
    fixed_files = 0

    print("🧹 Correction des espaces en trop...")

    for py_file in target_dir.rglob("*.py"):
        if is_security_excluded(py_file):
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            modified = False
            new_lines = []

            for line in lines:
                # Supprimer les espaces en fin de ligne (W291)
                new_line = (
                    line.rstrip() + "\n" if line.endswith("\n") else line.rstrip()
                )
                if new_line != line:
                    modified = True
                new_lines.append(new_line)

            # Assurer une ligne vide en fin de fichier (W292)
            if new_lines and not new_lines[-1].endswith("\n"):
                new_lines[-1] += "\n"
                modified = True

            if modified:
                with open(py_file, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                fixed_files += 1
                print(f"  ✅ {py_file}")

        except Exception as e:
            print(f"  ❌ Erreur avec {py_file}: {e}")

    if fixed_files > 0:
        print(f"🎉 {fixed_files} fichiers corrigés pour les espaces")
    else:
        print("✅ Aucun problème d'espaces trouvé")

    return fixed_files


def fix_code(target_path=None):
    """Corrige automatiquement le code."""
    target_dir = Path(target_path) if target_path else Path.cwd()

    print("🔧 works-on-my-machine - Correction automatique du code")
    print("=" * 50)
    print(f"📂 Répertoire cible: {target_dir}")

    # Détecter les dossiers
    target_dirs = detect_project_dirs(target_dir)
    if not target_dirs:
        print("❌ Aucun dossier Python trouvé")
        return 1

    print(f"📁 Formatage: {', '.join(target_dirs)}")

    success = True

    # 0. Corriger les problèmes d'espaces
    fix_whitespace_issues(target_dir)

    # 1. Formater avec black
    black_success = run_command(
        ["black"] + target_dirs, "Formatage automatique (black)", cwd=target_dir
    )
    success = success and black_success

    # 2. Organiser les imports avec isort
    isort_success = run_command(
        ["isort"] + target_dirs, "Organisation des imports (isort)", cwd=target_dir
    )
    success = success and isort_success

    # Résumé
    print("\n" + "=" * 50)
    if success:
        print("🎉 Corrections automatiques terminées !")
        print("✅ Le code a été formaté et organisé.")
        return 0
    else:
        print("⚠️  Certaines corrections ont échoué.")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script de linting pour works-on-my-machine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Analyser le projet works-on-my-machine
  python lint.py

  # Analyser un répertoire spécifique
  python lint.py /chemin/vers/projet

  # Corriger automatiquement le code
  python lint.py --fix

  # Corriger un répertoire spécifique
  python lint.py /chemin/vers/projet --fix
        """,
    )

    parser.add_argument(
        "path",
        nargs="?",
        help="Chemin du projet à analyser (défaut: répertoire courant)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Corriger automatiquement le code au lieu de juste l'analyser",
    )

    args = parser.parse_args()

    if args.fix:
        sys.exit(fix_code(args.path))
    else:
        sys.exit(main(args.path))
