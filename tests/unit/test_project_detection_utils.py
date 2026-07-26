#!/usr/bin/env python3
"""Unit tests for pure project-variant detection utilities."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from womm.utils.project.variant_detection_utils import VariantDetectionUtils


@pytest.mark.parametrize(
    ("dependencies", "has_tsconfig", "expected"),
    [
        ({}, False, "js"),
        ({}, True, "ts"),
        ({"react": "19.0.0"}, False, "react"),
        ({"react-dom": "19.0.0"}, True, "react-ts"),
        ({"vue": "3.0.0"}, False, "vue"),
        ({"vue": "3.0.0"}, True, "vue-ts"),
    ],
)
def test_detect_javascript_variant_from_dependencies(
    tmp_path: Path,
    dependencies: dict[str, str],
    has_tsconfig: bool,
    expected: str,
) -> None:
    (tmp_path / "package.json").write_text(
        json.dumps({"dependencies": dependencies}), encoding="utf-8"
    )
    if has_tsconfig:
        (tmp_path / "tsconfig.json").write_text("{}", encoding="utf-8")

    assert VariantDetectionUtils.detect_variant(tmp_path, "javascript") == expected


def test_detect_javascript_variant_reads_dev_dependencies(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text(
        json.dumps({"devDependencies": {"react": "19.0.0"}}), encoding="utf-8"
    )

    assert VariantDetectionUtils.detect_variant(tmp_path, "javascript") == "react"


@pytest.mark.parametrize("package_json", ["{", "[]", '{"dependencies": []}'])
def test_detect_javascript_variant_defaults_for_invalid_package_json(
    tmp_path: Path, package_json: str
) -> None:
    (tmp_path / "package.json").write_text(package_json, encoding="utf-8")

    assert VariantDetectionUtils.detect_variant(tmp_path, "javascript") == "js"


@pytest.mark.parametrize(
    ("marker", "content"),
    [
        ("manage.py", ""),
        ("pyproject.toml", '[project]\ndependencies = ["Django>=5"]\n'),
        ("requirements.txt", "Django==5.1\n"),
    ],
)
def test_detect_python_variant_from_django_markers(
    tmp_path: Path, marker: str, content: str
) -> None:
    (tmp_path / marker).write_text(content, encoding="utf-8")

    assert VariantDetectionUtils.detect_variant(tmp_path, "python") == "django"


def test_detect_python_variant_defaults_without_django_marker(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("flask==3.0\n", encoding="utf-8")

    assert VariantDetectionUtils.detect_variant(tmp_path, "python") == "py"


def test_user_variant_overrides_auto_detection(tmp_path: Path) -> None:
    (tmp_path / "manage.py").touch()

    assert (
        VariantDetectionUtils.detect_variant(tmp_path, "python", user_variant="py")
        == "py"
    )


@pytest.mark.parametrize(
    ("language", "user_variant", "message"),
    [
        ("rust", "stable", "Unsupported language"),
        ("python", "react", "not supported"),
        ("rust", None, "Auto-detection not supported"),
    ],
)
def test_detect_variant_rejects_unsupported_inputs(
    tmp_path: Path, language: str, user_variant: str | None, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        VariantDetectionUtils.detect_variant(tmp_path, language, user_variant)
