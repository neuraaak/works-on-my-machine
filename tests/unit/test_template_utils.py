#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST TEMPLATE UTILS - Placeholder replacement and validation
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for the template placeholder utilities.

``replace_platform_placeholders`` is exercised against the real
platform-detection helpers (no mocking — the substituted values vary by OS,
so assertions only check placeholder removal and extra-var injection, not
literal platform strings). The file-touching functions run against real
files under ``tmp_path``.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Third-party imports
import pytest

# Local imports
from womm.utils.project.template_utils import (
    generate_cross_platform_template,
    replace_platform_placeholders,
    validate_template_placeholders,
)

# ///////////////////////////////////////////////////////////////
# REPLACE PLATFORM PLACEHOLDERS
# ///////////////////////////////////////////////////////////////


def test_replace_platform_placeholders_empty_text_returns_as_is():
    assert replace_platform_placeholders("") == ""


def test_replace_platform_placeholders_replaces_platform_system():
    result = replace_platform_placeholders("System: {{PLATFORM_SYSTEM}}")

    assert "{{PLATFORM_SYSTEM}}" not in result


def test_replace_platform_placeholders_replaces_python_path():
    result = replace_platform_placeholders("Python: {{PYTHON_PATH}}")

    assert "{{PYTHON_PATH}}" not in result


def test_replace_platform_placeholders_injects_extra_vars():
    result = replace_platform_placeholders(
        "Hello {{PROJECT_NAME}}!", PROJECT_NAME="MyApp"
    )

    assert result == "Hello MyApp!"


def test_replace_platform_placeholders_leaves_unknown_placeholder_untouched():
    result = replace_platform_placeholders("{{UNKNOWN_PLACEHOLDER}}")

    assert result == "{{UNKNOWN_PLACEHOLDER}}"


# ///////////////////////////////////////////////////////////////
# VALIDATE TEMPLATE PLACEHOLDERS
# ///////////////////////////////////////////////////////////////


def test_validate_template_placeholders_none_path_raises():
    with pytest.raises(ValueError, match="cannot be None"):
        validate_template_placeholders(None)


def test_validate_template_placeholders_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        validate_template_placeholders(tmp_path / "missing.tmpl")


def test_validate_template_placeholders_directory_raises(tmp_path):
    with pytest.raises(IsADirectoryError):
        validate_template_placeholders(tmp_path)


def test_validate_template_placeholders_all_supported(tmp_path):
    template = tmp_path / "template.txt"
    template.write_text("Hello {{PROJECT_NAME}}, run on {{PLATFORM_SYSTEM}}")

    result = validate_template_placeholders(template)

    assert result["is_valid"] is True
    assert result["total_placeholders"] == 2
    assert set(result["supported_placeholders"]) == {
        "PROJECT_NAME",
        "PLATFORM_SYSTEM",
    }
    assert result["unsupported_placeholders"] == []


def test_validate_template_placeholders_detects_unsupported(tmp_path):
    template = tmp_path / "template.txt"
    template.write_text("{{PROJECT_NAME}} and {{NOT_A_REAL_PLACEHOLDER}}")

    result = validate_template_placeholders(template)

    assert result["is_valid"] is False
    assert "NOT_A_REAL_PLACEHOLDER" in result["unsupported_placeholders"]


def test_validate_template_placeholders_no_placeholders_is_valid(tmp_path):
    template = tmp_path / "template.txt"
    template.write_text("Plain text, nothing to replace here.")

    result = validate_template_placeholders(template)

    assert result["total_placeholders"] == 0
    assert result["is_valid"] is True


# ///////////////////////////////////////////////////////////////
# GENERATE CROSS PLATFORM TEMPLATE
# ///////////////////////////////////////////////////////////////


def test_generate_cross_platform_template_none_template_path_raises(tmp_path):
    with pytest.raises(ValueError, match="Template path cannot be None"):
        generate_cross_platform_template(None, tmp_path / "out.txt")


def test_generate_cross_platform_template_missing_template_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        generate_cross_platform_template(
            tmp_path / "missing.tmpl", tmp_path / "out.txt"
        )


def test_generate_cross_platform_template_directory_as_template_raises(tmp_path):
    with pytest.raises(IsADirectoryError):
        generate_cross_platform_template(tmp_path, tmp_path / "out.txt")


def test_generate_cross_platform_template_none_output_path_raises(tmp_path):
    template = tmp_path / "template.txt"
    template.write_text("content")

    with pytest.raises(ValueError, match="Output path cannot be None"):
        generate_cross_platform_template(template, None)


def test_generate_cross_platform_template_writes_substituted_output(tmp_path):
    template = tmp_path / "template.txt"
    template.write_text("Hello {{PROJECT_NAME}}!")
    output = tmp_path / "nested" / "out.txt"

    generate_cross_platform_template(
        template, output, template_vars={"PROJECT_NAME": "MyApp"}
    )

    assert output.read_text(encoding="utf-8") == "Hello MyApp!"


def test_generate_cross_platform_template_creates_output_directory(tmp_path):
    template = tmp_path / "template.txt"
    template.write_text("static content")
    output = tmp_path / "a" / "b" / "c" / "out.txt"

    generate_cross_platform_template(template, output)

    assert output.exists()
