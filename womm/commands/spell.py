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
from rich.json import JSON

from womm.core.dependencies.dev_tools_manager import dev_tools_manager
from womm.core.ui.console import console

# IMPORTS
########################################################
# Internal modules and dependencies
from womm.core.utils.spell_manager import spell_manager

# MAIN FUNCTIONS
########################################################
# Core CLI functionality and command groups


@click.group()
def spell_group():
    """📝 Spell checking with CSpell."""


# UTILITY FUNCTIONS
########################################################
# Helper functions and utilities


def print_spell_add_result(result):
    """Display spell add result"""
    if result.success:
        console.print("✅ Words added successfully", style="green")
    else:
        console.print(f"❌ Failed to add words: {result.message}", style="red")


def print_spell_check_start(path: Path, fix: bool):
    """Display spell check start message"""
    mode = "fix" if fix else "check"
    console.print(f"🔍 Starting spell {mode} for: {path}", style="blue")


def print_spell_dictionary_info(dict_info):
    """Display dictionary information"""
    console.print("📚 Dictionary Information:", style="cyan")
    console.print(
        f"  Directory exists: {'✅' if dict_info['directory_exists'] else '❌'}"
    )
    console.print(f"  Total files: {dict_info['total_files']}")
    if dict_info["files"]:
        console.print("  Files:")
        for file_path in dict_info["files"]:
            console.print(f"    - {file_path}")


def print_spell_install_progress():
    """Display spell installation progress"""
    console.print("📦 Installing CSpell...", style="blue")


def print_spell_install_result(result):
    """Display spell installation result"""
    if result.success:
        console.print("✅ CSpell installed successfully", style="green")
    else:
        console.print(f"❌ CSpell installation failed: {result.message}", style="red")


def print_spell_result(result):
    """Display spell result"""
    if result.success:
        console.print(f"✅ {result.message}", style="green")
    else:
        console.print(f"❌ {result.message}", style="red")


def print_spell_setup_result(result):
    """Display spell setup result"""
    if result.success:
        console.print("✅ CSpell setup completed successfully", style="green")
    else:
        console.print(f"❌ CSpell setup failed: {result.message}", style="red")


def print_spell_start(operation: str):
    """Display spell operation start"""
    console.print(f"🔧 Starting {operation}...", style="blue")


def print_spell_status(status_data):
    """Display spell status"""
    console.print("📊 CSpell Project Status:", style="cyan")
    console.print(
        f"  Project configured: {'✅' if status_data.get('configured') else '❌'}"
    )
    if status_data.get("config_file"):
        console.print(f"  Config file: {status_data['config_file']}")
    if status_data.get("words_count"):
        console.print(f"  Custom words: {status_data['words_count']}")


def print_spell_summary(summary):
    """Display spell check summary"""
    if summary.success:
        console.print("✅ Spell check completed successfully", style="green")
        if hasattr(summary, "issues_count") and summary.issues_count > 0:
            console.print(
                f"⚠️ Found {summary.issues_count} spelling issues", style="yellow"
            )
    else:
        console.print(f"❌ Spell check failed: {summary.error}", style="red")


def print_spell_tool_check_result(available: bool):
    """Display CSpell tool availability check"""
    if available:
        console.print("✅ CSpell is available", style="green")
    else:
        console.print("❌ CSpell is not available", style="red")


def print_prompt(message: str, required: bool = False) -> str:
    """Display a prompt and get user input"""
    prompt_text = f"{message}: "
    if required:
        prompt_text += "(required) "
    return input(prompt_text)


def confirm(message: str) -> bool:
    """Display a confirmation prompt"""
    response = input(f"{message} (y/N): ").lower().strip()
    return response in ["y", "yes"]


# COMMAND FUNCTIONS
########################################################
# Command implementations


@spell_group.command("install")
def spell_install():
    """📦 Install CSpell and dictionaries globally."""
    # Check if CSpell is already available
    print_spell_tool_check_result(spell_manager.cspell_available)

    if not spell_manager.cspell_available:
        # Install CSpell via DevToolsManager (ensures Node via runtime_manager)
        print_spell_install_progress()
        tool_result = dev_tools_manager.install_dev_tool(
            language="universal", tool_type="spell_checking", tool="cspell"
        )
        if not tool_result.success:
            print_spell_install_result(
                type(
                    "Result",
                    (),
                    {
                        "success": False,
                        "message": tool_result.error
                        or "Failed to install CSpell via dev tools manager",
                    },
                )()
            )
            sys.exit(1)

        # Refresh cspell availability check after installation
        spell_manager.cspell_available = spell_manager._check_cspell_availability()

    # Install essential dictionaries
    print_spell_start("dictionary setup")
    dict_result = spell_manager.setup_dictionaries()
    print_spell_setup_result(dict_result)

    # Final success message
    ok_result = type(
        "Result", (), {"success": True, "message": "CSpell and dictionaries are ready"}
    )()
    print_spell_install_result(ok_result)

    sys.exit(0)


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
    print_spell_start("project setup")
    result = spell_manager.setup_project(project_name, project_type)
    print_spell_setup_result(result)

    sys.exit(0 if result.success else 1)


@spell_group.command("status")
def spell_status():
    """📊 Display CSpell project status."""
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
    """➕ Add words to CSpell configuration."""
    if interactive:
        # Interactive mode - prompt for words
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
    """📚 Add all dictionaries from .cspell-dict/ to CSpell configuration."""
    from womm.core.tools.dictionary_manager import get_dictionary_info

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
    if not force and not confirm("Continue with adding all dictionaries?"):
        print_spell_result(
            type(
                "Result",
                (),
                {"success": False, "message": "Operation cancelled by user"},
            )()
        )
        sys.exit(1)

    # Add all dictionaries
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
    """📋 List available dictionaries in .cspell-dict/."""
    from womm.core.tools.dictionary_manager import get_dictionary_info

    dict_info = get_dictionary_info()
    print_spell_dictionary_info(dict_info)

    sys.exit(0)


@spell_group.command("check")
@click.argument("path", type=click.Path(exists=True), default=".", required=False)
@click.option("--fix", is_flag=True, help="Interactive fix mode")
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Output detailed JSON diagnostics when available",
)
def spell_check(path, fix, json_output):
    """🔍 Check spelling in files."""
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
    summary = spell_manager.check_spelling(Path(path), fix, json_output=json_output)
    print_spell_summary(summary)

    # Optional JSON output
    if json_output and getattr(summary, "data", None) is not None:
        console.print(JSON.from_data(summary.data))

    sys.exit(0 if summary.success else 1)
