#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST BASE VALIDATION SERVICE - Generic validation patterns
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for ``BaseValidationService``.

Pure static methods (no singleton, no service state) operating on real
paths under ``tmp_path`` and plain Python values — no mocking needed.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from womm.services.common.base_validation_service import BaseValidationService

# ///////////////////////////////////////////////////////////////
# PATH EXISTS
# ///////////////////////////////////////////////////////////////


def test_validate_path_exists_missing_path_fails(tmp_path):
    result = BaseValidationService.validate_path_exists(tmp_path / "missing.txt")

    assert not result.success
    assert "does not exist" in result.error


def test_validate_path_exists_file_type_mismatch_fails(tmp_path):
    directory = tmp_path / "adir"
    directory.mkdir()

    result = BaseValidationService.validate_path_exists(directory, path_type="file")

    assert not result.success
    assert "not a file" in result.error


def test_validate_path_exists_directory_type_mismatch_fails(tmp_path):
    file_path = tmp_path / "afile.txt"
    file_path.write_text("data")

    result = BaseValidationService.validate_path_exists(
        file_path, path_type="directory"
    )

    assert not result.success
    assert "not a directory" in result.error


def test_validate_path_exists_any_type_accepts_file(tmp_path):
    file_path = tmp_path / "afile.txt"
    file_path.write_text("data")

    result = BaseValidationService.validate_path_exists(file_path, path_type="any")

    assert result.success


def test_validate_path_exists_invalid_path_type_returns_error(monkeypatch, tmp_path):
    def boom(_self):
        raise OSError("disk error")

    monkeypatch.setattr("pathlib.Path.exists", boom)

    result = BaseValidationService.validate_path_exists(tmp_path)

    assert not result.success
    assert "Error validating path" in result.error


# ///////////////////////////////////////////////////////////////
# PATH READABLE
# ///////////////////////////////////////////////////////////////


def test_validate_path_readable_missing_path_fails(tmp_path):
    result = BaseValidationService.validate_path_readable(tmp_path / "missing.txt")

    assert not result.success
    assert "does not exist" in result.error


def test_validate_path_readable_directory_fails(tmp_path):
    result = BaseValidationService.validate_path_readable(tmp_path)

    assert not result.success
    assert "not a file" in result.error


def test_validate_path_readable_file_succeeds(tmp_path):
    file_path = tmp_path / "afile.txt"
    file_path.write_text("data")

    result = BaseValidationService.validate_path_readable(file_path)

    assert result.success


# ///////////////////////////////////////////////////////////////
# PATH WRITABLE
# ///////////////////////////////////////////////////////////////


def test_validate_path_writable_missing_parent_fails(tmp_path):
    result = BaseValidationService.validate_path_writable(
        tmp_path / "missing_dir" / "afile.txt"
    )

    assert not result.success
    assert "does not exist" in result.error


def test_validate_path_writable_nonexistent_file_target_fails(tmp_path):
    # BUG (base_validation_service.py:166): for a target that doesn't exist yet,
    # `is_file()` is False so `parent` resolves to the target itself instead of
    # its containing directory, and the writability check fails even though the
    # real parent directory exists and is writable. Documented here, not fixed.
    result = BaseValidationService.validate_path_writable(tmp_path / "afile.txt")

    assert not result.success
    assert "Parent directory does not exist" in result.error


def test_validate_path_writable_existing_file_checks_its_directory(tmp_path):
    file_path = tmp_path / "afile.txt"
    file_path.write_text("data")

    result = BaseValidationService.validate_path_writable(file_path)

    assert result.success


def test_validate_path_writable_directory_target_uses_itself_as_parent(tmp_path):
    result = BaseValidationService.validate_path_writable(tmp_path)

    assert result.success


# ///////////////////////////////////////////////////////////////
# NON-EMPTY STRING
# ///////////////////////////////////////////////////////////////


def test_validate_non_empty_string_rejects_non_string():
    result = BaseValidationService.validate_non_empty_string(123, field_name="age")

    assert not result.success
    assert "must be a string" in result.error


def test_validate_non_empty_string_rejects_whitespace_only():
    result = BaseValidationService.validate_non_empty_string("   ")

    assert not result.success
    assert "cannot be empty" in result.error


def test_validate_non_empty_string_accepts_value():
    result = BaseValidationService.validate_non_empty_string("hello")

    assert result.success


# ///////////////////////////////////////////////////////////////
# STRING PATTERN
# ///////////////////////////////////////////////////////////////


def test_validate_string_pattern_matches():
    result = BaseValidationService.validate_string_pattern("abc123", r"^[a-z0-9]+$")

    assert result.success


def test_validate_string_pattern_does_not_match():
    result = BaseValidationService.validate_string_pattern(
        "ABC", r"^[a-z]+$", field_name="slug"
    )

    assert not result.success
    assert "slug does not match required pattern" in result.error


def test_validate_string_pattern_invalid_regex_reports_error():
    result = BaseValidationService.validate_string_pattern("abc", r"[", field_name="x")

    assert not result.success
    assert "Error validating x" in result.error


# ///////////////////////////////////////////////////////////////
# DICT STRUCTURE
# ///////////////////////////////////////////////////////////////


def test_validate_dict_structure_rejects_non_dict():
    result = BaseValidationService.validate_dict_structure("not a dict", ["a"])

    assert not result.success
    assert "must be a dictionary" in result.error


def test_validate_dict_structure_reports_missing_keys():
    result = BaseValidationService.validate_dict_structure(
        {"a": 1}, ["a", "b", "c"], field_name="config"
    )

    assert not result.success
    assert "Missing required keys in config: b, c" in result.error


def test_validate_dict_structure_accepts_complete_dict():
    result = BaseValidationService.validate_dict_structure({"a": 1, "b": 2}, ["a", "b"])

    assert result.success


# ///////////////////////////////////////////////////////////////
# DICT VALUE TYPES
# ///////////////////////////////////////////////////////////////


def test_validate_dict_value_types_rejects_non_dict():
    result = BaseValidationService.validate_dict_value_types("nope", {"a": str})

    assert not result.success
    assert "must be a dictionary" in result.error


def test_validate_dict_value_types_reports_type_mismatch():
    result = BaseValidationService.validate_dict_value_types(
        {"age": "twelve"}, {"age": int}, field_name="profile"
    )

    assert not result.success
    assert "Field 'age' in profile has type str, expected int" in result.error


def test_validate_dict_value_types_ignores_missing_optional_keys():
    result = BaseValidationService.validate_dict_value_types(
        {"name": "Ada"}, {"name": str, "age": int}
    )

    assert result.success


def test_validate_dict_value_types_accepts_matching_types():
    result = BaseValidationService.validate_dict_value_types(
        {"name": "Ada", "age": 36}, {"name": str, "age": int}
    )

    assert result.success


# ///////////////////////////////////////////////////////////////
# VALUE IN RANGE
# ///////////////////////////////////////////////////////////////


def test_validate_value_in_range_below_minimum_fails():
    result = BaseValidationService.validate_value_in_range(1, 5, 10, field_name="port")

    assert not result.success
    assert "port must be >= 5, got 1" in result.error


def test_validate_value_in_range_above_maximum_fails():
    result = BaseValidationService.validate_value_in_range(20, 5, 10, field_name="port")

    assert not result.success
    assert "port must be <= 10, got 20" in result.error


def test_validate_value_in_range_within_bounds_succeeds():
    result = BaseValidationService.validate_value_in_range(7, 5, 10)

    assert result.success


def test_validate_value_in_range_no_bounds_always_succeeds():
    result = BaseValidationService.validate_value_in_range(-999, None, None)

    assert result.success


# ///////////////////////////////////////////////////////////////
# VALUE IN LIST
# ///////////////////////////////////////////////////////////////


def test_validate_value_in_list_rejects_unknown_value():
    result = BaseValidationService.validate_value_in_list(
        "cyan", ["red", "green", "blue"], field_name="color"
    )

    assert not result.success
    assert "color must be one of" in result.error


def test_validate_value_in_list_accepts_known_value():
    result = BaseValidationService.validate_value_in_list("red", ["red", "green"])

    assert result.success


# ///////////////////////////////////////////////////////////////
# VALIDATE ALL / ANY
# ///////////////////////////////////////////////////////////////


def test_validate_all_succeeds_when_every_validation_passes():
    from womm.shared.results import ValidationResult

    result = BaseValidationService.validate_all(
        [ValidationResult(success=True), ValidationResult(success=True)]
    )

    assert result.success


def test_validate_all_combines_error_messages_from_failures():
    from womm.shared.results import ValidationResult

    result = BaseValidationService.validate_all(
        [
            ValidationResult(success=False, error="first error"),
            ValidationResult(success=True),
            ValidationResult(success=False, error="second error"),
        ]
    )

    assert not result.success
    assert result.error == "first error\nsecond error"


def test_validate_any_succeeds_when_one_validation_passes():
    from womm.shared.results import ValidationResult

    result = BaseValidationService.validate_any(
        [
            ValidationResult(success=False, error="nope"),
            ValidationResult(success=True),
        ]
    )

    assert result.success


def test_validate_any_fails_when_all_validations_fail():
    from womm.shared.results import ValidationResult

    result = BaseValidationService.validate_any(
        [
            ValidationResult(success=False, error="first"),
            ValidationResult(success=False, error="second"),
        ]
    )

    assert not result.success
    assert result.error == "first OR second"
