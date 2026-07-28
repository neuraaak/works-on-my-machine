#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST SECURITY VALIDATION UTILS - Pure security predicates
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""
Tests for the stateless security predicate functions.

All pure functions over ``SecurityPatternsConfig``'s static patterns —
no mocking, no I/O beyond ``Path.resolve()`` on real ``tmp_path`` paths.
"""

from __future__ import annotations

# ///////////////////////////////////////////////////////////////
# IMPORTS
# ///////////////////////////////////////////////////////////////
# Local imports
from womm.utils.security.security_validation_utils import (
    has_dangerous_command_patterns,
    has_dangerous_file_patterns,
    has_excessive_traversal,
    is_dangerous_argument,
    is_system_directory,
    validate_chmod_permissions,
    validate_chown_owner,
    validate_permission_command,
)

# ///////////////////////////////////////////////////////////////
# DANGEROUS COMMAND PATTERNS
# ///////////////////////////////////////////////////////////////


def test_has_dangerous_command_patterns_detects_rm_rf():
    assert has_dangerous_command_patterns("rm -rf /") is True


def test_has_dangerous_command_patterns_is_case_insensitive():
    assert has_dangerous_command_patterns("RM -RF /") is True


def test_has_dangerous_command_patterns_clean_command_is_safe():
    assert has_dangerous_command_patterns("ls -la") is False


# ///////////////////////////////////////////////////////////////
# DANGEROUS ARGUMENTS
# ///////////////////////////////////////////////////////////////


def test_is_dangerous_argument_matches_known_dangerous_flag():
    assert is_dangerous_argument("rm", "-rf") is True


def test_is_dangerous_argument_matches_shell_injection_pattern():
    assert is_dangerous_argument("echo", "hello; rm -rf /") is True


def test_is_dangerous_argument_safe_argument_for_safe_command():
    assert is_dangerous_argument("echo", "hello world") is False


# ///////////////////////////////////////////////////////////////
# CHMOD / CHOWN VALIDATION
# ///////////////////////////////////////////////////////////////


def test_validate_chmod_permissions_accepts_allowed_pattern():
    assert validate_chmod_permissions("644") is True


def test_validate_chmod_permissions_rejects_non_matching_string():
    assert validate_chmod_permissions("not-a-permission") is False


def test_validate_chown_owner_accepts_allowed_pattern():
    assert validate_chown_owner("user") is True


def test_validate_chown_owner_rejects_non_matching_string():
    assert validate_chown_owner("!!!invalid!!!") is False


# ///////////////////////////////////////////////////////////////
# PERMISSION COMMAND VALIDATION
# ///////////////////////////////////////////////////////////////


def test_validate_permission_command_too_short_is_invalid():
    assert validate_permission_command(["chmod"]) is False


def test_validate_permission_command_chmod_delegates_to_chmod_validation():
    assert validate_permission_command(["chmod", "644"]) is True
    assert validate_permission_command(["chmod", "not-a-permission"]) is False


def test_validate_permission_command_chown_delegates_to_chown_validation():
    assert validate_permission_command(["chown", "user"]) is True


def test_validate_permission_command_unknown_base_command_is_invalid():
    assert validate_permission_command(["touch", "file.txt"]) is False


# ///////////////////////////////////////////////////////////////
# DANGEROUS FILE PATTERNS
# ///////////////////////////////////////////////////////////////


def test_has_dangerous_file_patterns_detects_ssh_key_path():
    assert has_dangerous_file_patterns("~/.ssh/id_rsa") is True


def test_has_dangerous_file_patterns_clean_path_is_safe():
    assert has_dangerous_file_patterns("project/src/main.py") is False


# ///////////////////////////////////////////////////////////////
# EXCESSIVE TRAVERSAL
# ///////////////////////////////////////////////////////////////


def test_has_excessive_traversal_no_dots_is_safe():
    assert has_excessive_traversal("project/src/main.py") is False


def test_has_excessive_traversal_within_default_limit_is_safe():
    assert has_excessive_traversal("../../file.txt") is False


def test_has_excessive_traversal_beyond_default_limit_is_excessive():
    assert has_excessive_traversal("../../../../file.txt") is True


def test_has_excessive_traversal_respects_custom_limit():
    assert has_excessive_traversal("../../file.txt", max_traversal=1) is True


# ///////////////////////////////////////////////////////////////
# SYSTEM DIRECTORY DETECTION
# ///////////////////////////////////////////////////////////////


def test_is_system_directory_true_for_known_unix_path(monkeypatch):
    from pathlib import Path

    monkeypatch.setattr(Path, "resolve", lambda _self: Path("/etc/passwd"))

    assert is_system_directory(Path("/etc/passwd")) is True


def test_is_system_directory_false_for_regular_project_path(tmp_path):
    assert is_system_directory(tmp_path / "myproject") is False


def test_is_system_directory_conservative_on_resolution_failure(monkeypatch):
    from pathlib import Path

    def _boom(_self):
        raise OSError("cannot resolve")

    monkeypatch.setattr(Path, "resolve", _boom)

    assert is_system_directory(Path("whatever")) is True
