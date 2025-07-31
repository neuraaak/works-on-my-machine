#!/usr/bin/env python3
"""
CSpell Manager - Gestionnaire de configuration et installation CSpell.
Installe CSpell et ses dictionnaires globalement.
Configure CSpell pour un projet spécifique.
Lance la vérification orthographique.
Détecte le type de projet.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


def check_cspell_installed() -> bool:
    """Check if CSpell is installed."""
    return shutil.which("cspell") is not None


def install_cspell_global() -> bool:
    """Install CSpell and its dictionaries globally."""
    print("📦 Installing CSpell and dictionaries...")

    try:
        # Installation CSpell
        from shared.cli_manager import run_command

        result = run_command(["npm", "install", "-g", "cspell"], "Installation CSpell")
        if not result.success:
            raise Exception("CSpell installation failed")
        print("✅ CSpell installed")

        # Dictionnaires essentiels
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

        print("📚 Installing dictionaries...")
        from shared.cli_manager import run_command

        for dictionary in dictionaries:
            try:
                result = run_command(
                    ["npm", "install", "-g", dictionary],
                    f"Installing dictionary {dictionary}",
                )
                if result.success:
                    print(f"  ✅ {dictionary}")
                else:
                    print(f"  ⚠️ {dictionary} - installation error")
            except Exception:
                print(f"  ⚠️ {dictionary} - installation error")

        return True

    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False


def create_global_config() -> bool:
    """Copy global configuration to user location."""
    devtools_path = Path.home() / ".dev-tools"
    global_config_source = devtools_path / "shared" / "configs" / "cspell.global.json"

    # Déterminer l'emplacement de la config globale selon l'OS
    import platform

    system = platform.system()

    if system == "Windows":
        config_dir = Path.home() / "AppData" / "Roaming" / "cspell"
    elif system == "Darwin":  # macOS
        config_dir = Path.home() / "Library" / "Preferences" / "cspell"
    else:  # Linux
        config_dir = Path.home() / ".config" / "cspell"

    config_dir.mkdir(parents=True, exist_ok=True)
    global_config_target = config_dir / "cspell.json"

    if global_config_source.exists():
        shutil.copy2(global_config_source, global_config_target)
        print(f"✅ Global configuration installed: {global_config_target}")
        return True
    else:
        print(f"❌ Source configuration not found: {global_config_source}")
        return False


def setup_project_cspell(
    project_path: Path, project_type: str, project_name: str
) -> bool:
    """Configure CSpell for a specific project."""
    devtools_path = Path.home() / ".dev-tools"

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
        print(f"❌ Project type not supported: {project_type}")
        return False

    if not template_path.exists():
        print(f"❌ Template not found: {template_path}")
        return False

    # Lire le template
    template_content = template_path.read_text(encoding="utf-8")

    # Remplacer les placeholders
    config_content = template_content.replace("{{PROJECT_NAME}}", project_name)

    # Écrire la configuration
    config_file = project_path / "cspell.json"
    config_file.write_text(config_content, encoding="utf-8")

    print(f"✅ CSpell configuration created: {config_file}")
    return True


def run_spellcheck(path: Path, fix_mode: bool = False) -> bool:
    """Run spell check."""
    if not check_cspell_installed():
        print("❌ CSpell not installed - use: spellcheck --install")
        return False

    cmd = ["cspell", str(path)]

    if fix_mode:
        cmd.append("--interactive")
        print(f"🔧 Interactive mode - Fixing: {path}")
    else:
        cmd.extend(["--no-progress", "--show-context"])
        print(f"🔍 Checking: {path}")

    from shared.cli_manager import run_command

    try:
        result = run_command(cmd, f"Spell check - {path.name}")
        return result.success
    except Exception as e:
        print(f"❌ Check error: {e}")
        return False


def detect_project_type(project_path: Path) -> Optional[str]:
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


def main():
    """Launch the main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="CSpell manager for dev-tools")
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install CSpell and dictionaries globally",
    )
    parser.add_argument(
        "--setup-global", action="store_true", help="Configure CSpell globally"
    )
    parser.add_argument(
        "--setup-project",
        metavar="PROJECT_NAME",
        help="Configure CSpell for current project",
    )
    parser.add_argument(
        "--check", metavar="PATH", help="Check spelling of file/folder"
    )
    parser.add_argument(
        "--fix", metavar="PATH", help="Fix spelling in interactive mode"
    )
    parser.add_argument(
        "--type", choices=["python", "javascript"], help="Force project type"
    )

    args = parser.parse_args()

    if args.install:
        success = install_cspell_global()
        if success:
            create_global_config()
        return

    if args.setup_global:
        create_global_config()
        return

    if args.setup_project:
        project_path = Path.cwd()
        project_type = args.type or detect_project_type(project_path)

        if not project_type:
            print("❌ Project type not detected. Use --type")
            return

        setup_project_cspell(project_path, project_type, args.setup_project)
        return

    if args.check:
        check_path = Path(args.check)
        run_spellcheck(check_path, fix_mode=False)
        return

    if args.fix:
        fix_path = Path(args.fix)
        run_spellcheck(fix_path, fix_mode=True)
        return

    # Default mode: check current project
    project_path = Path.cwd()

    if not check_cspell_installed():
        print("❌ CSpell not installed")
        print("💡 Install with: spellcheck --install")
        return

    # Look for existing CSpell config
    config_file = project_path / "cspell.json"
    if config_file.exists():
        print("📝 CSpell configuration found")
        run_spellcheck(project_path)
    else:
        print("❓ No CSpell configuration")
        print("💡 Configure with: spellcheck --setup-project PROJECT_NAME")


if __name__ == "__main__":
    main()
