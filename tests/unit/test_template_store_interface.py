"""Tests for the template store interface."""

from pathlib import Path

import pytest

from womm.interfaces.project.template_store_interface import (
    TemplateStoreInterface,
)


@pytest.fixture(autouse=True)
def isolated_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    home = tmp_path / "home"
    monkeypatch.setenv("WOMM_HOME", str(home))
    return home


@pytest.fixture
def local_template(tmp_path: Path) -> Path:
    root = tmp_path / "mine"
    root.mkdir()
    (root / "copier.yml").write_text("project_name:\n  type: str\n", encoding="utf-8")
    return root


def test_list_returns_official_templates():
    result = TemplateStoreInterface().list_templates()

    assert result.success is True
    assert result.entries
    assert {"official/python", "official/javascript"} <= {
        entry.qualified_id for entry in result.entries
    }


def test_show_returns_a_single_entry():
    result = TemplateStoreInterface().show_template("official/python")

    assert result.success is True
    assert result.entry is not None
    assert result.entry.id == "python"


def test_show_unknown_template_fails_without_raising():
    result = TemplateStoreInterface().show_template("nope")

    assert result.success is False
    assert "nope" in result.error


def test_add_then_remove_round_trip(local_template: Path):
    interface = TemplateStoreInterface()

    added = interface.add_template("mine", local_template)
    assert added.success is True

    removed = interface.remove_template("mine")
    assert removed.success is True
    assert interface.show_template("user/mine").success is False


def test_add_url_fails_without_raising():
    result = TemplateStoreInterface().add_template(
        "remote", Path("https://github.com/acme/tpl.git")
    )

    assert result.success is False
    assert "not supported yet" in result.error


def test_update_points_at_a_new_source(local_template: Path, tmp_path: Path):
    interface = TemplateStoreInterface()
    interface.add_template("mine", local_template)
    moved = tmp_path / "moved"
    moved.mkdir()
    (moved / "copier.yml").write_text("project_name:\n  type: str\n", encoding="utf-8")

    result = interface.update_template("mine", moved)

    assert result.success is True
    assert result.entry is not None
    assert result.entry.source == moved
