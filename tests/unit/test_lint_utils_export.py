#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST LINT UTILS EXPORT - JSON export coverage
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Direct tests for exporting lint tool results to JSON files."""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Standard library imports
import json
from pathlib import Path

# Local imports
from womm.shared.results.lint_results import ToolResult
from womm.utils.lint import export_lint_results_to_json

# ///////////////////////////////////////////////////////////////
# EXPORT LINT RESULTS TO JSON
# ///////////////////////////////////////////////////////////////


def test_export_lint_results_to_json_creates_output_directory(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "reports" / "lint"

    exported = export_lint_results_to_json({}, output_dir)

    assert exported == []
    assert output_dir.is_dir()


def test_export_lint_results_to_json_writes_one_file_per_tool(
    tmp_path: Path,
) -> None:
    results = {
        "ruff": ToolResult(
            success=True,
            message="clean",
            tool_name="ruff",
            files_checked=5,
            issues_found=0,
        ),
        "isort": ToolResult(
            success=False,
            message="issues found",
            tool_name="isort",
            files_checked=5,
            issues_found=2,
        ),
    }

    exported = export_lint_results_to_json(results, tmp_path)

    assert len(exported) == 2
    names = {path.name.split("_")[0] for path in exported}
    assert names == {"ruff", "isort"}
    for path in exported:
        assert path.is_file()


def test_export_lint_results_to_json_writes_expected_payload(
    tmp_path: Path,
) -> None:
    result = ToolResult(
        success=True,
        message="ok",
        tool_name="ruff",
        files_checked=3,
        issues_found=1,
        fixed_issues=1,
        data={"detail": "value"},
    )

    exported = export_lint_results_to_json({"ruff": result}, tmp_path, mode="fix")

    payload = json.loads(exported[0].read_text(encoding="utf-8"))
    assert payload["tool"] == "ruff"
    assert payload["mode"] == "fix"
    assert payload["success"] is True
    assert payload["files_checked"] == 3
    assert payload["issues_found"] == 1
    assert payload["fixed_issues"] == 1
    assert payload["message"] == "ok"
    assert payload["data"] == {"detail": "value"}
    assert payload["raw_result"]["tool_name"] == "ruff"
    assert "ruff_fix_" in exported[0].name
