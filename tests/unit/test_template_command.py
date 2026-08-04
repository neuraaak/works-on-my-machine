"""Tests for the template command surface."""

from pathlib import Path

import pytest
from click.testing import CliRunner

from womm.commands.project.template import template_group


@pytest.fixture(autouse=True)
def isolated_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("WOMM_HOME", str(tmp_path / "home"))
    return tmp_path


def test_list_shows_official_templates():
    result = CliRunner().invoke(template_group, ["list"])

    assert result.exit_code == 0
    assert "python" in result.output


def test_show_displays_one_template():
    result = CliRunner().invoke(template_group, ["show", "official/python"])

    assert result.exit_code == 0
    assert "python" in result.output


def test_show_unknown_template_exits_non_zero():
    result = CliRunner().invoke(template_group, ["show", "nope"])

    assert result.exit_code != 0


def test_add_registers_a_local_template(tmp_path: Path):
    source = tmp_path / "mine"
    source.mkdir()
    (source / "copier.yml").write_text("project_name:\n  type: str\n", encoding="utf-8")

    added = CliRunner().invoke(template_group, ["add", "mine", str(source)])
    listed = CliRunner().invoke(template_group, ["list"])

    assert added.exit_code == 0
    assert "mine" in listed.output


def test_add_url_exits_non_zero():
    result = CliRunner().invoke(
        template_group, ["add", "remote", "https://github.com/acme/tpl.git"]
    )

    assert result.exit_code != 0
    assert "not supported yet" in result.output
