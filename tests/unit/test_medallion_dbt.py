"""Unit tests for the medallion-dbt accelerator."""

from __future__ import annotations

from pathlib import Path


def test_get_medallion_dbt_accelerator():
    from dpa.accelerators import get_accelerator

    cls = get_accelerator("medallion-dbt")
    assert cls is not None
    assert cls.name == "medallion-dbt"


def test_medallion_dbt_list_files():
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-dbt")()
    files = [str(f).replace("\\", "/") for f in acc.list_files()]

    assert "databricks.yml" in files
    assert "dbt_project.yml" in files
    assert "profiles.yml" in files
    assert "resources/jobs/dbt_job.yml" in files
    assert "models/sources.yml" in files
    assert "models/bronze/orders.sql" in files
    assert "models/bronze/lineitem.sql" in files
    assert "models/bronze/part.sql" in files
    assert "models/bronze/supplier.sql" in files
    assert "models/bronze/partsupp.sql" in files
    assert "models/gold/dim_customer.sql" in files
    assert "models/gold/dim_part.sql" in files
    assert "models/gold/dim_supplier.sql" in files
    assert "models/gold/fact_order.sql" in files


def test_medallion_dbt_scaffold(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-dbt")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    assert (project_dir / "databricks.yml").exists()
    assert (project_dir / "dbt_project.yml").exists()
    assert (project_dir / "profiles.yml").exists()
    assert (project_dir / "resources" / "jobs" / "dbt_job.yml").exists()
    assert (project_dir / "models" / "sources.yml").exists()
    assert (project_dir / "models" / "bronze" / "orders.sql").exists()
    assert (project_dir / "models" / "bronze" / "part.sql").exists()
    assert (project_dir / "models" / "bronze" / "supplier.sql").exists()
    assert (project_dir / "models" / "bronze" / "partsupp.sql").exists()
    assert (project_dir / "models" / "gold" / "dim_customer.sql").exists()
    assert (project_dir / "models" / "gold" / "dim_part.sql").exists()
    assert (project_dir / "models" / "gold" / "dim_supplier.sql").exists()
    assert (project_dir / "models" / "gold" / "fact_order.sql").exists()


def test_medallion_dbt_scaffold_renders_dbt_project(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-dbt")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    content = (project_dir / "dbt_project.yml").read_text()
    assert "medallion_dbt" in content
    assert "+database" in content
    assert "dpa_bronze_dev" in content
    assert "dpa_gold_dev" in content


def test_medallion_dbt_scaffold_renders_bundle_variables(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-dbt")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    bundle = (project_dir / "databricks.yml").read_text()
    assert "medallion-dbt" in bundle
    assert "dpa_bronze_dev" in bundle
    assert "dpa_gold_dev" in bundle
    assert "tpch_dbt" in bundle


def test_medallion_dbt_scaffold_renders_serverless_env(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-dbt")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    job_yml = (project_dir / "resources" / "jobs" / "dbt_job.yml").read_text()
    assert "environment_key" in job_yml
    assert "dbt-databricks" in job_yml
    assert "workspace.file_path" in job_yml
    assert "WORKSPACE" in job_yml
