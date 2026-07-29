#!/usr/bin/env python3
# ///////////////////////////////////////////////////////////////
# TEST SHARED RUNTIME - Executable Resolution
# Project: Works On My Machine
# ///////////////////////////////////////////////////////////////

"""Tests for the command path consumed by external integrations."""

from __future__ import annotations

# Standard library imports
from pathlib import Path

# Local imports
from womm.shared import runtime


def test_get_womm_executable_prefers_the_uv_shim(monkeypatch, tmp_path: Path) -> None:
    shim = tmp_path / ".local" / "bin" / "womm.exe"
    shim.parent.mkdir(parents=True)
    shim.write_text("entrypoint", encoding="utf-8")
    monkeypatch.setattr(runtime.Path, "home", lambda: tmp_path)
    monkeypatch.setattr(runtime.sys, "platform", "win32")
    monkeypatch.setattr(runtime.shutil, "which", lambda _name: None)

    assert runtime.get_womm_executable() == shim


def test_get_womm_executable_falls_back_to_path_lookup(
    monkeypatch, tmp_path: Path
) -> None:
    executable = tmp_path / "bin" / "womm"
    executable.parent.mkdir()
    executable.write_text("entrypoint", encoding="utf-8")
    monkeypatch.setattr(runtime.Path, "home", lambda: tmp_path / "home")
    monkeypatch.setattr(runtime.sys, "platform", "linux")
    monkeypatch.setattr(runtime.shutil, "which", lambda _name: str(executable))

    assert runtime.get_womm_executable() == executable
