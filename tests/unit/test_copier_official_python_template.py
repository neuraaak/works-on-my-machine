"""Generation matrix for the official Python template."""

from pathlib import Path

import pytest

from womm.services.project.copier_project_creation_service import (
    CopierProjectCreationService,
    ProjectCreationRequest,
)
from womm.services.project.template_store_service import TemplateStoreService

BASE_ANSWERS = {
    "project_name": "acme-tool",
    "package_name": "acme_tool",
    "description": "A demo project",
    "author_name": "Tester",
}


def render(destination: Path, **overrides: object) -> Path:
    """Render the official Python template with merged answers."""
    source = TemplateStoreService().resolve("official/python").source
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

    assert (out / "pyproject.toml").is_file()
    assert (out / "README.md").is_file()
    assert (out / "src" / "acme_tool" / "__init__.py").is_file()
    assert (out / "tests").is_dir()


def test_flat_layout_places_the_package_at_the_root(tmp_path: Path):
    out = render(tmp_path / "p", use_src_layout=False)

    assert (out / "acme_tool" / "__init__.py").is_file()
    assert not (out / "src").exists()


def test_tests_can_be_disabled(tmp_path: Path):
    out = render(tmp_path / "p", with_tests=False)

    assert not (out / "tests").exists()


def test_ci_can_be_disabled(tmp_path: Path):
    out = render(tmp_path / "p", with_ci=False)

    assert not (out / ".github").exists()


def test_django_framework_is_rendered(tmp_path: Path):
    out = render(tmp_path / "p", framework="django")

    assert "django" in (out / "pyproject.toml").read_text(encoding="utf-8").lower()


@pytest.mark.parametrize("license_id", ["MIT", "Apache-2.0", "proprietary"])
def test_each_license_renders(tmp_path: Path, license_id: str):
    out = render(tmp_path / license_id, license=license_id)

    assert (out / "pyproject.toml").is_file()


def test_rendered_pyproject_is_parseable(tmp_path: Path):
    import tomllib

    out = render(tmp_path / "p")
    data = tomllib.loads((out / "pyproject.toml").read_text(encoding="utf-8"))

    assert data["project"]["name"] == "acme-tool"
