#!/usr/bin/env python3
"""Unit tests for pure security and file-scanning utilities."""

from __future__ import annotations

from pathlib import Path

import pytest

from womm.utils.common.file_scanner_utils import (
    contains_security_sensitive_pattern,
    is_python_file,
    should_exclude_path,
)
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


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        ("python -m pytest", False),
        ("rm -rf build", True),
        ("shutdown /s", True),
    ],
)
def test_has_dangerous_command_patterns(command: str, expected: bool) -> None:
    assert has_dangerous_command_patterns(command) is expected


@pytest.mark.parametrize(
    ("command", "argument", "expected"),
    [
        ("rm", "-rf", True),
        ("python", "script.py; shutdown /s", True),
        ("python", "script.py", False),
    ],
)
def test_is_dangerous_argument(command: str, argument: str, expected: bool) -> None:
    assert is_dangerous_argument(command, argument) is expected


@pytest.mark.parametrize(
    ("permissions", "expected"),
    [("755", True), ("u+x", True), ("888", False), ("755; rm -rf /", False)],
)
def test_validate_chmod_permissions(permissions: str, expected: bool) -> None:
    assert validate_chmod_permissions(permissions) is expected


@pytest.mark.parametrize(
    ("owner", "expected"),
    [("developer", True), ("developer:staff", True), ("root;whoami", False)],
)
def test_validate_chown_owner(owner: str, expected: bool) -> None:
    assert validate_chown_owner(owner) is expected


@pytest.mark.parametrize(
    ("command", "expected"),
    [
        (["chmod", "644", "file.txt"], True),
        (["chown", "developer:staff", "file.txt"], True),
        (["chmod", "888", "file.txt"], False),
        (["git", "status"], False),
        (["chmod"], False),
    ],
)
def test_validate_permission_command(command: list[str], expected: bool) -> None:
    assert validate_permission_command(command) is expected


@pytest.mark.parametrize(
    ("file_path", "expected"),
    [
        ("src/main.py", False),
        ("../../etc/passwd", True),
        ("~/.ssh/id_rsa", True),
    ],
)
def test_has_dangerous_file_patterns(file_path: str, expected: bool) -> None:
    assert has_dangerous_file_patterns(file_path) is expected


@pytest.mark.parametrize(
    ("file_path", "max_traversal", "expected"),
    [("../../module", 2, False), ("../../../module", 2, True), ("../module", 0, True)],
)
def test_has_excessive_traversal(
    file_path: str, max_traversal: int, expected: bool
) -> None:
    assert has_excessive_traversal(file_path, max_traversal) is expected


def test_is_system_directory_rejects_temporary_project_path(tmp_path: Path) -> None:
    assert not is_system_directory(tmp_path)


def test_is_python_file_requires_existing_regular_python_file(tmp_path: Path) -> None:
    python_file = tmp_path / "module.PY"
    python_file.write_text("print('ok')", encoding="utf-8")
    package_stub = tmp_path / "types.pyi"
    package_stub.write_text("value: int", encoding="utf-8")

    assert is_python_file(python_file)
    assert is_python_file(package_stub)
    assert not is_python_file(tmp_path / "missing.py")
    assert not is_python_file(tmp_path)


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        (Path("src/module.py"), False),
        (Path(".git/config"), True),
        (Path("project/node_modules/package.json"), True),
    ],
)
def test_should_exclude_path(path: Path, expected: bool) -> None:
    assert should_exclude_path(path) is expected


@pytest.mark.parametrize(
    ("file_path", "expected"),
    [
        (Path("src/main.py"), False),
        (Path("config/secret_token.txt"), True),
        ("credentials.json", True),
    ],
)
def test_contains_security_sensitive_pattern(
    file_path: Path | str, expected: bool
) -> None:
    assert contains_security_sensitive_pattern(file_path) is expected
