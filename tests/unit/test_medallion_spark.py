"""Unit tests for the medallion-spark accelerator."""

from __future__ import annotations

from pathlib import Path


def test_get_medallion_spark_accelerator():
    from dpa.accelerators import get_accelerator

    cls = get_accelerator("medallion-spark")
    assert cls is not None
    assert cls.name == "medallion-spark"


def test_medallion_spark_list_files():
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-spark")()
    files = [str(f).replace("\\", "/") for f in acc.list_files()]

    assert "databricks.yml" in files
    assert "resources/jobs/medallion_job.yml" in files
    assert "notebooks/bronze/ingest.py" in files
    assert "notebooks/silver/transform.py" in files
    assert "notebooks/gold/aggregate.py" in files


def test_medallion_spark_scaffold(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-spark")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    assert (project_dir / "databricks.yml").exists()
    assert (project_dir / "resources" / "jobs" / "medallion_job.yml").exists()
    assert (project_dir / "notebooks" / "bronze" / "ingest.py").exists()
    assert (project_dir / "notebooks" / "silver" / "transform.py").exists()
    assert (project_dir / "notebooks" / "gold" / "aggregate.py").exists()


def test_medallion_spark_scaffold_renders_catalogs(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-spark")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    bundle = (project_dir / "databricks.yml").read_text()
    assert "bronze_dev" in bundle
    assert "silver_dev" in bundle
    assert "gold_dev" in bundle


def test_medallion_spark_scaffold_renders_bronze_notebook(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-spark")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    nb = (project_dir / "notebooks" / "bronze" / "ingest.py").read_text()
    assert "# Databricks notebook source" in nb
    assert "samples.tpch" in nb
    assert "bronze_dev" in nb
    assert "trigger(availableNow=True)" in nb
    assert "readStream" in nb


def test_medallion_spark_scaffold_renders_silver_notebook(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-spark")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    nb = (project_dir / "notebooks" / "silver" / "transform.py").read_text()
    assert "# Databricks notebook source" in nb
    assert "orders_enriched" in nb
    assert "readStream" in nb
    assert "writeStream" in nb


def test_medallion_spark_scaffold_renders_gold_notebook(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-spark")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    nb = (project_dir / "notebooks" / "gold" / "aggregate.py").read_text()
    assert "# Databricks notebook source" in nb
    assert "sales_summary" in nb
    assert "customer_summary" in nb
    assert "outputMode" in nb
