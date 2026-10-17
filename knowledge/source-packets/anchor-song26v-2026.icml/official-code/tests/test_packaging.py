"""Tests for distribution metadata and importable package boundaries."""

import ast
from pathlib import Path

import pytest

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python 3.8-3.10 compatibility
    import tomli as tomllib


EXPECTED_PACKAGES = {
    "ablation",
    "auditor_agent",
    "auditor_model_training",
    "baselines",
    "evaluation_judges",
    "mcp_tools",
    "pipeline_statistics",
    "task_construction",
    "toolbox_expansion",
    "trajectory_generation",
}


def test_pyproject_declares_distribution_and_build_backend(repo_root: Path) -> None:
    config = tomllib.loads((repo_root / "pyproject.toml").read_text())
    assert config["project"]["name"] == "anchor-safety-eval"
    assert config["build-system"]["build-backend"] == "setuptools.build_meta"
    assert config["project"]["requires-python"] == ">=3.10"


def test_pyproject_declares_core_and_optional_dependencies(repo_root: Path) -> None:
    project = tomllib.loads((repo_root / "pyproject.toml").read_text())["project"]
    dependencies = " ".join(project["dependencies"])
    for dependency in ["beautifulsoup4", "openai", "pexpect", "requests", "tqdm"]:
        assert dependency in dependencies
    assert set(project["optional-dependencies"]) == {
        "mcp",
        "taxonomy",
        "training",
        "dev",
    }


@pytest.mark.parametrize("package", sorted(EXPECTED_PACKAGES))
def test_top_level_packages_have_init_files(repo_root: Path, package: str) -> None:
    init_file = repo_root / package / "__init__.py"
    assert init_file.is_file()
    ast.parse(init_file.read_text())


def test_all_tracked_python_files_parse(repo_root: Path) -> None:
    excluded = {".git", ".agents", ".venv", "build", "dist"}
    python_files = [
        path
        for path in repo_root.rglob("*.py")
        if not excluded.intersection(path.parts)
    ]
    assert python_files
    failures = []
    for path in python_files:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, UnicodeDecodeError) as error:
            failures.append(f"{path.relative_to(repo_root)}: {error}")
    assert not failures, "\n".join(failures)


@pytest.mark.integration
def test_package_imports_work_outside_repository(repo_root: Path, tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend(str(repo_root))
    for package in EXPECTED_PACKAGES:
        __import__(package)


def test_pytest_configuration_points_to_tests(repo_root: Path) -> None:
    config = tomllib.loads((repo_root / "pyproject.toml").read_text())
    pytest_config = config["tool"]["pytest"]["ini_options"]
    assert pytest_config["testpaths"] == ["tests"]
    assert "--strict-config" in pytest_config["addopts"]
