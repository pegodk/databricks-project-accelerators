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
    assert "resources/genie_spaces/tpch_genie.genie_space.yml" in files
    assert "notebooks/setup_metric_views.py" in files
    assert "resources/dashboards/tpch_overview.lvdash.json" in files


def test_ai_bi_scaffold(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("ai-bi")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    assert (project_dir / "databricks.yml").exists()
    assert (project_dir / "resources" / "jobs" / "setup_views_job.yml").exists()
    assert (project_dir / "resources" / "dashboards" / "dashboard.yml").exists()
    assert (project_dir / "resources" / "genie_spaces" / "tpch_genie.genie_space.yml").exists()
    assert (project_dir / "notebooks" / "setup_metric_views.py").exists()
    assert (project_dir / "resources" / "dashboards" / "tpch_overview.lvdash.json").exists()


def test_ai_bi_scaffold_renders_setup_notebook(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("ai-bi")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    nb = (project_dir / "notebooks" / "setup_metric_views.py").read_text()
    # Widget defaults are baked from cfg at scaffold time; runtime values come from job parameters.
    assert 'dbutils.widgets.text("catalog", "dpa_gold_dev")' in nb
    assert 'dbutils.widgets.text("schema", "tpch_metrics")' in nb
    assert "CREATE OR REPLACE VIEW" in nb
    assert "WITH METRICS" in nb
    assert "LANGUAGE YAML" in nb
    assert "v_tpch" in nb
    assert "samples.tpch.orders" in nb
    assert "t7d_customers" in nb
    assert "total_revenue" in nb


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


def test_ai_bi_scaffold_renders_dashboard_catalog(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("ai-bi")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    lvdash = json.loads(
        (project_dir / "resources" / "dashboards" / "tpch_overview.lvdash.json").read_text()
    )
    queries = [ds["query"] for ds in lvdash["datasets"]]
    assert all("dpa_gold_dev.tpch_metrics" in q for q in queries)


def test_ai_bi_scaffold_renders_genie_space_yml(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("ai-bi")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    genie_yml = (project_dir / "resources" / "genie_spaces" / "tpch_genie.genie_space.yml").read_text()
    assert "dpa-ai-bi" in genie_yml
    assert "var.warehouse_id" in genie_yml
    assert "serialized_space" in genie_yml
    assert "sample_questions" in genie_yml
    assert "text_instructions" in genie_yml
    assert "dpa_gold_dev.tpch_metrics.v_tpch" in genie_yml
