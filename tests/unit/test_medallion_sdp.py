"""Unit tests for the medallion-sdp accelerator."""

from __future__ import annotations

from pathlib import Path


def test_get_medallion_sdp_accelerator():
    from dpa.accelerators import get_accelerator

    cls = get_accelerator("medallion-sdp")
    assert cls is not None
    assert cls.name == "medallion-sdp"


def test_medallion_sdp_list_files():
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    files = [str(f).replace("\\", "/") for f in acc.list_files()]

    assert "databricks.yml" in files
    assert "resources/pipelines/pipeline.yml" in files
    assert "resources/schemas/schemas.yml" in files
    assert "resources/jobs/trigger_job.yml" in files
    assert "src/pipelines/bronze/ingest.py" in files
    assert "src/pipelines/silver/tpch_customer.py" in files
    assert "src/pipelines/silver/tpch_orders.py" in files
    assert "src/pipelines/silver/tpch_lineitem.py" in files
    assert "src/pipelines/gold/tpch_dim_customer.py" in files
    assert "src/pipelines/gold/tpch_dim_part.py" in files
    assert "src/pipelines/gold/tpch_dim_supplier.py" in files
    assert "src/pipelines/gold/tpch_fact_order.py" in files
    assert not any("src_example" in f for f in files)


def test_medallion_sdp_scaffold(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    assert (project_dir / "databricks.yml").exists()
    assert (project_dir / "resources" / "pipelines" / "pipeline.yml").exists()
    assert (project_dir / "resources" / "schemas" / "schemas.yml").exists()
    assert (project_dir / "resources" / "jobs" / "trigger_job.yml").exists()
    assert (project_dir / "src" / "pipelines" / "bronze" / "ingest.py").exists()
    assert (project_dir / "src" / "pipelines" / "silver" / "tpch_customer.py").exists()
    assert (project_dir / "src" / "pipelines" / "silver" / "tpch_orders.py").exists()
    assert (project_dir / "src" / "pipelines" / "silver" / "tpch_lineitem.py").exists()
    assert (project_dir / "src" / "pipelines" / "gold" / "tpch_dim_customer.py").exists()
    assert (project_dir / "src" / "pipelines" / "gold" / "tpch_dim_part.py").exists()
    assert (project_dir / "src" / "pipelines" / "gold" / "tpch_dim_supplier.py").exists()
    assert (project_dir / "src" / "pipelines" / "gold" / "tpch_fact_order.py").exists()
    assert not (project_dir / "src_example").exists()


def test_medallion_sdp_scaffold_renders_project_slug(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    acc.scaffold(target=tmp_path / acc.project_slug)

    content = (tmp_path / acc.project_slug / "databricks.yml").read_text()
    assert "medallion-sdp" in content


def test_medallion_sdp_scaffold_renders_pipeline_config(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    acc.scaffold(target=tmp_path / acc.project_slug)

    pipeline = (tmp_path / acc.project_slug / "resources" / "pipelines" / "pipeline.yml").read_text()
    assert "src/pipelines/**" in pipeline
    assert "bronze_catalog" in pipeline
    assert "silver_catalog" in pipeline
    assert "gold_catalog" in pipeline
    assert "bronze_schema" in pipeline
    assert "gold_schema" in pipeline


def test_medallion_sdp_scaffold_renders_schemas(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    acc.scaffold(target=tmp_path / acc.project_slug)

    schemas = (tmp_path / acc.project_slug / "resources" / "schemas" / "schemas.yml").read_text()
    assert "var.bronze_catalog" in schemas
    assert "var.silver_catalog" in schemas
    assert "var.gold_catalog" in schemas
    assert "tpch" in schemas


def test_medallion_sdp_scaffold_bronze_uses_streaming(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    acc.scaffold(target=tmp_path / acc.project_slug)

    ingest = (tmp_path / acc.project_slug / "src" / "pipelines" / "bronze" / "ingest.py").read_text()
    assert "create_streaming_table" in ingest
    assert "append_flow" in ingest
    assert "appendOnly" in ingest
    assert "readStream" in ingest
    assert "samples.tpch" in ingest


def test_medallion_sdp_scaffold_silver_uses_cdc(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    acc.scaffold(target=tmp_path / acc.project_slug)

    orders = (tmp_path / acc.project_slug / "src" / "pipelines" / "silver" / "tpch_orders.py").read_text()
    assert "create_streaming_table" in orders
    assert "create_auto_cdc_from_snapshot_flow" in orders
    assert "expect_or_drop" in orders


def test_medallion_sdp_scaffold_gold_dims_have_surrogate_key(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    acc.scaffold(target=tmp_path / acc.project_slug)

    dim = (tmp_path / acc.project_slug / "src" / "pipelines" / "gold" / "tpch_dim_customer.py").read_text()
    assert "xxhash64" in dim
    assert "customer_id" in dim
    assert "materialized_view" in dim


def test_medallion_sdp_scaffold_gold_fact_joins_dims(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    acc.scaffold(target=tmp_path / acc.project_slug)

    fact = (tmp_path / acc.project_slug / "src" / "pipelines" / "gold" / "tpch_fact_order.py").read_text()
    assert "fact_order" in fact
    assert "datediff" in fact
    assert "customer_id" in fact
    assert "part_id" in fact
    assert "supplier_id" in fact


def test_medallion_sdp_scaffold_no_overwrite_without_force(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    project_dir = tmp_path / acc.project_slug

    acc.scaffold(target=project_dir)
    original = (project_dir / "databricks.yml").read_text()

    (project_dir / "databricks.yml").write_text("# modified")
    acc.scaffold(target=project_dir, force=False)
    assert (project_dir / "databricks.yml").read_text() == "# modified"

    acc.scaffold(target=project_dir, force=True)
    assert (project_dir / "databricks.yml").read_text() == original
