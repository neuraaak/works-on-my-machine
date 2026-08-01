#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# DOCTOR - Runtime Diagnostics
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
Read-only runtime diagnostics for the WOMM CLI.

This module owns the presentation (header, renderer) and drives the
interface, which returns a Result object.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Third-party imports
import click
from ezpl import LogLevel

# Local imports
from ...interfaces import DoctorInterface
from ...ui.common import ezpl_bridge, ezprinter
from ...ui.system import render_doctor_result

# ///////////////////////////////////////////////////////////////
# COMMAND
# ///////////////////////////////////////////////////////////////


@click.command("doctor")
@click.help_option("-h", "--help")
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Enable verbose output (DEBUG level)",
)
def doctor_cmd(verbose: bool) -> None:
    """🩺 Report the installed runtime without changing user configuration."""
    if verbose:
        ezpl_bridge.set_level(LogLevel.DEBUG.label)

    ezprinter.print_header("Runtime Diagnostic")

    result = DoctorInterface().diagnose()
    render_doctor_result(result, verbose)


__all__ = ["doctor_cmd"]
