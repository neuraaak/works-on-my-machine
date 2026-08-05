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
    assert (out / ".pre-commit-config.yaml").is_file()
    assert (out / ".vscode" / "settings.json").is_file()


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


def test_vscode_files_can_be_disabled(tmp_path: Path):
    out = render(tmp_path / "p", with_vscode=False)

    assert not (out / ".vscode").exists()
    assert ".vscode/" in (out / ".gitignore").read_text(encoding="utf-8")


def test_vscode_settings_use_ruff_and_ty(tmp_path: Path):
    import json

    out = render(tmp_path / "p")

    extensions = json.loads(
        (out / ".vscode" / "extensions.json").read_text(encoding="utf-8")
    )
    assert "charliermarsh.ruff" in extensions["recommendations"]
    assert "astral-sh.ty" in extensions["recommendations"]
    assert not any(
        rec.startswith("ms-python.mypy") for rec in extensions["recommendations"]
    )

    settings = json.loads(
        (out / ".vscode" / "settings.json").read_text(encoding="utf-8")
    )
    assert settings["python.analysis.typeCheckingMode"] == "off"
    assert "**/.mypy_cache" not in settings["files.exclude"]
    assert settings["files.exclude"]["**/.ruff_cache"] is True
    assert settings["python.testing.pytestEnabled"] is True


def test_vscode_pytest_discovery_disabled_when_tests_disabled(tmp_path: Path):
    import json

    out = render(tmp_path / "p", with_tests=False)

    settings = json.loads(
        (out / ".vscode" / "settings.json").read_text(encoding="utf-8")
    )
    assert settings["python.testing.pytestEnabled"] is False


def test_vscode_recommends_django_extension_for_django_framework(tmp_path: Path):
    import json

    out = render(tmp_path / "p", framework="django")

    extensions = json.loads(
        (out / ".vscode" / "extensions.json").read_text(encoding="utf-8")
    )
    assert "batisteo.vscode-django" in extensions["recommendations"]


def test_pre_commit_uses_the_project_quality_toolchain(tmp_path: Path):
    out = render(tmp_path / "p")

    config = (out / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "ruff check --fix" in config
    assert "ruff format" in config
    assert "ty check" in config
    assert "black" not in config
    assert "flake8" not in config
    assert "isort" not in config


@pytest.mark.parametrize("license_id", ["MIT", "Apache-2.0", "proprietary"])
def test_each_license_renders(tmp_path: Path, license_id: str):
    out = render(tmp_path / license_id, license=license_id)

    assert (out / "pyproject.toml").is_file()


def test_rendered_pyproject_is_parseable(tmp_path: Path):
    import tomllib

    out = render(tmp_path / "p")
    data = tomllib.loads((out / "pyproject.toml").read_text(encoding="utf-8"))

    assert data["project"]["name"] == "acme-tool"


def test_framework_none_renders_no_django_file(tmp_path: Path):
    out = render(tmp_path / "p")

    assert not (out / "manage.py").exists()
    assert not (out / "src" / "acme_tool" / "settings.py").exists()

    data = (out / "pyproject.toml").read_text(encoding="utf-8")
    assert "django" not in data.lower()


@pytest.mark.parametrize("use_src_layout", [True, False])
def test_django_framework_renders_a_working_project(
    tmp_path: Path, use_src_layout: bool
):
    out = render(
        tmp_path / f"django-{use_src_layout}",
        framework="django",
        use_src_layout=use_src_layout,
    )

    package_dir = out / "src" / "acme_tool" if use_src_layout else out / "acme_tool"

    assert (out / "manage.py").is_file()
    assert (package_dir / "settings.py").is_file()
    assert (package_dir / "urls.py").is_file()
    assert (package_dir / "wsgi.py").is_file()
    assert (package_dir / "asgi.py").is_file()
    assert (package_dir / "core" / "__init__.py").is_file()
    assert (package_dir / "core" / "apps.py").is_file()
    assert (package_dir / "core" / "views.py").is_file()

    settings = (package_dir / "settings.py").read_text(encoding="utf-8")
    assert 'ROOT_URLCONF = "acme_tool.urls"' in settings

    import tomllib

    data = tomllib.loads((out / "pyproject.toml").read_text(encoding="utf-8"))
    assert any(dep.startswith("django") for dep in data["project"]["dependencies"])
    dev_deps = data["dependency-groups"]["dev"]
    assert any(dep.startswith("pytest-django") for dep in dev_deps)
    assert any(dep.startswith("django-stubs") for dep in dev_deps)


def test_django_ci_workflow_runs_manage_py_check(tmp_path: Path):
    out = render(tmp_path / "p", framework="django")

    workflow = (out / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "python manage.py check" in workflow


def test_django_pytest_ini_declares_settings_module(tmp_path: Path):
    out = render(tmp_path / "p", framework="django")

    data = (out / "pyproject.toml").read_text(encoding="utf-8")
    assert 'DJANGO_SETTINGS_MODULE = "acme_tool.settings"' in data


def test_uv_workflow_uses_uv_commands(tmp_path: Path):
    out = render(tmp_path / "p", framework="django")

    readme = (out / "README.md").read_text(encoding="utf-8")
    assert "uv sync --group dev" in readme
    assert "uv run pytest" in readme
    assert "uv run ruff check ." in readme
    assert "uv run ty check ." in readme
    assert "pip install" not in readme

    workflow = (out / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "astral-sh/setup-uv" in workflow
    assert "uv sync --group dev" in workflow
    assert "uv run ruff check ." in workflow
    assert "uv run ty check ." in workflow
    assert "uv run pytest" in workflow
    assert "uv run python manage.py check" in workflow
    assert "pip install" not in workflow

    precommit = (out / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "entry: uv run ruff check --fix" in precommit
    assert "entry: uv run ruff format" in precommit
    assert "entry: uv run ty check" in precommit


def test_pip_workflow_used_when_uv_disabled(tmp_path: Path):
    out = render(tmp_path / "p", framework="django", use_uv=False)

    readme = (out / "README.md").read_text(encoding="utf-8")
    assert "pip install -e . --group dev" in readme
    assert "uv" not in readme.lower()

    workflow = (out / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "astral-sh/setup-uv" not in workflow
    assert "pip install -e . --group dev" in workflow
    assert "ruff check ." in workflow
    assert "python manage.py check" in workflow
    assert "uv run" not in workflow

    precommit = (out / ".pre-commit-config.yaml").read_text(encoding="utf-8")
    assert "entry: ruff check --fix" in precommit
    assert "entry: uv run" not in precommit
