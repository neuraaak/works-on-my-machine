#!/usr/bin/env python3
"""
Spell checking commands for WOMM CLI.
Handles CSpell configuration and spell checking.
"""

import sys
from pathlib import Path

import click

from shared.core.spell_manager import SpellManager
from shared.ui import (
    print_spell_add_result,
    print_spell_check_start,
    print_spell_dictionary_info,
    print_spell_install_progress,
    print_spell_install_result,
    print_spell_result,
    print_spell_setup_result,
    print_spell_start,
    print_spell_status,
    print_spell_summary,
    print_spell_tool_check_result,
)


@click.group()
def spell_group():
    """📝 Spell checking with CSpell."""


@spell_group.command("install")
def spell_install():
    """Install CSpell and dictionaries globally."""
    spell_manager = SpellManager()

    # Check if CSpell is already available
    print_spell_tool_check_result(spell_manager.cspell_available)

    if spell_manager.cspell_available:
        print_spell_result(
            type(
                "Result",
                (),
                {"success": True, "message": "CSpell is already installed"},
            )()
        )
        return

    # Install CSpell
    print_spell_install_progress()
    result = spell_manager.install_cspell()
    print_spell_install_result(result)

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
    spell_manager = SpellManager()

    print_spell_start("project setup")
    result = spell_manager.setup_project(project_name, project_type)
    print_spell_setup_result(result)

    sys.exit(0 if result.success else 1)


@spell_group.command("status")
def spell_status():
    """Display CSpell project status."""
    spell_manager = SpellManager()

    result = spell_manager.get_project_status()

    if result.success:
        print_spell_status(result.data)
    else:
        print_spell_result(result)

    sys.exit(0 if result.success else 1)


@spell_group.command("add")
@click.argument("words", nargs=-1, required=False)
@click.option(
    "--file", "file_path", type=click.Path(exists=True), help="Add words from file"
)
@click.option("--interactive", is_flag=True, help="Interactive mode")
def spell_add(words, file_path, interactive):
    """Add words to CSpell configuration."""
    spell_manager = SpellManager()

    if interactive:
        # Interactive mode - prompt for words
        from shared.ui import print_prompt

        word = print_prompt("Enter word to add", required=True)
        if word:
            words = [word]
        else:
            print_spell_result(
                type("Result", (), {"success": False, "message": "No word provided"})()
            )
            sys.exit(1)

    if file_path:
        # Add words from file
        result = spell_manager.add_words_from_file(Path(file_path))
    elif words:
        # Add words from command line
        result = spell_manager.add_words(list(words))
    else:
        print_spell_result(
            type(
                "Result",
                (),
                {
                    "success": False,
                    "message": "Specify words, --file, or --interactive",
                },
            )()
        )
        sys.exit(1)

    print_spell_add_result(result)
    sys.exit(0 if result.success else 1)


@spell_group.command("add-all")
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def spell_add_all(force):
    """Add all dictionaries from .cspell-dict/ to CSpell configuration."""
    from shared.tools.dictionary_manager import get_dictionary_info

    # Get dictionary information
    dict_info = get_dictionary_info()

    if not dict_info["directory_exists"]:
        print_spell_result(
            type(
                "Result",
                (),
                {"success": False, "message": ".cspell-dict directory not found"},
            )()
        )
        sys.exit(1)

    if dict_info["total_files"] == 0:
        print_spell_result(
            type(
                "Result",
                (),
                {"success": False, "message": ".cspell-dict directory is empty"},
            )()
        )
        sys.exit(1)

    # Show what will be added
    print_spell_dictionary_info(dict_info)

    # Confirm unless --force
    if not force:
        from shared.ui import confirm

        if not confirm("Continue with adding all dictionaries?"):
            print_spell_result(
                type(
                    "Result",
                    (),
                    {"success": False, "message": "Operation cancelled by user"},
                )()
            )
            sys.exit(1)

    # Add all dictionaries
    spell_manager = SpellManager()
    success_count = 0
    error_count = 0

    for file_path in dict_info["files"]:
        result = spell_manager.add_words_from_file(Path(file_path))
        if result.success:
            success_count += 1
        else:
            error_count += 1

    if error_count == 0:
        print_spell_result(
            type(
                "Result",
                (),
                {
                    "success": True,
                    "message": f"All {success_count} dictionaries added successfully",
                },
            )()
        )
    elif success_count > 0:
        print_spell_result(
            type(
                "Result",
                (),
                {
                    "success": True,
                    "message": f"{success_count} dictionaries added, {error_count} failed",
                },
            )()
        )
    else:
        print_spell_result(
            type(
                "Result",
                (),
                {"success": False, "message": "No dictionaries could be added"},
            )()
        )

    sys.exit(0 if success_count > 0 else 1)


@spell_group.command("list-dicts")
def spell_list_dicts():
    """List available dictionaries in .cspell-dict/."""
    from shared.tools.dictionary_manager import get_dictionary_info

    dict_info = get_dictionary_info()
    print_spell_dictionary_info(dict_info)

    sys.exit(0)


@spell_group.command("check")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Interactive fix mode")
def spell_check(path, fix):
    """Check spelling in files."""
    spell_manager = SpellManager()

    # Show header first
    print_spell_check_start(Path(path), fix)

    # Check CSpell availability
    print_spell_tool_check_result(spell_manager.cspell_available)

    if not spell_manager.cspell_available:
        print_spell_result(
            type(
                "Result",
                (),
                {
                    "success": False,
                    "message": 'CSpell is not available. Run "womm spell install" first.',
                },
            )()
        )
        sys.exit(1)

    # Perform spell check
    summary = spell_manager.check_spelling(Path(path), fix)
    print_spell_summary(summary)

    sys.exit(0 if summary.success else 1)
