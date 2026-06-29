"""Unit tests for the custom-spark-lib accelerator."""

from __future__ import annotations

from pathlib import Path


def test_get_custom_spark_lib_accelerator():
    from dpa.accelerators import get_accelerator

    cls = get_accelerator("custom-spark-lib")
    assert cls is not None
    assert cls.name == "custom-spark-lib"


def test_custom_spark_lib_list_files():
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("custom-spark-lib")()
    files = [str(f).replace("\\", "/") for f in acc.list_files()]

    assert "databricks.yml" in files
    assert "pyproject.toml" in files
    assert "resources/jobs/medallion_job.yml" in files
    assert "notebooks/bronze/ingest.py" in files
    assert "notebooks/gold/aggregate.py" in files
    assert "src/spark_transforms/__init__.py" in files
    assert "src/spark_transforms/medallion.py" in files


def test_custom_spark_lib_scaffold(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("custom-spark-lib")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    assert (project_dir / "databricks.yml").exists()
    assert (project_dir / "pyproject.toml").exists()
    assert (project_dir / "resources" / "jobs" / "medallion_job.yml").exists()
    assert (project_dir / "notebooks" / "bronze" / "ingest.py").exists()
    assert (project_dir / "notebooks" / "gold" / "aggregate.py").exists()
    assert (project_dir / "src" / "spark_transforms" / "__init__.py").exists()
    assert (project_dir / "src" / "spark_transforms" / "medallion.py").exists()


def test_custom_spark_lib_scaffold_renders_catalogs(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("custom-spark-lib")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    bundle = (project_dir / "databricks.yml").read_text()
    assert "dpa_bronze_dev" in bundle
    assert "dpa_gold_dev" in bundle
    assert "artifacts" in bundle
    assert "type: whl" in bundle


def test_custom_spark_lib_scaffold_renders_pyproject(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("custom-spark-lib")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    pyproject = (project_dir / "pyproject.toml").read_text()
    assert "custom_spark_lib_transforms" in pyproject
    assert "setuptools" in pyproject
    assert 'where = ["src"]' in pyproject


def test_custom_spark_lib_scaffold_renders_bronze_notebook(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("custom-spark-lib")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    nb = (project_dir / "notebooks" / "bronze" / "ingest.py").read_text()
    assert "# Databricks notebook source" in nb
    assert "samples.tpch" in nb
    assert "dpa_bronze_dev" in nb
    assert "trigger(availableNow=True)" in nb
    assert "readStream" in nb


def test_custom_spark_lib_scaffold_renders_gold_notebook(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("custom-spark-lib")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    nb = (project_dir / "notebooks" / "gold" / "aggregate.py").read_text()
    assert "# Databricks notebook source" in nb
    assert "spark_transforms" in nb
    assert "dim_customer" in nb
    assert "fact_order" in nb
    assert "saveAsTable" in nb
