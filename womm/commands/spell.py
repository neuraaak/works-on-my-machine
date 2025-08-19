#!/usr/bin/env python3
"""
Spell checking commands for WOMM CLI.
Handles CSpell configuration and spell checking.
"""

# IMPORTS
########################################################
# External modules and dependencies

import sys
from pathlib import Path

import click

# IMPORTS
########################################################
# Internal modules and dependencies
from ..core.managers.spell.spell_manager import spell_manager

# MAIN FUNCTIONS
########################################################
# Core CLI functionality and command groups


@click.group()
def spell_group():
    """📝 Spell checking with CSpell."""


# COMMAND FUNCTIONS
########################################################
# Command implementations


@spell_group.command("install")
def spell_install():
    """📦 Install CSpell and dictionaries globally."""
    result = spell_manager.install_cspell()
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
    """⚙️ Set CSpell for current project."""
    result = spell_manager.perform_setup_project(project_name, project_type)
    sys.exit(0 if result.success else 1)


@spell_group.command("status")
def spell_status():
    """📊 Display CSpell project status."""
    result = spell_manager.display_project_status()
    sys.exit(0 if result.success else 1)


@spell_group.command("add")
@click.argument("words", nargs=-1, required=False)
@click.option(
    "--file", "file_path", type=click.Path(exists=True), help="Add words from file"
)
@click.option("--interactive", is_flag=True, help="Interactive mode")
def spell_add(words, file_path, interactive):
    """➕ Add words to CSpell configuration."""
    result = spell_manager.perform_add_words(
        words=list(words) if words else None,
        file_path=Path(file_path) if file_path else None,
        interactive=interactive,
    )
    sys.exit(0 if result.success else 1)


@spell_group.command("add-all")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def spell_add_all(force):
    """📚 Add all dictionaries from .cspell-dict/ to CSpell configuration."""
    result = spell_manager.perform_add_all_dictionaries(force=force)
    sys.exit(0 if result.success else 1)


@spell_group.command("list-dicts")
def spell_list_dicts():
    """📋 List available dictionaries in .cspell-dict/."""
    result = spell_manager.perform_list_dictionaries()
    sys.exit(0 if result.success else 1)


@spell_group.command("check")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option(
    "--json",
    "json_export",
    is_flag=True,
    default=False,
    help="Export results to JSON file in ~/.womm/spell-results/",
)
@click.option(
    "--json-dir",
    "json_output",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Export results to JSON file in specified directory",
)
def spell_check(path, json_export, json_output):
    """🔍 Check spelling in files."""
    # Déterminer le chemin d'export JSON
    export_path = None
    if json_export:
        # Utiliser le chemin par défaut ~/.womm/spell-results/
        from ..core.installation.installation_manager import get_target_womm_path

        womm_path = get_target_womm_path()
        export_path = womm_path / "spell-results"
    elif json_output is not None:
        # Utiliser le chemin personnalisé spécifié
        export_path = json_output

    result = spell_manager.perform_spell_check(path=Path(path), json_output=export_path)
    sys.exit(0 if result.success else 1)
