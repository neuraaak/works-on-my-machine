"""Generation matrix for the official JavaScript template."""

import json
from pathlib import Path

import pytest

from womm.services.project.copier_project_creation_service import (
    CopierProjectCreationService,
    ProjectCreationRequest,
)
from womm.services.project.template_store_service import TemplateStoreService

BASE_ANSWERS = {
    "project_name": "acme-app",
    "description": "A demo app",
    "author_name": "Tester",
}


def render(destination: Path, **overrides: object) -> Path:
    """Render the official JavaScript template with merged answers."""
    source = TemplateStoreService().resolve("official/javascript").source
    CopierProjectCreationService().create(
        ProjectCreationRequest(
            template_source=source,
            destination=destination,
            answers={**BASE_ANSWERS, **overrides},
            defaults=True,
        )
    )
    return destination


def test_defaults_produce_a_coherent_project(tmp_path: Path):
    out = render(tmp_path / "p")

    manifest = json.loads((out / "package.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "acme-app"
    assert not (out / "tsconfig.json").exists()


def test_typescript_adds_a_tsconfig(tmp_path: Path):
    out = render(tmp_path / "p", typescript=True)

    assert (out / "tsconfig.json").is_file()


@pytest.mark.parametrize("framework", ["none", "react", "vue"])
@pytest.mark.parametrize("typescript", [False, True])
def test_every_framework_renders_in_both_language_modes(
    tmp_path: Path, framework: str, typescript: bool
):
    out = render(
        tmp_path / f"{framework}-{typescript}",
        framework=framework,
        typescript=typescript,
    )

    manifest = json.loads((out / "package.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "acme-app"
    assert (out / "tsconfig.json").is_file() is typescript


@pytest.mark.parametrize("manager", ["npm", "pnpm", "yarn"])
def test_each_package_manager_renders(tmp_path: Path, manager: str):
    out = render(tmp_path / manager, package_manager=manager)

    assert (out / "package.json").is_file()


def test_tests_can_be_disabled(tmp_path: Path):
    out = render(tmp_path / "p", with_tests=False)

    assert not (out / "tests").exists()


def test_rendered_package_json_is_valid_json(tmp_path: Path):
    out = render(tmp_path / "p", framework="react", typescript=True)

    json.loads((out / "package.json").read_text(encoding="utf-8"))
