#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# SHARED MIGRATION - Legacy Data Layout Migration
# Project: works-on-my-machine
# ///////////////////////////////////////////////////////////////

"""
One-shot migration of the WOMM data directory.

The self-installer used to write dot-prefixed directories next to the code
it copied into ``~/.womm``. Now that the data directory holds data only,
those become plain directories:

===========================  ==========================
Legacy                       Current
===========================  ==========================
``.logs/``                   ``logs/``
``.templates/``              ``templates/``
``.backup/.path*.json``      ``backups/path/``
``.backup/context_menu/``    ``backups/registry/``
===========================  ==========================

The migration is **idempotent** (guarded by ``state.json``), **never
overwrites** an existing destination, and **never raises**: it runs at
startup, where a failure must degrade into a report rather than take the
CLI down. Leftover *code* in ``~/.womm`` is out of scope — it is reported
so a diagnostic command can offer to clean it up, never deleted here.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path

# Local imports
from .paths import (
    logs_dir,
    path_backups_dir,
    registry_backups_dir,
    state_file,
    user_templates_dir,
    womm_data_dir,
)

# ///////////////////////////////////////////////////////////////
# LOGGER SETUP
# ///////////////////////////////////////////////////////////////

logger = logging.getLogger(__name__)

# ///////////////////////////////////////////////////////////////
# CONSTANTS
# ///////////////////////////////////////////////////////////////

# Layout version written to ``state.json``. Bump when the data directory
# changes shape again; the migration reruns only for older versions.
DATA_VERSION = 1

# Legacy directory names, relative to the data directory.
LEGACY_LOGS = ".logs"
LEGACY_TEMPLATES = ".templates"
LEGACY_BACKUPS = ".backup"
LEGACY_REGISTRY_BACKUPS = "context_menu"

# Legacy PATH-backup files live directly in ``.backup/``.
LEGACY_PATH_BACKUP_GLOB = ".path*.json"

# Entries that mean the legacy installer copied *code* into the data dir.
CODE_RESIDUE_ENTRIES = ("womm", "womm.py", "womm.bat", ".proof")

# ///////////////////////////////////////////////////////////////
# RESULT TYPE
# ///////////////////////////////////////////////////////////////


@dataclass
class MigrationReport:
    """Outcome of a migration attempt (read-only summary)."""

    performed: bool = False
    moved_count: int = 0
    skipped_count: int = 0
    failed_count: int = 0
    code_residue: bool = False
    errors: list[str] = field(default_factory=list)


# ///////////////////////////////////////////////////////////////
# INTERNAL HELPERS
# ///////////////////////////////////////////////////////////////


def _already_migrated() -> bool:
    """Return True when ``state.json`` records the current layout version."""
    state = state_file()
    if not state.is_file():
        return False

    try:
        recorded = json.loads(state.read_text(encoding="utf-8")).get("data_version", 0)
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as e:
        # An unreadable state file is treated as "not migrated": rerunning is
        # safe (every move is skip-if-exists), losing data is not.
        logger.warning(f"Unreadable state file, assuming no migration: {e}")
        return False

    return isinstance(recorded, int) and recorded >= DATA_VERSION


def _write_state() -> None:
    """Record the current layout version, best effort."""
    try:
        state_file().write_text(
            json.dumps({"data_version": DATA_VERSION}, indent=2),
            encoding="utf-8",
        )
    except OSError as e:
        logger.warning(f"Could not write the data state file: {e}")


def _move_entry(source: Path, destination: Path, report: MigrationReport) -> None:
    """Move one entry, skipping rather than overwriting an existing target."""
    if destination.exists():
        report.skipped_count += 1
        logger.info(f"Skipping {source}: {destination} already exists")
        return

    try:
        shutil.move(str(source), str(destination))
    except (OSError, shutil.Error) as e:
        report.failed_count += 1
        report.errors.append(f"{source} -> {destination}: {e}")
        logger.warning(f"Could not migrate {source}: {e}")
        return

    report.moved_count += 1


def _move_directory_contents(
    source_dir: Path,
    destination_dir: Path,
    report: MigrationReport,
    pattern: str = "*",
) -> None:
    """Move every entry matching ``pattern`` from one directory to another."""
    if not source_dir.is_dir():
        return

    for entry in sorted(source_dir.glob(pattern)):
        _move_entry(entry, destination_dir / entry.name, report)


# ///////////////////////////////////////////////////////////////
# PUBLIC API
# ///////////////////////////////////////////////////////////////


def migrate_legacy_data_layout() -> MigrationReport:
    """Move a legacy data directory to the current layout.

    Safe to call on every startup: it returns immediately once
    ``state.json`` records the current version, and never raises.

    Returns:
        MigrationReport: what moved, what was skipped, and what failed.
    """
    report = MigrationReport()

    try:
        if _already_migrated():
            return report

        data_dir = womm_data_dir()
        report.performed = True

        _move_directory_contents(data_dir / LEGACY_LOGS, logs_dir(), report)
        _move_directory_contents(
            data_dir / LEGACY_TEMPLATES, user_templates_dir(), report
        )

        legacy_backups = data_dir / LEGACY_BACKUPS
        _move_directory_contents(
            legacy_backups, path_backups_dir(), report, pattern=LEGACY_PATH_BACKUP_GLOB
        )
        _move_directory_contents(
            legacy_backups / LEGACY_REGISTRY_BACKUPS, registry_backups_dir(), report
        )

        report.code_residue = any(
            (data_dir / entry).exists() for entry in CODE_RESIDUE_ENTRIES
        )

        # Keep retrying on later startups when a source entry could not be moved.
        # Writing the version despite a failure would strand that legacy data forever.
        if not report.failed_count:
            _write_state()

        if report.moved_count:
            logger.info(f"Migrated {report.moved_count} entries to the new data layout")
    except OSError as e:
        report.performed = True
        report.failed_count += 1
        report.errors.append(str(e))
        logger.warning(f"Could not initialize the data migration: {e}")

    return report


# ///////////////////////////////////////////////////////////////
# EXPORTS
# ///////////////////////////////////////////////////////////////

__all__ = ["DATA_VERSION", "MigrationReport", "migrate_legacy_data_layout"]
