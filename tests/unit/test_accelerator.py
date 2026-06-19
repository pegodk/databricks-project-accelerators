"""Unit tests for the medallion-sdp accelerator scaffold."""

from __future__ import annotations

from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Industry config loading
# ---------------------------------------------------------------------------

def test_finance_config_loads():
    from dia.industries import get_industry_config

    cfg = get_industry_config("medallion-sdp", "finance")
    assert cfg is not None
    assert cfg["name"] == "finance"
    assert "bronze_tables" in cfg
    assert len(cfg["bronze_tables"]) == 3  # transactions, accounts, customers


def test_unknown_industry_returns_none():
    from dia.industries import get_industry_config

    assert get_industry_config("medallion-sdp", "fantasy_sports") is None


def test_unknown_accelerator_returns_none():
    from dia.industries import get_industry_config

    assert get_industry_config("nonexistent-acc", "finance") is None


def test_list_industry_support():
    from dia.industries import list_industry_support

    support = list_industry_support()
    assert "finance" in support
    assert support["finance"]["medallion-sdp"] is True


# ---------------------------------------------------------------------------
# Accelerator registry
# ---------------------------------------------------------------------------

def test_get_accelerator():
    from dia.accelerators import get_accelerator

    cls = get_accelerator("medallion-sdp")
    assert cls is not None
    assert cls.name == "medallion-sdp"


def test_get_unknown_accelerator():
    from dia.accelerators import get_accelerator

    assert get_accelerator("unicorn-engine") is None


# ---------------------------------------------------------------------------
# Scaffold: generated file list
# ---------------------------------------------------------------------------

def test_list_files_finance():
    from dia.accelerators import get_accelerator
    from dia.industries import get_industry_config

    cfg = get_industry_config("medallion-sdp", "finance")
    acc = get_accelerator("medallion-sdp")(industry="finance", industry_config=cfg)
    files = acc.list_files()

    str_files = [str(f).replace("\\", "/") for f in files]

    assert "databricks.yml" in str_files
    assert "pyproject.toml" in str_files
    assert "resources/pipelines/pipeline.yml" in str_files
    assert "resources/jobs/job.yml" in str_files
    assert "resources/schemas/schemas.yml" in str_files
    assert any("dim_customer" in f for f in str_files)
    assert any("fact_transactions" in f for f in str_files)
    assert any("fake_data_source" in f for f in str_files)


# ---------------------------------------------------------------------------
# Scaffold: actual file generation
# ---------------------------------------------------------------------------

def test_scaffold_finance(tmp_path: Path):
    from dia.accelerators import get_accelerator
    from dia.industries import get_industry_config

    cfg = get_industry_config("medallion-sdp", "finance")
    acc = get_accelerator("medallion-sdp")(industry="finance", industry_config=cfg)
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    assert (project_dir / "databricks.yml").exists()
    assert (project_dir / "pyproject.toml").exists()
    assert (project_dir / "resources" / "pipelines" / "pipeline.yml").exists()
    assert (project_dir / "resources" / "jobs" / "job.yml").exists()
    assert (project_dir / "resources" / "schemas" / "schemas.yml").exists()
    assert (project_dir / "src" / "framework" / "config.py").exists()
    assert (project_dir / "src" / "framework" / "dlt.py").exists()
    assert (project_dir / "src" / "pipelines" / "finance" / "metadata" / "bronze" / "tables.yml").exists()
    assert (project_dir / "src" / "pipelines" / "finance" / "metadata" / "silver" / "tables.yml").exists()
    assert (project_dir / "src" / "pipelines" / "finance" / "transformations" / "bronze" / "ingest_tables.py").exists()
    assert (project_dir / "src" / "pipelines" / "finance" / "transformations" / "silver" / "clean_tables.py").exists()
    assert (project_dir / "src" / "pipelines" / "finance" / "data_sources" / "fake_data_source.py").exists()
    assert (project_dir / "src" / "pipelines" / "finance" / "transformations" / "gold" / "dim_customer.py").exists()
    assert (project_dir / "src" / "pipelines" / "finance" / "transformations" / "gold" / "fact_transactions.py").exists()


def test_scaffold_renders_industry_name(tmp_path: Path):
    from dia.accelerators import get_accelerator
    from dia.industries import get_industry_config

    cfg = get_industry_config("medallion-sdp", "finance")
    acc = get_accelerator("medallion-sdp")(industry="finance", industry_config=cfg)
    acc.scaffold(target=tmp_path / acc.project_slug)

    databricks_yml = (tmp_path / acc.project_slug / "databricks.yml").read_text()
    assert "finance-medallion-sdp" in databricks_yml

    pipeline_yml = (tmp_path / acc.project_slug / "resources" / "pipelines" / "pipeline.yml").read_text()
    assert "FinanceFakeDataSource" not in pipeline_yml  # pipeline.yml has no class name
    assert "finance_medallion_sdp_pipeline" in pipeline_yml


def test_scaffold_renders_bronze_metadata(tmp_path: Path):
    from dia.accelerators import get_accelerator
    from dia.industries import get_industry_config

    cfg = get_industry_config("medallion-sdp", "finance")
    acc = get_accelerator("medallion-sdp")(industry="finance", industry_config=cfg)
    acc.scaffold(target=tmp_path / acc.project_slug)

    bronze_yml = (
        tmp_path / acc.project_slug / "src" / "pipelines" / "finance" / "metadata" / "bronze" / "tables.yml"
    ).read_text()
    assert "transactions" in bronze_yml
    assert "accounts" in bronze_yml
    assert "customers" in bronze_yml
    assert "FinanceFakeDataSource" in bronze_yml


def test_scaffold_renders_silver_expectations(tmp_path: Path):
    from dia.accelerators import get_accelerator
    from dia.industries import get_industry_config

    cfg = get_industry_config("medallion-sdp", "finance")
    acc = get_accelerator("medallion-sdp")(industry="finance", industry_config=cfg)
    acc.scaffold(target=tmp_path / acc.project_slug)

    silver_yml = (
        tmp_path / acc.project_slug / "src" / "pipelines" / "finance" / "metadata" / "silver" / "tables.yml"
    ).read_text()
    assert "transaction_id_not_null" in silver_yml
    assert "status_valid" in silver_yml


def test_scaffold_no_overwrite_without_force(tmp_path: Path):
    from dia.accelerators import get_accelerator
    from dia.industries import get_industry_config

    cfg = get_industry_config("medallion-sdp", "finance")
    acc = get_accelerator("medallion-sdp")(industry="finance", industry_config=cfg)
    project_dir = tmp_path / acc.project_slug

    acc.scaffold(target=project_dir)
    original = (project_dir / "databricks.yml").read_text()

    # Modify file then re-scaffold without force — should not overwrite
    (project_dir / "databricks.yml").write_text("# modified")
    acc.scaffold(target=project_dir, force=False)
    assert (project_dir / "databricks.yml").read_text() == "# modified"

    # With force=True it should overwrite
    acc.scaffold(target=project_dir, force=True)
    assert (project_dir / "databricks.yml").read_text() == original
