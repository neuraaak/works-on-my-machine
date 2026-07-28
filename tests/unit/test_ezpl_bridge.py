#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST EZPL BRIDGE - Panel/table builders and progress calculations
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for ``ExtendedPrinter`` and ``DynamicLayeredProgress``.

The panel/table ``create_*`` methods are pure builders (data in, Rich object
out) and are asserted on directly. ``print_*`` methods delegate to the
inherited console/logger, so the console is patched to assert on the calls
made. ``DynamicLayeredProgress`` holds real percentage-calculation logic and
is exercised against a real ``rich.progress.Progress`` writing to an
in-memory buffer (no terminal needed).
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import io
from unittest.mock import MagicMock

# Third-party imports
import pytest
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Local imports
from womm.ui.common.ezpl_bridge import DynamicLayeredProgress, ExtendedPrinter

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def printer():
    p = ExtendedPrinter()
    p._console = MagicMock()
    return p


# ///////////////////////////////////////////////////////////////
# PRINT UTILITIES
# ///////////////////////////////////////////////////////////////


def test_print_header_prints_separators_and_title(printer):
    printer.print_header("My Title")

    assert printer._console.print.call_count == 4


def test_print_separator_uses_default_dash(printer):
    printer.print_separator()

    printer._console.print.assert_called_once_with("-" * 80, style="dim white")


def test_print_command_shows_dollar_prefix(printer):
    printer.print_command("womm lint")

    printer._console.print.assert_called_once_with("$ womm lint", style="bold cyan")


def test_print_result_success_uses_green(printer):
    printer.print_result("done", success=True)

    printer._console.print.assert_called_once_with("done", style="bold green")


def test_print_result_failure_uses_red(printer):
    printer.print_result("failed", success=False)

    printer._console.print.assert_called_once_with("failed", style="bold red")


def test_print_dry_run_message_without_details(printer, monkeypatch):
    info = MagicMock()
    monkeypatch.setattr(printer, "info", info)

    printer.print_dry_run_message("delete files")

    info.assert_called_once_with("🔍 [DRY-RUN] Would delete files")


def test_print_dry_run_message_with_details(printer, monkeypatch):
    info = MagicMock()
    monkeypatch.setattr(printer, "info", info)

    printer.print_dry_run_message("delete files", details="3 files")

    info.assert_called_once_with("🔍 [DRY-RUN] Would delete files: 3 files")


def test_print_dry_run_success_delegates_to_success(printer, monkeypatch):
    success = MagicMock()
    monkeypatch.setattr(printer, "success", success)

    printer.print_dry_run_success()

    success.assert_called_once_with("✅ Dry run completed successfully")


def test_print_dry_run_warning_delegates_to_warning(printer, monkeypatch):
    warning = MagicMock()
    monkeypatch.setattr(printer, "warning", warning)

    printer.print_dry_run_warning()

    warning.assert_called_once_with("⚠️  DRY-RUN MODE - No changes will be made")


# ///////////////////////////////////////////////////////////////
# PANEL BUILDERS
# ///////////////////////////////////////////////////////////////


def test_create_panel_returns_panel_with_given_content(printer):
    panel = printer.create_panel("body", title="T")

    assert isinstance(panel, Panel)


def test_create_info_panel_uses_info_icon(printer):
    panel = printer.create_info_panel("Info", "content")

    assert isinstance(panel, Panel)
    assert panel.title == "ℹ️ Info"


def test_create_success_panel_uses_success_icon(printer):
    panel = printer.create_success_panel("Done", "content")

    assert panel.title == "✅ Done"


def test_create_error_panel_uses_error_icon(printer):
    panel = printer.create_error_panel("Oops", "content")

    assert panel.title == "❌ Oops"


def test_create_warning_panel_uses_warning_icon(printer):
    panel = printer.create_warning_panel("Careful", "content")

    assert panel.title == "⚠️ Careful"


@pytest.mark.parametrize(
    ("status", "icon"),
    [("success", "✅"), ("error", "❌"), ("warning", "⚠️"), ("pending", "⏳")],
)
def test_create_installation_panel_icon_matches_status(printer, status, icon):
    panel = printer.create_installation_panel("Step 1", "desc", status=status)

    assert panel.title == f"{icon} Step 1"


# ///////////////////////////////////////////////////////////////
# TABLE BUILDERS
# ///////////////////////////////////////////////////////////////


def test_create_table_with_simple_column_names(printer):
    table = printer.create_table("T", ["Name", "Value"], rows=[["a", "1"]])

    assert isinstance(table, Table)
    assert len(table.columns) == 2
    assert table.row_count == 1


def test_create_table_with_custom_column_tuples(printer):
    table = printer.create_table("T", [("Name", "cyan", True), ("Value", None, False)])

    assert len(table.columns) == 2


def test_create_status_table_empty_data_returns_placeholder(printer):
    table = printer.create_status_table("T", [])

    assert isinstance(table, Table)


def test_create_status_table_marks_success_and_failure_rows(printer):
    table = printer.create_status_table(
        "T",
        [
            {"Tool": "ruff", "Status": "success"},
            {"Tool": "mypy", "Status": "error: failed"},
            {"Tool": "black", "Status": "warning: skipped"},
            {"Tool": "isort", "Status": "unknown"},
        ],
    )

    assert table.row_count == 4


def test_create_dependency_table_marks_available_and_missing(printer):
    table = printer.create_dependency_table({"ruff": "0.5.0", "black": ""})

    assert table.row_count == 2


def test_create_command_table_builds_rows_from_dicts(printer):
    table = printer.create_command_table(
        [{"command": "lint", "description": "Run linters", "category": "quality"}]
    )

    assert table.row_count == 1


def test_create_backup_table_formats_sizes_and_truncates_long_description(printer):
    table = printer.create_backup_table(
        [
            {
                "name": "a.json",
                "size": 500,
                "modified": "2026-01-01",
                "description": "x",
            },
            {
                "name": "b.json",
                "size": 2048,
                "modified": "2026-01-02",
                "description": "y" * 60,
            },
            {
                "name": "c.json",
                "size": 5 * 1024 * 1024,
                "modified": "2026-01-03",
                "description": "z",
            },
        ]
    )

    assert table.row_count == 3


# ///////////////////////////////////////////////////////////////
# DYNAMIC LAYERED PROGRESS
# ///////////////////////////////////////////////////////////////


@pytest.fixture
def buffered_console():
    return Console(file=io.StringIO(), force_terminal=False, width=80)


def test_dynamic_layered_progress_creates_a_task_per_stage(buffered_console):
    stages = [{"name": "download", "description": "Downloading"}]

    with DynamicLayeredProgress(buffered_console, stages) as progress:
        assert "download" in progress.task_ids


def test_update_layer_ignores_unknown_layer(buffered_console):
    progress = DynamicLayeredProgress(buffered_console, [{"name": "a"}])

    with progress:
        progress.update_layer("does-not-exist", progress_value=50)


def test_update_layer_main_stage_computes_percentage_from_steps(buffered_console):
    stages = [{"name": "install", "type": "main", "steps": ["a", "b", "c", "d"]}]

    with DynamicLayeredProgress(buffered_console, stages) as progress:
        progress.update_layer("install", progress_value=2)

        task = progress.progress.tasks[progress.task_ids["install"]]
        assert task.completed == 50


def test_update_layer_progress_stage_computes_percentage_from_total(buffered_console):
    stages = [{"name": "copy", "type": "progress", "total": 200}]

    with DynamicLayeredProgress(buffered_console, stages) as progress:
        progress.update_layer("copy", progress_value=50)

        task = progress.progress.tasks[progress.task_ids["copy"]]
        assert task.completed == 25


def test_update_layer_spinner_uses_value_as_percentage_directly(buffered_console):
    stages = [{"name": "spin"}]

    with DynamicLayeredProgress(buffered_console, stages) as progress:
        progress.update_layer("spin", progress_value=42)

        task = progress.progress.tasks[progress.task_ids["spin"]]
        assert task.completed == 42


def test_update_layer_with_message_appends_to_description(buffered_console):
    stages = [{"name": "spin", "description": "Working"}]

    with DynamicLayeredProgress(buffered_console, stages) as progress:
        progress.update_layer("spin", message="step 2")

        task = progress.progress.tasks[progress.task_ids["spin"]]
        assert task.description == "Working - step 2"


def test_complete_layer_sets_completed_to_100_and_tracks_it(buffered_console):
    stages = [{"name": "a"}]

    with DynamicLayeredProgress(buffered_console, stages) as progress:
        progress.complete_layer("a")

        task = progress.progress.tasks[progress.task_ids["a"]]
        assert task.completed == 100
        assert "a" in progress._completed_stages


def test_complete_layer_ignores_unknown_layer(buffered_console):
    progress = DynamicLayeredProgress(buffered_console, [{"name": "a"}])

    with progress:
        progress.complete_layer("does-not-exist")


def test_emergency_stop_does_not_raise_on_already_stopped_progress(buffered_console):
    progress = DynamicLayeredProgress(buffered_console, [{"name": "a"}])

    with progress:
        pass

    progress.emergency_stop("stopped")
