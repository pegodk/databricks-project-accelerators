"""Unit tests for the accelerator scaffold."""

from __future__ import annotations

from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Registry
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
# File list
# ---------------------------------------------------------------------------

def test_list_files():
    from dia.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    files = [str(f).replace("\\", "/") for f in acc.list_files()]

    assert "databricks.yml" in files
    assert "pyproject.toml" in files
    assert "resources/pipelines/pipeline.yml" in files
    assert "resources/jobs/job.yml" in files
    assert "resources/schemas/schemas.yml" in files
    assert any("synthetic_data_source" in f for f in files)
    assert any("dim_entity" in f for f in files)
    assert any("fact_events" in f for f in files)


# ---------------------------------------------------------------------------
# Scaffold: file presence
# ---------------------------------------------------------------------------

def test_scaffold(tmp_path: Path):
    from dia.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    assert (project_dir / "databricks.yml").exists()
    assert (project_dir / "pyproject.toml").exists()
    assert (project_dir / "resources" / "pipelines" / "pipeline.yml").exists()
    assert (project_dir / "resources" / "jobs" / "job.yml").exists()
    assert (project_dir / "resources" / "schemas" / "schemas.yml").exists()
    assert (project_dir / "src" / "framework" / "config.py").exists()
    assert (project_dir / "src" / "framework" / "dlt.py").exists()
    assert (project_dir / "src" / "pipelines" / "main" / "data_sources" / "synthetic_data_source.py").exists()
    assert (project_dir / "src" / "pipelines" / "main" / "metadata" / "bronze" / "tables.yml").exists()
    assert (project_dir / "src" / "pipelines" / "main" / "metadata" / "silver" / "tables.yml").exists()
    assert (project_dir / "src" / "pipelines" / "main" / "transformations" / "bronze" / "ingest_tables.py").exists()
    assert (project_dir / "src" / "pipelines" / "main" / "transformations" / "silver" / "clean_tables.py").exists()
    assert (project_dir / "src" / "pipelines" / "main" / "transformations" / "gold" / "dim_entity.py").exists()
    assert (project_dir / "src" / "pipelines" / "main" / "transformations" / "gold" / "fact_events.py").exists()


# ---------------------------------------------------------------------------
# Scaffold: rendered content
# ---------------------------------------------------------------------------

def test_scaffold_renders_project_slug(tmp_path: Path):
    from dia.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    acc.scaffold(target=tmp_path / acc.project_slug)

    content = (tmp_path / acc.project_slug / "databricks.yml").read_text()
    assert "medallion-sdp" in content


def test_scaffold_renders_bronze_metadata(tmp_path: Path):
    from dia.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    acc.scaffold(target=tmp_path / acc.project_slug)

    bronze_yml = (
        tmp_path / acc.project_slug / "src" / "pipelines" / "main" / "metadata" / "bronze" / "tables.yml"
    ).read_text()
    assert "events" in bronze_yml
    assert "entities" in bronze_yml
    assert "records" in bronze_yml
    assert "SyntheticDataSource" in bronze_yml


def test_scaffold_renders_silver_expectations(tmp_path: Path):
    from dia.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    acc.scaffold(target=tmp_path / acc.project_slug)

    silver_yml = (
        tmp_path / acc.project_slug / "src" / "pipelines" / "main" / "metadata" / "silver" / "tables.yml"
    ).read_text()
    assert "event_id_not_null" in silver_yml
    assert "entity_id_not_null" in silver_yml


def test_scaffold_renders_data_source_class(tmp_path: Path):
    from dia.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    acc.scaffold(target=tmp_path / acc.project_slug)

    source = (
        tmp_path / acc.project_slug / "src" / "pipelines" / "main" / "data_sources" / "synthetic_data_source.py"
    ).read_text()
    assert "class SyntheticDataSource(DataSource)" in source
    assert "events" in source
    assert "entities" in source
    assert "records" in source


# ---------------------------------------------------------------------------
# Scaffold: overwrite behaviour
# ---------------------------------------------------------------------------

def test_scaffold_no_overwrite_without_force(tmp_path: Path):
    from dia.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    project_dir = tmp_path / acc.project_slug

    acc.scaffold(target=project_dir)
    original = (project_dir / "databricks.yml").read_text()

    (project_dir / "databricks.yml").write_text("# modified")
    acc.scaffold(target=project_dir, force=False)
    assert (project_dir / "databricks.yml").read_text() == "# modified"

    acc.scaffold(target=project_dir, force=True)
    assert (project_dir / "databricks.yml").read_text() == original
