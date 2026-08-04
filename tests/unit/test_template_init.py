"""Tests for the template scaffolding command."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from womm.commands.project.template import template_group
from womm.interfaces.project.template_store_interface import (
    TemplateStoreInterface,
)
from womm.services.project.template_store_service import TemplateStoreService


@pytest.fixture(autouse=True)
def isolated_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WOMM_HOME", str(tmp_path / "home"))


def test_init_creates_a_template_skeleton(tmp_path: Path):
    destination = tmp_path / "my-template"

    result = TemplateStoreInterface().init_template(
        destination,
        answers={"template_name": "my-template"},
        force=False,
        defaults=True,
    )

    assert result.success is True
    assert (destination / "copier.yml").is_file()
    assert (destination / "template").is_dir()
    assert (destination / "README.md").is_file()


def test_generated_skeleton_is_a_valid_template(tmp_path: Path):
    destination = tmp_path / "my-template"
    TemplateStoreInterface().init_template(
        destination,
        answers={"template_name": "my-template"},
        force=False,
        defaults=True,
    )

    entry = TemplateStoreService().add("mine", destination)

    assert entry.qualified_id == "user/mine"


def test_init_refuses_a_non_empty_destination(tmp_path: Path):
    destination = tmp_path / "busy"
    destination.mkdir()
    (destination / "x.txt").write_text("x", encoding="utf-8")

    result = TemplateStoreInterface().init_template(
        destination, answers={}, force=False, defaults=True
    )

    assert result.success is False
    assert "--force" in result.error


def test_init_command_scaffolds(tmp_path: Path):
    destination = tmp_path / "cli-template"

    result = CliRunner().invoke(
        template_group, ["init", str(destination), "--defaults"]
    )

    assert result.exit_code == 0
    assert (destination / "copier.yml").is_file()
