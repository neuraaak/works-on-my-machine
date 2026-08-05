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
    assert manifest["type"] == "module"
    assert "vitest" in manifest["devDependencies"]
    assert "@biomejs/biome" in manifest["devDependencies"]
    assert (out / "biome.json").is_file()
    assert (out / ".vscode" / "settings.json").is_file()
    assert not (out / ".eslintrc.json").exists()
    assert not (out / "eslint.config.mjs").exists()
    assert not (out / "prettier.config.mjs").exists()
    assert not (out / ".prettierignore").exists()
    assert not (out / "index.html").exists()
    assert not (out / "vite.config.mjs").exists()
    assert not (out / "tsconfig.json").exists()


def test_typescript_adds_a_tsconfig(tmp_path: Path):
    out = render(tmp_path / "p", typescript=True)

    json.loads((out / "tsconfig.json").read_text(encoding="utf-8"))


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
    assert (out / "index.html").is_file() is (framework != "none")
    assert (out / "vite.config.mjs").is_file() is (framework != "none")


@pytest.mark.parametrize("manager", ["npm", "pnpm", "yarn", "bun"])
def test_each_package_manager_renders(tmp_path: Path, manager: str):
    out = render(tmp_path / manager, package_manager=manager)

    assert (out / "package.json").is_file()


def test_bun_readme_uses_explicit_run_for_the_test_script(tmp_path: Path):
    out = render(tmp_path / "p", package_manager="bun")

    readme = (out / "README.md").read_text(encoding="utf-8")
    assert "bun run test" in readme
    assert "bun test\n" not in readme


def test_tests_can_be_disabled(tmp_path: Path):
    out = render(tmp_path / "p", with_tests=False)

    assert not (out / "tests").exists()


def test_vscode_files_can_be_disabled(tmp_path: Path):
    out = render(tmp_path / "p", with_vscode=False)

    assert not (out / ".vscode").exists()
    assert ".vscode/" in (out / ".gitignore").read_text(encoding="utf-8")


def test_rendered_package_json_is_valid_json(tmp_path: Path):
    out = render(tmp_path / "p", framework="react", typescript=True)

    json.loads((out / "package.json").read_text(encoding="utf-8"))


def test_react_uses_vite_instead_of_react_scripts(tmp_path: Path):
    out = render(tmp_path / "p", framework="react")

    manifest = json.loads((out / "package.json").read_text(encoding="utf-8"))
    assert "vite" in manifest["devDependencies"]
    assert "@vitejs/plugin-react" in manifest["devDependencies"]
    assert "react-scripts" not in manifest["devDependencies"]


def test_vue_uses_vite_instead_of_vue_cli(tmp_path: Path):
    out = render(tmp_path / "p", framework="vue")

    manifest = json.loads((out / "package.json").read_text(encoding="utf-8"))
    assert "vite" in manifest["devDependencies"]
    assert "@vitejs/plugin-vue" in manifest["devDependencies"]
    assert "@vue/cli-service" not in manifest["devDependencies"]


def test_vscode_settings_are_modernized(tmp_path: Path):
    out = render(tmp_path / "p")

    settings = json.loads(
        (out / ".vscode" / "settings.json").read_text(encoding="utf-8")
    )
    assert "eslint.useFlatConfig" not in settings
    assert settings["editor.rulers"] == [100]
    assert settings["search.exclude"]["**/node_modules"] is True
    assert settings["search.exclude"]["**/dist"] is True
    assert settings["search.exclude"]["**/coverage"] is True


def test_vscode_recommends_vitest_extension_when_tests_enabled(tmp_path: Path):
    out = render(tmp_path / "p", with_tests=True)

    extensions = json.loads(
        (out / ".vscode" / "extensions.json").read_text(encoding="utf-8")
    )
    assert "vitest.explorer" in extensions["recommendations"]


def test_vscode_does_not_recommend_vitest_extension_when_tests_disabled(
    tmp_path: Path,
):
    out = render(tmp_path / "p", with_tests=False)

    extensions = json.loads(
        (out / ".vscode" / "extensions.json").read_text(encoding="utf-8")
    )
    assert "vitest.explorer" not in extensions["recommendations"]


@pytest.mark.parametrize("manager", ["pnpm", "yarn", "bun"])
def test_package_json_pins_a_package_manager_for_corepack(tmp_path: Path, manager: str):
    out = render(tmp_path / manager, package_manager=manager)

    manifest = json.loads((out / "package.json").read_text(encoding="utf-8"))
    assert manifest["packageManager"].startswith(f"{manager}@")


def test_package_json_has_no_package_manager_pin_for_npm(tmp_path: Path):
    out = render(tmp_path / "p", package_manager="npm")

    manifest = json.loads((out / "package.json").read_text(encoding="utf-8"))
    assert "packageManager" not in manifest


@pytest.mark.parametrize("framework", ["none", "react"])
def test_biome_is_used_for_non_vue_frameworks(tmp_path: Path, framework: str):
    out = render(tmp_path / framework, framework=framework)

    assert (out / "biome.json").is_file()
    assert not (out / "eslint.config.mjs").exists()
    assert not (out / "prettier.config.mjs").exists()

    manifest = json.loads((out / "package.json").read_text(encoding="utf-8"))
    assert "@biomejs/biome" in manifest["devDependencies"]
    assert "eslint" not in manifest["devDependencies"]
    assert "prettier" not in manifest["devDependencies"]
    assert manifest["scripts"]["lint"] == "biome lint ."
    assert manifest["scripts"]["format"] == "biome format --write ."


def test_eslint_and_prettier_are_kept_for_vue(tmp_path: Path):
    out = render(tmp_path / "p", framework="vue")

    assert (out / "eslint.config.mjs").is_file()
    assert (out / "prettier.config.mjs").is_file()
    assert not (out / "biome.json").exists()

    manifest = json.loads((out / "package.json").read_text(encoding="utf-8"))
    assert "@biomejs/biome" not in manifest["devDependencies"]
    assert "eslint" in manifest["devDependencies"]
    assert manifest["scripts"]["lint"] == "eslint ."


def test_vscode_recommends_biome_extension_for_non_vue(tmp_path: Path):
    out = render(tmp_path / "p", framework="react")

    extensions = json.loads(
        (out / ".vscode" / "extensions.json").read_text(encoding="utf-8")
    )
    assert "biomejs.biome" in extensions["recommendations"]
    assert "dbaeumer.vscode-eslint" not in extensions["recommendations"]
    assert "esbenp.prettier-vscode" not in extensions["recommendations"]

    settings = json.loads(
        (out / ".vscode" / "settings.json").read_text(encoding="utf-8")
    )
    assert settings["editor.defaultFormatter"] == "biomejs.biome"


def test_vscode_recommends_eslint_and_prettier_for_vue(tmp_path: Path):
    out = render(tmp_path / "p", framework="vue")

    extensions = json.loads(
        (out / ".vscode" / "extensions.json").read_text(encoding="utf-8")
    )
    assert "biomejs.biome" not in extensions["recommendations"]
    assert "dbaeumer.vscode-eslint" in extensions["recommendations"]
    assert "esbenp.prettier-vscode" in extensions["recommendations"]

    settings = json.loads(
        (out / ".vscode" / "settings.json").read_text(encoding="utf-8")
    )
    assert settings["editor.defaultFormatter"] == "esbenp.prettier-vscode"
