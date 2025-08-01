#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy development tools to a global directory.

This script copies the Works On My Machine tools to a global location
and optionally creates global commands accessible from anywhere.
"""

import argparse
import os
import platform
import shutil
import sys
from pathlib import Path

# Importer le gestionnaire CLI
from shared.cli_manager import run_command, run_silent


def get_default_target():
    """Get default target directory based on platform."""
    if platform.system() == "Windows":
        return Path.home() / ".womm"
    else:
        return Path.home() / ".womm"


def deploy_tools(target_dir: Path, install_global: bool = False):
    """Deploy tools to target directory.

    Args:
        target_dir: Target directory for deployment.
        install_global: Whether to install global commands.
    """
    print(f"📦 Deploying Works On My Machine to: {target_dir}")

    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy all files
    source_dir = Path(__file__).parent.parent
    print(f"📁 Copying from: {source_dir}")

    # Remove existing files
    if target_dir.exists():
        for item in target_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

    # Copy files
    for item in source_dir.iterdir():
        if item.name.startswith("."):
            continue  # Skip hidden files

        if item.is_file():
            shutil.copy2(item, target_dir)
        elif item.is_dir():
            shutil.copytree(item, target_dir / item.name)

    print("✅ Files copied successfully")

    # Create global commands if requested
    if install_global:
        create_global_commands(target_dir)


def create_global_commands(target_dir: Path):
    """Create global commands accessible from anywhere.

    Args:
        target_dir: Directory containing the deployed tools.
    """
    print("🔧 Creating global commands...")

    if platform.system() == "Windows":
        create_windows_commands(target_dir)
    else:
        create_unix_commands(target_dir)


def create_windows_commands(target_dir: Path):
    """Create Windows global commands.

    Args:
        target_dir: Directory containing the deployed tools.
    """
    # Create batch files in a directory that's in PATH
    bin_dir = Path.home() / "bin"
    bin_dir.mkdir(exist_ok=True)

    # Main new-project script (uses existing project_detector)
    new_project_script = target_dir / "new-project.py"
    new_project_content = f"""@echo off
python "{target_dir}/new-project.py" %*
"""
    batch_script = bin_dir / "new-project.bat"
    batch_script.write_text(new_project_content, encoding="utf-8")

    # Create other batch files
    scripts = [
        "new-python-project.py",
        "new-js-project.py",
        "vscode-config.py",
        "template-helpers.py",
        "spellcheck.py",
        "dev-tools-install.py",
        "setup-dev-env.py",
        "context-menu.py",
        "registrator.py",
        "lint-project.py",
    ]

    for script in scripts:
        script_path = target_dir / script
        if script_path.exists():
            batch_name = script.replace(".py", ".bat")
            batch_content = f"""@echo off
python "{script_path}" %*
"""
            (bin_dir / batch_name).write_text(batch_content, encoding="utf-8")

    # Add to PATH if not already there
    try:
        result = run_silent(["reg", "query", "HKCU\\Environment", "/v", "PATH"])
        if result.returncode == 0:
            output = result.stdout.decode("utf-8", errors="ignore")
            if str(bin_dir) not in output:
                # Add to PATH
                new_path = f"{bin_dir};%PATH%"
                run_command(
                    [
                        "reg",
                        "add",
                        "HKCU\\Environment",
                        "/v",
                        "PATH",
                        "/t",
                        "REG_EXPAND_SZ",
                        "/d",
                        new_path,
                        "/f",
                    ],
                    "Adding bin directory to PATH",
                )
                print("✅ Added bin directory to PATH")
            else:
                print("✅ bin directory already in PATH")
    except Exception as e:
        print(f"⚠️  Could not update PATH: {e}")
        print(f'💡 Add manually: setx PATH "{bin_dir};%PATH%"')

    print(f"✅ Windows commands created in: {bin_dir}")


def create_unix_commands(target_dir: Path):
    """Create Unix global commands.

    Args:
        target_dir: Directory containing the deployed tools.
    """
    # Create shell functions
    shell = os.environ.get("SHELL", "")
    home = Path.home()

    if "zsh" in shell:
        profile_file = home / ".zshrc"
    elif "bash" in shell:
        profile_file = home / ".bashrc"
    else:
        profile_file = home / ".profile"

    # Create functions
    functions = f"""
# Works On My Machine - Global Commands
function new-project {{ python "{target_dir}/new-project.py" $@ }}
function new-python-project {{ python "{target_dir}/new-python-project.py" $@ }}
function new-js-project {{ python "{target_dir}/new-js-project.py" $@ }}
function vscode-config {{ python "{target_dir}/vscode-config.py" $@ }}
function template-helpers {{ python "{target_dir}/template-helpers.py" $@ }}
function spellcheck {{ python "{target_dir}/spellcheck.py" $@ }}
function dev-tools-install {{ python "{target_dir}/dev-tools-install.py" $@ }}
function setup-dev-env {{ python "{target_dir}/setup-dev-env.py" $@ }}
function context-menu {{ python "{target_dir}/context-menu.py" $@ }}
function registrator {{ python "{target_dir}/registrator.py" $@ }}
function lint-project {{ python "{target_dir}/lint-project.py" $@ }}
"""

    # Add to profile if not already there
    if profile_file.exists():
        with open(profile_file, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = ""

    if "Works On My Machine - Global Commands" not in content:
        with open(profile_file, "a", encoding="utf-8") as f:
            f.write(functions)

        print(f"✅ Added functions to {profile_file}")
        print("🔄 Restart your terminal or run 'source ~/.bashrc' to use commands")
    else:
        print("✅ Functions already in profile")

    print("✅ Unix commands created")


def main():
    """Run the deployment script."""
    parser = argparse.ArgumentParser(description="Deploy Works On My Machine tools")
    parser.add_argument(
        "--target",
        type=str,
        default=str(get_default_target()),
        help="Target directory for deployment",
    )
    parser.add_argument(
        "--install-global",
        action="store_true",
        help="Install global commands accessible from anywhere",
    )

    args = parser.parse_args()

    target_path = Path(args.target).expanduser().resolve()

    try:
        deploy_tools(target_path, args.install_global)
        print("\n🎉 Deployment completed successfully!")
        print(f"📁 Tools deployed to: {target_path}")

        if args.install_global:
            print("🌍 Global commands installed")
            print("💡 Restart your terminal to use the new commands")
        else:
            print("💡 To install global commands, run with --install-global")

    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
