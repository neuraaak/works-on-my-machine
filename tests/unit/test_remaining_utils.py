from pathlib import Path

import pytest

from womm.utils.project import core_utils, file_utils
from womm.utils.womm_setup import installer_utils


def test_project_core_detects_and_creates_structure(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").touch()
    assert core_utils.categorize_directory(tmp_path) == "python"
    assert core_utils.matches_project_type({"python": ["pyproject.toml"]}, "python")
    created = core_utils.create_python_structure(tmp_path / "new", "demo")
    assert len(created) >= 4
    assert (tmp_path / "new" / "src").is_dir()
    assert len(core_utils.create_python_requirements_files(tmp_path / "new")) == 2
    assert len(core_utils.create_javascript_config_files(tmp_path / "new")) == 2


@pytest.mark.parametrize(
    "project_type, expected",
    [
        ("node", Path("src/main.js")),
        ("react", Path("src/App.jsx")),
        ("vue", Path("src/App.vue")),
    ],
)
def test_project_file_creators_write_expected_entrypoints(
    tmp_path: Path, project_type: str, expected: str
) -> None:
    created = file_utils.create_javascript_source_files(tmp_path, "demo", project_type)
    assert str(expected) in created
    assert (tmp_path / expected).is_file()


def test_python_file_creators_write_package_and_test(tmp_path: Path) -> None:
    assert str(Path("src/my_demo/main.py")) in file_utils.create_python_main_files(
        tmp_path, "my-demo"
    )
    (tmp_path / "tests").mkdir()
    assert file_utils.create_python_test_file(tmp_path, "my-demo") == [
        str(Path("tests/test_my_demo.py"))
    ]


def test_installer_patterns_copy_verification_and_proof(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    (source / "keep.py").write_text("x")
    (source / "ignore_test.py").write_text("x")
    assert installer_utils.check_default_patterns(source / "ignore_test.py", source)
    assert not installer_utils.should_exclude_file(source / "keep.py", source)
    assert set(installer_utils.get_files_to_copy(source)) == {
        "keep.py",
        "ignore_test.py",
    }
    target = tmp_path / "target"
    target.mkdir()
    (target / "keep.py").write_text("x")
    assert installer_utils.verify_files_copied(source, target, ["keep.py"])["success"]
    (target / "womm").mkdir()
    proof = installer_utils.create_installation_proof(target)
    proof_file = proof["proof_file"]
    assert isinstance(proof_file, str)
    assert Path(proof_file).is_file()
