#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST LINT DISPLAY - Renderer and pure-helper coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for the lint UI renderers.

``_format_size``/``_truncate_message`` are pure and asserted directly.
The rest is branching on ``LintSummaryResult``/``ToolStatusResult`` state;
``ezprinter``/``ezconsole`` are patched to assert on the calls made rather
than on any real terminal output.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
from unittest.mock import MagicMock

# Local imports
from womm.shared.results import LintSummaryResult, ToolResult
from womm.shared.results.lint_results import ToolStatusResult
from womm.ui.lint import display as display_module

# ///////////////////////////////////////////////////////////////
# FIXTURES
# ///////////////////////////////////////////////////////////////


def _patch_ui(monkeypatch):
    ezprinter = MagicMock()
    ezconsole = MagicMock()
    monkeypatch.setattr(display_module, "ezprinter", ezprinter)
    monkeypatch.setattr(display_module, "ezconsole", ezconsole)
    return ezprinter, ezconsole


# ///////////////////////////////////////////////////////////////
# PURE HELPERS
# ///////////////////////////////////////////////////////////////


def test_format_size_bytes():
    assert display_module._format_size(512) == "512 B"


def test_format_size_kilobytes():
    assert display_module._format_size(2048) == "2.0 KB"


def test_format_size_megabytes():
    assert display_module._format_size(5 * 1024 * 1024) == "5.0 MB"


def test_truncate_message_empty_returns_empty_string():
    assert display_module._truncate_message("") == ""


def test_truncate_message_short_message_is_unchanged():
    assert display_module._truncate_message("short") == "short"


def test_truncate_message_long_message_is_truncated_with_ellipsis():
    message = "x" * 60
    result = display_module._truncate_message(message, max_length=50)
    assert result == "x" * 47 + "..."
    assert len(result) == 50


def test_truncate_message_collapses_newlines():
    result = display_module._truncate_message("line one\nline two", max_length=50)
    assert result == "line one line two"


# ///////////////////////////////////////////////////////////////
# RENDER LINT SUMMARY RESULT
# ///////////////////////////////////////////////////////////////


def test_render_lint_summary_result_without_tool_results_reports_error(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    summary = LintSummaryResult(success=False, error="no files found")

    display_module.render_lint_summary_result(summary)

    ezprinter.error.assert_called_once_with("no files found")


def test_render_lint_summary_result_with_tool_results_displays_summary(monkeypatch):
    ezprinter, ezconsole = _patch_ui(monkeypatch)
    tool_result = ToolResult(
        success=True, tool_name="ruff", files_checked=3, issues_found=0
    )
    summary = LintSummaryResult(
        success=True,
        total_files=3,
        total_issues=0,
        tool_results={"ruff": tool_result},
    )

    display_module.render_lint_summary_result(summary)

    ezprinter.error.assert_not_called()
    ezconsole.print.assert_called()
    ezprinter.success.assert_called_once_with(
        "✨ All checks passed! 3 files are clean."
    )


# ///////////////////////////////////////////////////////////////
# RENDER TOOL STATUS RESULT
# ///////////////////////////////////////////////////////////////


def test_render_tool_status_result_failure_reports_error(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    result = ToolStatusResult(success=False, error="ruff not installed")

    display_module.render_tool_status_result(result)

    ezprinter.error.assert_called_once_with("ruff not installed")


def test_render_tool_status_result_success_displays_table(monkeypatch):
    ezprinter, ezconsole = _patch_ui(monkeypatch)
    result = ToolStatusResult(success=True, tool_summary={"ruff": "0.5.0"})

    display_module.render_tool_status_result(result)

    ezprinter.error.assert_not_called()
    ezconsole.print.assert_called_once()


# ///////////////////////////////////////////////////////////////
# DISPLAY TOOL RESULTS (CHECK VS FIX MODE)
# ///////////////////////////////////////////////////////////////


def test_display_tool_results_empty_warns(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)

    display_module._display_tool_results({}, mode="check")

    ezprinter.warning.assert_called_once_with("No tool results to display")


def test_display_tool_results_check_mode_prints_table(monkeypatch):
    _, ezconsole = _patch_ui(monkeypatch)
    tool_results = {
        "ruff": ToolResult(
            success=False, tool_name="ruff", files_checked=2, issues_found=4
        )
    }

    display_module._display_tool_results(tool_results, mode="check")

    ezconsole.print.assert_called_once()


def test_display_tool_results_fix_mode_prints_table(monkeypatch):
    _, ezconsole = _patch_ui(monkeypatch)
    tool_results = {
        "ruff": ToolResult(
            success=True, tool_name="ruff", files_checked=2, fixed_issues=3
        )
    }

    display_module._display_tool_results(tool_results, mode="fix")

    ezconsole.print.assert_called_once()


# ///////////////////////////////////////////////////////////////
# DISPLAY OVERALL SUMMARY
# ///////////////////////////////////////////////////////////////


def test_display_overall_summary_check_success_no_issues(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    summary = LintSummaryResult(success=True, total_files=5, total_issues=0)

    display_module._display_overall_summary(summary, mode="check")

    ezprinter.success.assert_called_once_with(
        "✨ All checks passed! 5 files are clean."
    )


def test_display_overall_summary_check_success_with_issues(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    summary = LintSummaryResult(success=True, total_files=5, total_issues=2)

    display_module._display_overall_summary(summary, mode="check")

    ezprinter.warning.assert_called_once_with("⚠️  Found 2 issues across 5 files.")


def test_display_overall_summary_check_failure_shows_tip(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    summary = LintSummaryResult(success=False, total_files=5, total_issues=2)

    display_module._display_overall_summary(summary, mode="check")

    ezprinter.tip.assert_called_once()


def test_display_overall_summary_fix_success_with_fixes(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    summary = LintSummaryResult(success=True, total_files=5, total_fixed=3)

    display_module._display_overall_summary(summary, mode="fix")

    ezprinter.success.assert_called_once_with("✨ Fixed 3 issues across 5 files!")


def test_display_overall_summary_fix_success_no_fixes(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    summary = LintSummaryResult(success=True, total_files=5, total_fixed=0)

    display_module._display_overall_summary(summary, mode="fix")

    ezprinter.info.assert_called_once_with("✅ No issues to fix in 5 files.")


def test_display_overall_summary_fix_failure_shows_tip(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    summary = LintSummaryResult(success=False, total_files=5)

    display_module._display_overall_summary(summary, mode="fix")

    ezprinter.tip.assert_called_once()


# ///////////////////////////////////////////////////////////////
# DISPLAY SCAN INFO
# ///////////////////////////////////////////////////////////////


def test_display_scan_info_without_extensions(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)

    display_module._display_scan_info(
        {"total_files": 4, "total_size": 100, "directories": {"a", "b"}}
    )

    ezprinter.info.assert_called_once()


def test_display_scan_info_with_extensions(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)

    display_module._display_scan_info(
        {
            "total_files": 4,
            "total_size": 100,
            "directories": {"a"},
            "extensions": {".py": 3, ".md": 1},
        }
    )

    assert ezprinter.info.call_count == 2


# ///////////////////////////////////////////////////////////////
# DISPLAY LINT SUMMARY (INTEGRATION OF THE ABOVE)
# ///////////////////////////////////////////////////////////////


def test_display_lint_summary_renders_scan_info_when_present(monkeypatch):
    ezprinter, _ = _patch_ui(monkeypatch)
    summary = LintSummaryResult(
        success=True,
        total_files=1,
        scan_summary={"total_files": 1, "total_size": 10, "directories": {"a"}},
    )

    display_module.display_lint_summary(summary)

    assert ezprinter.info.called


# ///////////////////////////////////////////////////////////////
# DISPLAY TOOL STATUS
# ///////////////////////////////////////////////////////////////


def test_display_tool_status_marks_available_and_missing_tools(monkeypatch):
    _, ezconsole = _patch_ui(monkeypatch)

    display_module.display_tool_status({"ruff": "0.5.0", "black": "not available"})

    ezconsole.print.assert_called_once()
