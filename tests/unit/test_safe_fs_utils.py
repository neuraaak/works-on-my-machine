#!/usr/bin/env python3
"""Regression tests for guarded filesystem deletion and path traversal."""

from __future__ import annotations

from pathlib import Path

import pytest

from womm.utils.common import safe_fs_utils
from womm.utils.security.security_validation_utils import has_excessive_traversal


class TestSafeRmtree:
    """Verify every guard executes before a directory is removed."""

    def test_removes_directory_inside_allowed_parent(self, tmp_path: Path) -> None:
        target = tmp_path / "allowed" / "target"
        target.mkdir(parents=True)
        (target / "file.txt").write_text("content", encoding="utf-8")

        safe_fs_utils.safe_rmtree(target, allowed_parent=tmp_path / "allowed")

        assert not target.exists()

    def test_rejects_missing_path(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            safe_fs_utils.safe_rmtree(tmp_path / "missing", allowed_parent=tmp_path)

    def test_rejects_file(self, tmp_path: Path) -> None:
        target = tmp_path / "file.txt"
        target.write_text("content", encoding="utf-8")

        with pytest.raises(NotADirectoryError):
            safe_fs_utils.safe_rmtree(target, allowed_parent=tmp_path)

        assert target.exists()

    def test_rejects_parent_traversal_outside_boundary(self, tmp_path: Path) -> None:
        allowed_parent = tmp_path / "allowed"
        allowed_parent.mkdir()
        outside_target = tmp_path / "outside"
        outside_target.mkdir()
        escaped_path = allowed_parent / ".." / outside_target.name

        with pytest.raises(ValueError, match="outside allowed boundary"):
            safe_fs_utils.safe_rmtree(escaped_path, allowed_parent=allowed_parent)

        assert outside_target.exists()

    def test_rejects_symlink_escaping_allowed_parent(self, tmp_path: Path) -> None:
        allowed_parent = tmp_path / "allowed"
        allowed_parent.mkdir()
        outside_target = tmp_path / "outside"
        outside_target.mkdir()
        link = allowed_parent / "escape"

        try:
            link.symlink_to(outside_target, target_is_directory=True)
        except OSError as error:
            pytest.skip(f"Symlinks unavailable in this environment: {error}")

        with pytest.raises(ValueError, match="outside allowed boundary"):
            safe_fs_utils.safe_rmtree(link, allowed_parent=allowed_parent)

        assert outside_target.exists()

    def test_rejects_critical_path_before_removal(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        target = tmp_path / "target"
        target.mkdir()
        monkeypatch.setattr(
            safe_fs_utils, "_get_critical_paths", lambda: {target.resolve()}
        )

        with pytest.raises(ValueError, match="critical system path"):
            safe_fs_utils.safe_rmtree(target, allowed_parent=tmp_path)

        assert target.exists()


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("project/src", False),
        ("../project", False),
        ("../../project", False),
        ("../../../project", True),
    ],
)
def test_has_excessive_traversal(path: str, expected: bool) -> None:
    """Allow at most two parent traversals in a user-supplied path."""
    assert has_excessive_traversal(path) is expected
