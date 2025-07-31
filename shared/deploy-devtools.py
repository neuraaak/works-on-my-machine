#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to deploy development tools to a global directory.

This script copies all development tools to a global directory
(e.g., ~/.dev-tools) to reuse them in all your projects.

Usage:
    python deploy-devtools.py [--target ~/.dev-tools]
    python deploy-devtools.py --install-global
"""

import argparse
import shutil
import sys
from pathlib import Path


def deploy_devtools(target_dir: Path, create_global_command: bool = False):
    """Deploy development tools to a target directory."""

    # Source directory (current project's .devtools)
    source_dir = Path(__file__).parent.parent

    print("🚀 Deploying development tools")
    print(f"📁 Source: {source_dir}")
    print(f"📁 Target: {target_dir}")

    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy all .devtools content
    if target_dir.exists():
        print(f"⚠️  Directory {target_dir} already exists.")
        response = input("Overwrite existing content? (y/N): ")
        if response.lower() != "y":
            print("Cancelled.")
            return

    # Copy recursively
    for item in source_dir.iterdir():
        if item.name == "__pycache__":
            continue

        target_item = target_dir / item.name

        if item.is_dir():
            if target_item.exists():
                shutil.rmtree(target_item)
            shutil.copytree(item, target_item)
            print(f"   ✓ {item.name}/ (directory)")
        else:
            shutil.copy2(item, target_item)
            print(f"   ✓ {item.name}")

    # Create global launch script
    if create_global_command:
        create_global_scripts(target_dir)

    print(f"\n✅ Deployment completed in {target_dir}")
    print_usage_instructions(target_dir)


def create_global_scripts(target_dir: Path):
    """Create global scripts to use tools everywhere."""

    print("\n🔧 Creating global commands...")

    # Script to initialize a new project
    new_project_script = target_dir / "new-python-project.py"
    new_project_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Global script to initialize a new Python project with dev environment.

Usage:
    python {new_project_script} my_new_project
    python {new_project_script} --current-dir
"""

import sys
import subprocess
from pathlib import Path

# Add devtools directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

# Import and run setup-project script
from setup_project import main

if __name__ == "__main__":
    main()
'''

    new_project_script.write_text(new_project_content, encoding="utf-8")
    print(f"   ✓ {new_project_script}")

    # Windows batch script
    if sys.platform == "win32":
        batch_script = target_dir / "new-python-project.bat"
        batch_content = f"""@echo off
python "{new_project_script}" %*
"""
        batch_script.write_text(batch_content, encoding="utf-8")
        print(f"   ✓ {batch_script}")


def add_to_path(target_dir: Path):
    """Instructions to add to PATH."""

    if sys.platform == "win32":
        print(
            f"""
🔧 To use commands globally on Windows:
1. Add to your PATH: {target_dir}
2. Or create an alias in PowerShell:
    echo 'function new-python-project {{ python "{target_dir}/new-python-project.py" @args }}' >> $PROFILE
"""
        )
    else:
        print(
            f"""
🔧 To use commands globally on Linux/Mac:
1. Add to your ~/.bashrc or ~/.zshrc:
    export PATH="{target_dir}:$PATH"
2. Or create an alias:
    alias new-python-project="python {target_dir}/new-python-project.py"
"""
        )


def print_usage_instructions(target_dir: Path):
    """Display usage instructions."""

    print(
        f"""
📋 Usage:

🆕 New project:
    python {target_dir}/scripts/setup-project.py my_new_project

🔧 Existing project:
    python {target_dir}/scripts/setup-project.py --current-dir

📁 Deployed structure:
    {target_dir}/
    ├── scripts/           # Automation scripts
    ├── configs/           # Configurations (.flake8, pre-commit, etc.)
    ├── vscode/           # VSCode configuration
    ├── templates/        # File templates
    └── README.md         # Documentation

💡 Tip:
    Add {target_dir}/scripts to PATH to use scripts everywhere!
"""
    )


def main():
    """Launch the main function."""
    parser = argparse.ArgumentParser(description="Deploy development tools")
    parser.add_argument(
        "--target",
        type=Path,
        default=Path.home() / ".dev-tools",
        help="Target directory (default: ~/.dev-tools)",
    )
    parser.add_argument(
        "--install-global", action="store_true", help="Create global commands"
    )

    args = parser.parse_args()

    deploy_devtools(args.target, args.install_global)

    if args.install_global:
        add_to_path(args.target)


if __name__ == "__main__":
    main()
