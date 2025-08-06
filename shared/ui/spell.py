#!/usr/bin/env python3
"""
Spell checking UI functions for WOMM CLI.
Provides consistent display of spell checking results and operations.
"""

# IMPORTS
########################################################
# Standard library imports
from pathlib import Path
from typing import List

# Third-party imports
# (None for this file)
# Local imports
from .console import console
from .panels import create_error_panel, create_success_panel

# MAIN FUNCTIONS
########################################################
# Core spell checking display functionality


def print_spell_start(operation: str):
    """Print spell checking operation start."""
    from .console import print_header

    print_header(f"Spell Check - {operation}")
    console.print(f"[SPELL] Starting {operation}...", style="blue")


def print_spell_progress(message: str):
    """Print spell checking progress."""
    from .console import print_info

    print_info("SPELL", message)


def print_spell_result(result):
    """Print spell checking result."""
    from .console import print_failed, print_success

    if result.success:
        print_success(result.message)
    else:
        print_failed(result.message)


def print_spell_summary(summary):
    """Print spell checking summary."""
    if summary.success:
        panel = create_success_panel("Spell Check Complete", summary.message)
    else:
        panel = create_error_panel("Spell Check Failed", summary.message)
    console.print(panel)

    # Show detailed results if available
    if hasattr(summary, "total_errors") and summary.total_errors > 0:
        print_spell_errors(summary.errors_by_file)
        print_spell_suggestions(summary.suggestions)


# UTILITY FUNCTIONS
########################################################
# Helper functions for spell checking operations


def print_spell_errors(errors_by_file: dict):
    """Print spelling errors by file."""
    if not errors_by_file:
        return

    console.print("\n[ERRORS] Spelling errors found:", style="red")

    for file_path, errors in errors_by_file.items():
        file_name = Path(file_path).name
        console.print(f"\n  📄 {file_name}:", style="yellow")
        for error in errors[:5]:  # Limit to first 5 errors per file
            console.print(f"    • {error}", style="red")

        if len(errors) > 5:
            console.print(f"    ... and {len(errors) - 5} more errors", style="dim")


def print_spell_suggestions(suggestions: List[str]):
    """Print spell checking suggestions."""
    if not suggestions:
        return

    console.print("\n[SUGGESTIONS] Next steps:", style="blue")
    for i, suggestion in enumerate(suggestions, 1):
        console.print(f"  {i}. {suggestion}", style="cyan")


def print_spell_status(status_data: dict):
    """Print project spell checking status."""
    from .console import print_header, print_info

    print_header("CSpell Project Status")
    print_info("STATUS", "CSpell Project Status:")

    # Configuration status
    config_status = "✅" if status_data.get("config_exists") else "❌"
    console.print(
        f"  {config_status} Configuration: {'Present' if status_data.get('config_exists') else 'Missing'}"
    )

    # Dictionary directory status
    dict_status = "✅" if status_data.get("dict_dir_exists") else "❌"
    console.print(
        f"  {dict_status} Dictionary directory: {'Present' if status_data.get('dict_dir_exists') else 'Missing'}"
    )

    # Dictionary files
    dict_files = status_data.get("dict_files", [])
    if dict_files:
        console.print(f"  📚 Dictionary files ({len(dict_files)}):")
        for file_name in dict_files:
            console.print(f"    • {file_name}")
        console.print(f"  📊 Total words: {status_data.get('total_words', 0)}")
    else:
        console.print("  📚 Dictionary files: None")


def print_spell_install_progress():
    """Print CSpell installation progress."""
    from .console import print_header, print_info

    print_header("CSpell Installation")
    print_info("INSTALL", "Installing CSpell and dictionaries...")


def print_spell_install_result(result):
    """Print CSpell installation result."""
    if result.success:
        panel = create_success_panel("CSpell Installation", result.message)
        console.print(panel)
    else:
        panel = create_error_panel("CSpell Installation Failed", result.message)
        console.print(panel)


def print_spell_setup_result(result):
    """Print CSpell setup result."""
    if result.success:
        panel = create_success_panel("CSpell Setup", result.message)
        console.print(panel)
    else:
        panel = create_error_panel("CSpell Setup Failed", result.message)
        console.print(panel)


def print_spell_add_result(result):
    """Print word addition result."""
    from .console import print_failed, print_success

    if result.success:
        print_success(result.message)
    else:
        print_failed(result.message)


def print_spell_dictionary_info(dict_info: dict):
    """Print dictionary information."""
    from .console import print_failed, print_header, print_info, print_tip

    print_header("CSpell Dictionaries")

    if not dict_info.get("directory_exists"):
        print_failed(".cspell-dict directory not found")
        print_tip("Create the directory and add dictionary files (.txt)")
        return

    if dict_info.get("total_files") == 0:
        print_info("INFO", ".cspell-dict directory is empty")
        print_tip("Add .txt files with one word per line")
        return

    # Create table data
    dictionaries = []
    for file_path in dict_info.get("files", []):
        file_path_obj = Path(file_path)
        try:
            word_count = len(file_path_obj.read_text(encoding="utf-8").splitlines())
            file_size = file_path_obj.stat().st_size
            file_size_str = f"{file_size} bytes"
        except Exception:
            word_count = 0
            file_size_str = "Error"

        dictionaries.append(
            {
                "file": file_path_obj.name,
                "words": word_count,
                "size": file_size_str,
                "status": "Available",
            }
        )

    # Display table
    from .tables import create_dictionary_table

    table = create_dictionary_table(dictionaries)
    console.print(table)

    # Display summary
    from .console import print_summary

    print_summary(f"Total dictionaries: {dict_info['total_files']}")
    print_summary(f"Total words available: {dict_info.get('total_words', 0)}")


def print_spell_check_start(path: Path, fix_mode: bool = False):
    """Print spell check start message."""
    from .console import print_header, print_info

    mode = "Fix" if fix_mode else "Check"
    print_header(f"Spell {mode}")
    print_info("SPELL", f"Starting spell {mode.lower()} on: {path}")


def print_spell_tool_check_result(available: bool):
    """Print CSpell tool availability check result."""
    from .console import print_failed, print_success, print_tip

    if available:
        print_success("CSpell is available")
    else:
        print_failed("CSpell is not available")
        print_tip("Run 'womm spell install' to install CSpell")
