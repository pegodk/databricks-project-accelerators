"""Unit tests for the mlflow-project accelerator."""

from __future__ import annotations

from pathlib import Path


def test_get_mlflow_project_accelerator():
    from dpa.accelerators import get_accelerator

    cls = get_accelerator("mlflow-project")
    assert cls is not None
    assert cls.name == "mlflow-project"


def test_mlflow_project_list_files():
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("mlflow-project")()
    files = [str(f).replace("\\", "/") for f in acc.list_files()]

    assert "databricks.yml" in files
    assert "resources/jobs/mlflow_job.yml" in files
    assert "resources/schemas/schema.yml" in files
    assert "notebooks/train.py" in files
    assert "notebooks/register.py" in files
    assert "notebooks/score.py" in files


def test_mlflow_project_scaffold(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("mlflow-project")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    assert (project_dir / "databricks.yml").exists()
    assert (project_dir / "resources" / "jobs" / "mlflow_job.yml").exists()
    assert (project_dir / "resources" / "schemas" / "schema.yml").exists()
    assert (project_dir / "notebooks" / "train.py").exists()
    assert (project_dir / "notebooks" / "register.py").exists()
    assert (project_dir / "notebooks" / "score.py").exists()


def test_mlflow_project_scaffold_renders_train_notebook(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("mlflow-project")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    nb = (project_dir / "notebooks" / "train.py").read_text()
    assert "# Databricks notebook source" in nb
    assert "mlflow.set_experiment" in nb
    assert "RandomForestRegressor" in nb
    assert "mlflow.sklearn.log_model" in nb
    assert "samples.tpch" in nb


def test_mlflow_project_scaffold_renders_register_notebook(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("mlflow-project")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    nb = (project_dir / "notebooks" / "register.py").read_text()
    assert "# Databricks notebook source" in nb
    assert "mlflow.register_model" in nb
    assert "set_registered_model_alias" in nb
    assert "champion" in nb


def test_mlflow_project_scaffold_renders_score_notebook(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("mlflow-project")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    nb = (project_dir / "notebooks" / "score.py").read_text()
    assert "# Databricks notebook source" in nb
    assert "mlflow.pyfunc.load_model" in nb
    assert "@champion" in nb
    assert "predicted_total_price" in nb


def test_mlflow_project_scaffold_renders_bundle_variables(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("mlflow-project")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    bundle = (project_dir / "databricks.yml").read_text()
    assert "mlflow_demo" in bundle
    assert "tpch_order_value" in bundle
    assert "/Shared/tpch-order-value" in bundle
