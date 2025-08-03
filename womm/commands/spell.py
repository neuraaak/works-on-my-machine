#!/usr/bin/env python3
"""
Spell checking commands for WOMM CLI.
Handles CSpell configuration and spell checking.
"""

import sys
from pathlib import Path

import click

from ..utils.path_manager import resolve_script_path


@click.group()
def spell_group():
    """📝 Spell checking with CSpell."""


@spell_group.command("install")
def spell_install():
    """Install CSpell and dictionaries globally."""
    # Check and install CSpell if needed
    from shared.dependency_manager import check_and_install_dependencies
    if not check_and_install_dependencies(["cspell"]):
        click.echo("❌ CSpell installation required but not completed")
        sys.exit(1)

    script_path = resolve_script_path("shared/tools/cspell_manager.py")

    cmd = [sys.executable, str(script_path), "--install"]
    from shared.core.cli_manager import run_command
    result = run_command(cmd, "Installing CSpell globally")
    sys.exit(0 if result.success else 1)


@spell_group.command("setup")
@click.argument("project_name")
@click.option(
    "--type",
    "project_type",
    type=click.Choice(["python", "javascript"]),
    help="Force project type",
)
def spell_setup(project_name, project_type):
    """Set CSpell for current project."""
    script_path = resolve_script_path("shared/tools/cspell_manager.py")

    cmd = [sys.executable, str(script_path), "--setup-project", project_name]
    if project_type:
        cmd.extend(["--type", project_type])

    from shared.core.cli_manager import run_command
    result = run_command(cmd, f"Setting up CSpell for {project_name}")
    sys.exit(0 if result.success else 1)


@spell_group.command("status")
def spell_status():
    """Display CSpell project status."""
    script_path = resolve_script_path("shared/tools/cspell_manager.py")

    cmd = [sys.executable, str(script_path), "--status"]
    from shared.core.cli_manager import run_command
    result = run_command(cmd, "Displaying CSpell status")
    sys.exit(0 if result.success else 1)


@spell_group.command("add")
@click.argument("words", nargs=-1, required=False)
@click.option(
    "--file", "file_path", type=click.Path(exists=True), help="Add words from file"
)
@click.option("--interactive", is_flag=True, help="Interactive mode")
def spell_add(words, file_path, interactive):
    """Add words to CSpell configuration."""
    script_path = resolve_script_path("shared/tools/cspell_manager.py")

    if interactive:
        cmd = [sys.executable, str(script_path), "--add-interactive"]
    elif file_path:
        cmd = [sys.executable, str(script_path), "--add-file", file_path]
    elif words:
        cmd = [sys.executable, str(script_path), "--add"] + list(words)
    else:
        click.echo("Error: Specify words, --file, or --interactive", err=True)
        sys.exit(1)

    from shared.core.cli_manager import run_command
    result = run_command(cmd, "Adding words to CSpell configuration")
    sys.exit(0 if result.success else 1)


@spell_group.command("add-all")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def spell_add_all(force):
    """Add all dictionaries from .cspell-dict/ to CSpell configuration."""
    from shared.tools.dictionary_manager import add_all_dictionaries

    # Override input function to skip confirmation if --force
    if force:
        import builtins

        original_input = builtins.input
        builtins.input = lambda _prompt: "y"

    try:
        success = add_all_dictionaries()
        sys.exit(0 if success else 1)
    finally:
        if force:
            builtins.input = original_input


@spell_group.command("list-dicts")
def spell_list_dicts():
    """List available dictionaries in .cspell-dict/."""
    from shared.tools.dictionary_manager import get_dictionary_info

    info = get_dictionary_info()

    if not info["directory_exists"]:
        click.echo("❌ .cspell-dict directory not found")
        click.echo("💡 Create the directory and add dictionary files (.txt)")
        sys.exit(1)

    if info["total_files"] == 0:
        click.echo("📁 .cspell-dict directory is empty")
        click.echo("💡 Add .txt files with one word per line")
        sys.exit(0)

    click.echo(f"📚 Found {info['total_files']} dictionary files:")
    for file_path in info["files"]:
        file_name = Path(file_path).name
        click.echo(f"   - {file_name}")

    click.echo(f"\n📊 Total words available: {info['total_words']}")


@spell_group.command("check")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Interactive fix mode")
def spell_check(path, fix):
    """Check spelling in files."""
    # Check and install CSpell if needed
    from shared.dependency_manager import check_and_install_dependencies
    if not check_and_install_dependencies(["cspell"]):
        click.echo("❌ CSpell installation required but not completed")
        sys.exit(1)

    script_path = resolve_script_path("shared/tools/cspell_manager.py")

    if fix:
        cmd = [sys.executable, str(script_path), "--fix", path]
    else:
        cmd = [sys.executable, str(script_path), "--check", path]

    from shared.core.cli_manager import run_command
    result = run_command(cmd, f"Spell checking {path}")
    sys.exit(0 if result.success else 1)
