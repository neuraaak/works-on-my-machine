#!/usr/bin/env python3
"""
CSpell Manager - Configuration and installation manager for CSpell.
Installs CSpell and its dictionaries globally.
Configures CSpell for a specific project.
Launches spell checking.
Detects project type.
"""

import logging
import shutil
import sys
from pathlib import Path
from typing import Optional


def check_cspell_installed() -> bool:
    """Check if CSpell is installed."""
    # Check via shutil.which (PATH)
    if shutil.which("cspell") is not None:
        return True

    # Check via npm (fallback)
    try:
        from womm.core.utils.cli_manager import run_silent

        result = run_silent(["npm", "list", "-g", "cspell"])
        return result.success and "cspell@" in result.stdout
    except Exception:
        return False


def install_cspell_global() -> bool:
    """Install CSpell and its dictionaries globally."""
    print("[INSTALL] Installing CSpell and dictionaries...")

    try:
        # Check that npm is available
        from womm.core.utils.cli_manager import check_tool_available

        if not check_tool_available("npm"):
            print("[ERROR] npm is not available. Please install Node.js first.")
            return False

        # CSpell installation
        from womm.core.utils.cli_manager import run_command

        result = run_command(["npm", "install", "-g", "cspell"], "CSpell installation")
        if not result.success:
            print(f"[ERROR] CSpell installation failed: {result.stderr}")
            print("[HINT] Try running with administrator privileges")
            return False
        print("[OK] CSpell installed")

        # Essential dictionaries
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

        print("[DICT] Installing dictionaries...")
        failed_dictionaries = []

        for dictionary in dictionaries:
            try:
                result = run_command(
                    ["npm", "install", "-g", dictionary],
                    f"Installing dictionary {dictionary}",
                )
                if result.success:
                    print(f"  [OK] {dictionary}")
                else:
                    print(
                        f"  [WARN] {dictionary} - installation error: {result.stderr}"
                    )
                    failed_dictionaries.append(dictionary)
            except Exception as e:
                print(f"  [WARN] {dictionary} - installation error: {e}")
                failed_dictionaries.append(dictionary)

        if failed_dictionaries:
            print(f"[WARN] {len(failed_dictionaries)} dictionaries failed to install")
            print(f"[WARN] Failed: {', '.join(failed_dictionaries)}")

        return True

    except Exception as e:
        print(f"[ERROR] Installation error: {e}")
        return False


def create_global_config() -> bool:
    """Copy global configuration to user location."""
    # Try several possible paths for womm
    possible_paths = [
        Path.home() / ".womm",
        Path(__file__).parent.parent,  # Relative path from this script
        Path.cwd(),  # Current directory
    ]

    devtools_path = None
    for path in possible_paths:
        config_source = path / "shared" / "configs" / "cspell.global.json"
        if config_source.exists():
            devtools_path = path
            break

    if devtools_path is None:
        print("[ERROR] Could not find womm installation")
        print("[HINT] Make sure you're running from the correct directory")
        return False

    global_config_source = devtools_path / "shared" / "configs" / "cspell.global.json"

    # Determine global config location according to OS
    import platform

    system = platform.system()

    if system == "Windows":
        config_dir = Path.home() / "AppData" / "Roaming" / "cspell"
    elif system == "Darwin":  # macOS
        config_dir = Path.home() / "Library" / "Preferences" / "cspell"
    else:  # Linux
        config_dir = Path.home() / ".config" / "cspell"

    try:
        config_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"[ERROR] Cannot create config directory {config_dir}: {e}")
        return False

    global_config_target = config_dir / "cspell.json"

    if global_config_source.exists():
        try:
            shutil.copy2(global_config_source, global_config_target)
            print(f"[OK] Global configuration installed: {global_config_target}")
            return True
        except Exception as e:
            print(f"[ERROR] Cannot copy configuration: {e}")
            return False
    else:
        print(f"[ERROR] Source configuration not found: {global_config_source}")
        return False


def setup_project_cspell(
    project_path: Path, project_type: str, project_name: str
) -> bool:
    """Configure CSpell for a specific project."""
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
        print(f"[ERROR] Project type not supported: {project_type}")
        return False

    if not template_path.exists():
        print(f"[ERROR] Template not found: {template_path}")
        return False

    # Lire le template
    template_content = template_path.read_text(encoding="utf-8")

    # Replace placeholders
    config_content = template_content.replace("{{PROJECT_NAME}}", project_name)

    # Write configuration
    config_file = project_path / "cspell.json"
    config_file.write_text(config_content, encoding="utf-8")

    print(f"[OK] CSpell configuration created: {config_file}")
    return True


def run_spellcheck(path: Path, fix_mode: bool = False) -> bool:
    """Run spell check."""
    if not check_cspell_installed():
        print("[ERROR] CSpell not installed - use: spellcheck --install")
        return False

    # Validation de sécurité préalable (sécurité toujours disponible)
    from womm.core.security.security_validator import security_validator

    use_security_validation = True

    # Utiliser le CLI manager standard avec validation de sécurité
    from womm.core.utils.cli_manager import run_command

    # Essayer d'abord avec cspell direct
    cmd = ["cspell", str(path)]

    if fix_mode:
        cmd.append("--interactive")
        print(f"[FIX] Interactive mode - Fixing: {path}")
    else:
        cmd.extend(["--no-progress", "--show-context"])
        print(f"[CHECK] Checking: {path}")

    # Valider la commande avant exécution si possible
    if use_security_validation:
        is_valid, error = security_validator.validate_command(cmd)
        if not is_valid:
            print(f"[SECURITY] Command validation failed: {error}")
            return False

    # Exécution avec shell=True pour Windows (nécessaire pour les commandes .cmd/.bat)
    result = run_command(cmd, f"Spell check - {path.name}", shell=True)  # noqa: S604
    if result.success:
        return True

    # Fallback npx conservé: utile si binaire cspell non dans PATH
    print("[FALLBACK] Trying with npx...")
    cmd = ["npx", "cspell", str(path)]
    if fix_mode:
        cmd.append("--interactive")
    else:
        cmd.extend(["--no-progress", "--show-context"])

    # Valider la commande npx
    if use_security_validation:
        is_valid, error = security_validator.validate_command(cmd)
        if not is_valid:
            print(f"[SECURITY] NPX command validation failed: {error}")
            return False

    result = run_command(  # noqa: S604
        cmd, f"Spell check - {path.name} (via npx)", shell=True
    )
    return result.success


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


def get_project_status(project_path: Path) -> dict:
    """Get detailed status of CSpell project configuration."""
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
            import json

            config_data = json.loads(config_file.read_text(encoding="utf-8"))
            status["words_count"] = len(config_data.get("words", []))
            status["dictionaries"] = config_data.get("dictionaries", [])
        except Exception as e:
            logging.debug(f"Failed to read CSpell config: {e}")

    # Detect project type
    status["project_type"] = detect_project_type(project_path)

    return status


def display_project_status(project_path: Path):
    """Display comprehensive project status."""
    status = get_project_status(project_path)

    print("\n" + "=" * 60)
    print("[STATUS] CSPELL PROJECT STATUS")
    print("=" * 60)

    # CSpell installation
    if status["cspell_installed"]:
        print("[OK] CSpell installed")
    else:
        print("[ERROR] CSpell not installed")
        print("   [TIP] Install with: womm spell install")

    # Configuration
    if status["config_exists"]:
        print(f"[OK] Configuration found: {status['config_path']}")
        print(f"   [WORDS] Custom words: {status['words_count']}")
        print(f"   [DICT] Dictionaries: {len(status['dictionaries'])}")
        if status["dictionaries"]:
            for dict_name in status["dictionaries"][:5]:  # Show first 5
                print(f"      - {dict_name}")
            if len(status["dictionaries"]) > 5:
                print(f"      ... and {len(status['dictionaries']) - 5} others")
    else:
        print("[ERROR] No CSpell configuration found")
        print("   [TIP] Configure with: womm spell setup <project_name>")

    # Project type
    if status["project_type"]:
        print(f"[DETECT] Project type detected: {status['project_type']}")
    else:
        print("[UNKNOWN] Project type not detected")

    # Quick check
    if status["cspell_installed"] and status["config_exists"]:
        print("\n[CHECK] Quick verification...")
        try:
            from womm.core.utils.cli_manager import run_command

            result = run_command(
                ["npx", "cspell", "--no-progress", str(project_path)],
                "Quick spell check",
            )
            if result.success:
                print("[OK] No spelling errors found")
            else:
                # Count issues from stderr
                lines = result.stderr.split("\n")
                issue_lines = [line for line in lines if "Unknown word" in line]
                print(f"[WARN] {len(issue_lines)} spelling errors found")
        except Exception as e:
            print(f"[ERROR] Error during verification: {e}")

    print("=" * 60)


def add_words_to_config(project_path: Path, words: list) -> bool:
    """Add words to CSpell configuration."""
    config_file = project_path / "cspell.json"

    if not config_file.exists():
        print("[ERROR] CSpell configuration not found")
        print(
            "[TIP] Create a configuration first with: womm spell setup <project_name>"
        )
        return False

    try:
        import json

        # Read current config
        config_data = json.loads(config_file.read_text(encoding="utf-8"))
        current_words = set(config_data.get("words", []))

        # Add new words
        new_words = []
        for word in words:
            word = word.strip()
            if word and word not in current_words:
                new_words.append(word)
                current_words.add(word)

        if not new_words:
            print("[INFO] All words are already in the configuration")
            return True

        # Update config
        config_data["words"] = sorted(current_words)

        # Write back
        config_file.write_text(
            json.dumps(config_data, indent=4, ensure_ascii=False), encoding="utf-8"
        )

        print(f"[OK] {len(new_words)} words added to configuration")
        if len(new_words) <= 10:
            for word in new_words:
                print(f"   + {word}")
        else:
            print(f"   + {', '.join(new_words[:5])}... and {len(new_words) - 5} others")

        return True

    except Exception as e:
        print(f"[ERROR] Error adding words: {e}")
        return False


def add_words_from_file(project_path: Path, file_path: Path) -> bool:
    """Add words from a file to CSpell configuration."""
    if not file_path.exists():
        print(f"[ERROR] File not found: {file_path}")
        return False

    try:
        words = []
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    words.extend(line.split())

        if not words:
            print("[WARN] No words found in file")
            return False

        return add_words_to_config(project_path, words)

    except Exception as e:
        print(f"[ERROR] Error reading file: {e}")
        return False


def add_words_interactive(project_path: Path) -> bool:
    """Interactive mode to add words."""
    print("[INTERACTIVE] Interactive word addition mode")
    print("[TIP] Type 'quit' to exit, 'check' to verify")

    words_to_add = []

    while True:
        try:
            word = input("Word to add: ").strip()

            if word.lower() == "quit":
                break
            elif word.lower() == "check":
                if words_to_add:
                    print(f"[PREVIEW] Words to add: {', '.join(words_to_add)}")
                else:
                    print("[INFO] No words to add")
                continue
            elif word:
                words_to_add.append(word)
                print(f"[ADDED] '{word}' added to list")
            else:
                print("[INFO] Empty word ignored")

        except KeyboardInterrupt:
            print("\n[INTERRUPT] Interrupted by user")
            break
        except EOFError:
            break

    if words_to_add:
        return add_words_to_config(project_path, words_to_add)
    else:
        print("[INFO] No words added")
        return True


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
    parser.add_argument("--check", metavar="PATH", help="Check spelling of file/folder")
    parser.add_argument(
        "--fix", metavar="PATH", help="Fix spelling in interactive mode"
    )
    parser.add_argument(
        "--type", choices=["python", "javascript"], help="Force project type"
    )
    parser.add_argument(
        "--status", action="store_true", help="Display status of current project"
    )
    parser.add_argument(
        "--add", nargs="*", metavar="WORDS", help="Add words to configuration"
    )
    parser.add_argument("--add-file", metavar="FILE", help="Add words from file")
    parser.add_argument(
        "--add-interactive", action="store_true", help="Interactive mode to add words"
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
            print("[ERROR] Project type not detected. Use --type")
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

    if args.status:
        display_project_status(Path.cwd())
        return

    if args.add:
        success = add_words_to_config(Path.cwd(), args.add)
        sys.exit(0 if success else 1)

    if args.add_file:
        success = add_words_from_file(Path.cwd(), Path(args.add_file))
        sys.exit(0 if success else 1)

    if args.add_interactive:
        success = add_words_interactive(Path.cwd())
        sys.exit(0 if success else 1)

    # Default mode: check current project
    project_path = Path.cwd()

    if not check_cspell_installed():
        print("[ERROR] CSpell not installed")
        print("[TIP] Install with: spellcheck --install")
        return

    # Look for existing CSpell config
    config_file = project_path / "cspell.json"
    if config_file.exists():
        print("[CONFIG] CSpell configuration found")
        run_spellcheck(project_path)
    else:
        print("[INFO] No CSpell configuration")
        print("[TIP] Configure with: spellcheck --setup-project PROJECT_NAME")


if __name__ == "__main__":
    main()
