"""Unit tests for the ai-bi accelerator."""

from __future__ import annotations

import json
from pathlib import Path


def test_get_ai_bi_accelerator():
    from dpa.accelerators import get_accelerator

    cls = get_accelerator("ai-bi")
    assert cls is not None
    assert cls.name == "ai-bi"


def test_ai_bi_list_files():
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("ai-bi")()
    files = [str(f).replace("\\", "/") for f in acc.list_files()]

    assert "databricks.yml" in files
    assert "resources/jobs/setup_views_job.yml" in files
    assert "resources/dashboards/dashboard.yml" in files
    assert "resources/warehouses/warehouse.yml" in files
    assert "resources/genie_spaces/tpch_genie.genie_space.yml" in files
    assert "src/sql/setup_metric_views.sql" in files
    assert "resources/dashboards/tpch_overview.lvdash.json" in files
    assert "resources/genie_spaces/tpch_genie.geniespace.json" in files


def test_ai_bi_scaffold(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("ai-bi")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    assert (project_dir / "databricks.yml").exists()
    assert (project_dir / "resources" / "jobs" / "setup_views_job.yml").exists()
    assert (project_dir / "resources" / "dashboards" / "dashboard.yml").exists()
    assert (project_dir / "resources" / "warehouses" / "warehouse.yml").exists()
    assert (project_dir / "resources" / "genie_spaces" / "tpch_genie.genie_space.yml").exists()
    assert (project_dir / "src" / "sql" / "setup_metric_views.sql").exists()
    assert (project_dir / "resources" / "dashboards" / "tpch_overview.lvdash.json").exists()
    assert (project_dir / "resources" / "genie_spaces" / "tpch_genie.geniespace.json").exists()


def test_ai_bi_scaffold_renders_setup_sql(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("ai-bi")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    sql = (project_dir / "src" / "sql" / "setup_metric_views.sql").read_text()
    assert "main.tpch_metrics" in sql
    assert "CREATE OR REPLACE VIEW" in sql
    assert "WITH METRICS" in sql
    assert "LANGUAGE YAML" in sql
    assert "v_tpch" in sql
    assert "samples.tpch.orders" in sql
    assert "t7d_customers" in sql
    assert "total_revenue" in sql


def test_ai_bi_scaffold_renders_valid_dashboard_json(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("ai-bi")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    lvdash = (project_dir / "resources" / "dashboards" / "tpch_overview.lvdash.json").read_text()
    parsed = json.loads(lvdash)
    assert "displayName" in parsed
    assert "datasets" in parsed
    assert "pages" in parsed
    assert len(parsed["datasets"]) > 0
    assert len(parsed["pages"]) > 0


def test_ai_bi_scaffold_renders_dashboard_name(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("ai-bi")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    dashboard_yml = (project_dir / "resources" / "dashboards" / "dashboard.yml").read_text()
    assert "TPCH Sales Overview" in dashboard_yml


def test_ai_bi_scaffold_renders_valid_genie_json(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("ai-bi")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    genie_json = (project_dir / "resources" / "genie_spaces" / "tpch_genie.geniespace.json").read_text()
    parsed = json.loads(genie_json)
    assert "display_name" in parsed
    assert "tables" in parsed
    assert "curated_questions" in parsed
    assert "instructions" in parsed
    assert len(parsed["tables"]) == 1
    assert parsed["tables"][0]["name"] == "v_tpch"
    assert len(parsed["curated_questions"]) > 0


def test_ai_bi_scaffold_renders_genie_catalog_and_schema(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("ai-bi")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    parsed = json.loads(
        (project_dir / "resources" / "genie_spaces" / "tpch_genie.geniespace.json").read_text()
    )
    table_catalogs = {t["catalog"] for t in parsed["tables"]}
    table_schemas = {t["schema"] for t in parsed["tables"]}
    assert table_catalogs == {"main"}
    assert table_schemas == {"tpch_metrics"}


def test_ai_bi_scaffold_renders_genie_space_yml(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("ai-bi")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    genie_yml = (project_dir / "resources" / "genie_spaces" / "tpch_genie.genie_space.yml").read_text()
    assert "TPCH Sales Genie" in genie_yml
    assert "starter_warehouse" in genie_yml
    assert "tpch_genie.geniespace.json" in genie_yml
