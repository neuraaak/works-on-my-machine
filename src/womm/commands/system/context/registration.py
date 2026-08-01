#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# CONTEXT REGISTRATION - Register and unregister commands
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Registration commands for the context menu.

Behaviour is unchanged from the single-module version: these commands only
moved file.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import sys
from typing import cast

# Third-party imports
import click
from ezpl import LogLevel
from rich.progress import TaskID

# Local imports
from ....interfaces import ContextMenuInterface
from ....services.context import ContextParameters
from ....ui.common import ezpl_bridge, ezprinter
from ....ui.context import ContextMenuWizard
from ....ui.context.display import (
    render_script_registration_result,
    render_script_unregistration_result,
)
from . import _check_windows, context_group

# ///////////////////////////////////////////////////////////////
# FUNCTIONS
# ///////////////////////////////////////////////////////////////


def _resolve_registration_target(
    target_path: str | None,
    label: str | None,
    icon: str,
    root: bool,
    file: bool,
    files: bool,
    background: bool,
    file_types: tuple[str, ...],
    extensions: tuple[str, ...],
    interactive: bool,
) -> tuple[str, str, str, ContextParameters] | None:
    """Resolve the (target, label, icon, context_params) tuple for registration.

    Runs the interactive wizard or validates the non-interactive flags.

    Returns:
        The resolved tuple, or None if the user cancelled (interactive) or a
        required option is missing (non-interactive).
    """
    if interactive:
        wizard_target, wizard_label, wizard_icon, context_params = (
            ContextMenuWizard.run_setup()
        )
        if not wizard_target or not wizard_label or context_params is None:
            return None
        resolved_icon = (
            wizard_icon if isinstance(wizard_icon, str) and wizard_icon else "auto"
        )
        return wizard_target, wizard_label, resolved_icon, context_params

    if not target_path:
        ezprinter.error("Missing required option: --target")
        ezprinter.info("Use --interactive for guided setup")
        return None
    if not label:
        ezprinter.error("Missing required option: --label")
        ezprinter.info("Use --interactive for guided setup")
        return None

    resolved_icon = icon if isinstance(icon, str) and icon else "auto"
    context_params = ContextParameters.from_flags(
        root=root,
        file=file,
        files=files,
        background=background,
        file_types=list(file_types) if file_types else None,
        extensions=list(extensions) if extensions else None,
    )
    return target_path, label, resolved_icon, context_params


# ///////////////////////////////////////////////////////////////
# REGISTRATION COMMANDS
# ///////////////////////////////////////////////////////////////


@context_group.command("register")
@click.help_option("-h", "--help")
@click.option(
    "--target",
    "target_path",
    type=click.Path(),
    help="Script or executable to register in context menu",
)
@click.option(
    "-l",
    "--label",
    help="Label to display in context menu",
)
@click.option(
    "--icon",
    default="auto",
    help="Icon path or 'auto' for auto-detection (default: auto)",
)
@click.option(
    "--root",
    is_flag=True,
    help="Register for root directories (drives) only",
)
@click.option(
    "--file",
    is_flag=True,
    help="Register for single file selection",
)
@click.option(
    "-F",
    "--files",
    is_flag=True,
    help="Register for multiple file selection",
)
@click.option(
    "--background",
    is_flag=True,
    help="Register for background context only",
)
@click.option(
    "--file-types",
    multiple=True,
    help="File types to register for (e.g., image, text, archive)",
)
@click.option(
    "--extension",
    "extensions",
    multiple=True,
    help="Custom file extensions (e.g., .py, .js)",
)
@click.option(
    "-I",
    "--interactive",
    is_flag=True,
    help="Interactive mode - guided setup",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Verbose mode",
)
def context_register(
    target_path: str | None,
    label: str | None,
    icon: str,
    root: bool,
    file: bool,
    files: bool,
    background: bool,
    file_types: tuple[str, ...],
    extensions: tuple[str, ...],
    interactive: bool,
    verbose: bool,
) -> None:
    """📝 Register scripts in Windows context menu."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Context Menu Registration")

    manager = ContextMenuInterface()

    if not _check_windows(manager):
        ezprinter.info("Consider using symbolic links or aliases on Unix systems")
        sys.exit(1)

    resolved = _resolve_registration_target(
        target_path,
        label,
        icon,
        root,
        file,
        files,
        background,
        file_types,
        extensions,
        interactive,
    )
    if resolved is None:
        if interactive:
            ezprinter.info("Registration cancelled")
            return
        sys.exit(1)
    resolved_target, resolved_label, resolved_icon, context_params = resolved

    if verbose:
        ezprinter.info(f"Target: {resolved_target}")
        ezprinter.info(f"Label: {resolved_label}")
        ezprinter.info(f"Icon: {resolved_icon}")
        if context_params:
            ezprinter.info(f"Context: {context_params.get_description()}")

    backup_dir = manager.get_backup_directory()
    backup_file = str(backup_dir / "context_menu_backup_before_register.json")
    with ezprinter.create_spinner_with_status(
        "Creating backup before registration..."
    ) as (progress, task):
        progress.update(cast(TaskID, task), status="Creating backup...")
        backup_result = manager.backup_entries(backup_file)

    if not backup_result.success:
        ezprinter.error(f"Backup failed: {backup_result.error}")
        sys.exit(1)

    if verbose:
        ezprinter.info(f"Backup created: {backup_file}")

    with ezprinter.create_spinner_with_status(
        "Registering script in context menu..."
    ) as (progress, task):
        progress.update(cast(TaskID, task), status="Adding registry entries...")
        result = manager.register_script(
            resolved_target, resolved_label, resolved_icon, False, context_params
        )

    render_script_registration_result(result)
    sys.exit(0 if result.success else 1)


# ///////////////////////////////////////////////////////////////
# UNREGISTRATION COMMANDS
# ///////////////////////////////////////////////////////////////


@context_group.command("unregister")
@click.help_option("-h", "--help")
@click.option(
    "--remove",
    "remove_key",
    required=True,
    help="Key name to remove (as stored in registry)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def context_unregister(remove_key: str, verbose: bool) -> None:
    """🗑️ Unregister scripts from Windows context menu."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Context Menu Unregistration")

    manager = ContextMenuInterface()

    if not _check_windows(manager):
        return

    if verbose:
        ezprinter.info(f"Removing key: {remove_key}")

    with ezprinter.create_spinner_with_status(
        "Unregistering script from context menu..."
    ) as (progress, task):
        progress.update(cast(TaskID, task), status="Removing registry entries...")
        result = manager.unregister_script(remove_key)

    render_script_unregistration_result(result)
    sys.exit(0 if result.success else 1)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////

__all__ = ["context_register", "context_unregister"]
