"""Unit tests for the custom-python-wheel accelerator."""

from __future__ import annotations

from pathlib import Path


def test_get_custom_python_wheel_accelerator():
    from dpa.accelerators import get_accelerator

    cls = get_accelerator("custom-python-wheel")
    assert cls is not None
    assert cls.name == "custom-python-wheel"


def test_custom_python_wheel_list_files():
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("custom-python-wheel")()
    files = [str(f).replace("\\", "/") for f in acc.list_files()]

    assert "databricks.yml" in files
    assert "pyproject.toml" in files
    assert "resources/jobs/wheel_job.yml" in files
    assert "notebooks/build_and_upload.py" in files
    assert "notebooks/verify_imports.py" in files
    assert "src/custom_python_wheel/__init__.py" in files
    assert "src/custom_python_wheel/functions.py" in files


def test_custom_python_wheel_scaffold(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("custom-python-wheel")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    assert (project_dir / "databricks.yml").exists()
    assert (project_dir / "pyproject.toml").exists()
    assert (project_dir / "resources" / "jobs" / "wheel_job.yml").exists()
    assert (project_dir / "notebooks" / "build_and_upload.py").exists()
    assert (project_dir / "notebooks" / "verify_imports.py").exists()
    assert (project_dir / "src" / "custom_python_wheel" / "__init__.py").exists()
    assert (project_dir / "src" / "custom_python_wheel" / "functions.py").exists()


def test_custom_python_wheel_scaffold_renders_pyproject(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("custom-python-wheel")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    pyproject = (project_dir / "pyproject.toml").read_text()
    assert 'name = "custom-python-wheel"' in pyproject
    assert 'packages = ["src/custom_python_wheel"]' in pyproject


def test_custom_python_wheel_scaffold_renders_build_notebook(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("custom-python-wheel")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    nb = (project_dir / "notebooks" / "build_and_upload.py").read_text()
    assert "# Databricks notebook source" in nb
    assert "pip wheel" in nb
    assert "shutil.copy" in nb
    assert "workspace_file_path" in nb


def test_custom_python_wheel_scaffold_renders_verify_notebook(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("custom-python-wheel")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    nb = (project_dir / "notebooks" / "verify_imports.py").read_text()
    assert "# Databricks notebook source" in nb
    assert "from custom_python_wheel import add, greet" in nb
    assert "restartPython" in nb
    assert "Hello, Databricks!" in nb
