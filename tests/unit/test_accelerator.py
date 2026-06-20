"""Unit tests for the accelerator scaffold."""

from __future__ import annotations

from pathlib import Path

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

def test_get_accelerator():
    from dpa.accelerators import get_accelerator

    cls = get_accelerator("medallion-sdp")
    assert cls is not None
    assert cls.name == "medallion-sdp"


def test_get_unknown_accelerator():
    from dpa.accelerators import get_accelerator

    assert get_accelerator("unicorn-engine") is None


def test_registry_contains_all_accelerators():
    from dpa.accelerators import ACCELERATOR_REGISTRY

    assert "medallion-sdp" in ACCELERATOR_REGISTRY
    assert "app-streamlit" in ACCELERATOR_REGISTRY
    assert "ai-bi" in ACCELERATOR_REGISTRY


# ---------------------------------------------------------------------------
# File list
# ---------------------------------------------------------------------------

def test_list_files():
    from dpa.accelerators import get_accelerator

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
    from dpa.accelerators import get_accelerator

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
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    acc.scaffold(target=tmp_path / acc.project_slug)

    content = (tmp_path / acc.project_slug / "databricks.yml").read_text()
    assert "medallion-sdp" in content


def test_scaffold_renders_bronze_metadata(tmp_path: Path):
    from dpa.accelerators import get_accelerator

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
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("medallion-sdp")()
    acc.scaffold(target=tmp_path / acc.project_slug)

    silver_yml = (
        tmp_path / acc.project_slug / "src" / "pipelines" / "main" / "metadata" / "silver" / "tables.yml"
    ).read_text()
    assert "event_id_not_null" in silver_yml
    assert "entity_id_not_null" in silver_yml


def test_scaffold_renders_data_source_class(tmp_path: Path):
    from dpa.accelerators import get_accelerator

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


# ---------------------------------------------------------------------------
# app-streamlit
# ---------------------------------------------------------------------------

def test_get_app_streamlit_accelerator():
    from dpa.accelerators import get_accelerator

    cls = get_accelerator("app-streamlit")
    assert cls is not None
    assert cls.name == "app-streamlit"


def test_app_streamlit_list_files():
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("app-streamlit")()
    files = [str(f).replace("\\", "/") for f in acc.list_files()]

    assert "databricks.yml" in files
    assert "resources/apps/app.yml" in files
    assert "resources/warehouses/warehouse.yml" in files
    assert "app/app.py" in files
    assert "app/app.yaml" in files
    assert "app/requirements.txt" in files


def test_app_streamlit_scaffold(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("app-streamlit")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    assert (project_dir / "databricks.yml").exists()
    assert (project_dir / "resources" / "apps" / "app.yml").exists()
    assert (project_dir / "resources" / "warehouses" / "warehouse.yml").exists()
    assert (project_dir / "app" / "app.py").exists()
    assert (project_dir / "app" / "app.yaml").exists()
    assert (project_dir / "app" / "requirements.txt").exists()


def test_app_streamlit_scaffold_renders_app_name(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("app-streamlit")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    bundle = (project_dir / "databricks.yml").read_text()
    assert "tpch-analytics" in bundle

    app_resource = (project_dir / "resources" / "apps" / "app.yml").read_text()
    assert "tpch_analytics" in app_resource
    assert "DATABRICKS_HTTP_PATH" in app_resource
    assert "resources.sql_warehouses.starter_warehouse.id" in app_resource


def test_app_streamlit_scaffold_renders_tpch_queries(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("app-streamlit")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    app_py = (project_dir / "app" / "app.py").read_text()
    assert "samples.tpch" in app_py
    assert "streamlit" in app_py
    assert "plotly" in app_py


def test_app_streamlit_requirements(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("app-streamlit")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    reqs = (project_dir / "app" / "requirements.txt").read_text()
    assert "streamlit" in reqs
    assert "databricks-sql-connector" in reqs
    assert "plotly" in reqs


# ---------------------------------------------------------------------------
# mlflow-project
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# python-wheel
# ---------------------------------------------------------------------------

def test_get_python_wheel_accelerator():
    from dpa.accelerators import get_accelerator

    cls = get_accelerator("python-wheel")
    assert cls is not None
    assert cls.name == "python-wheel"


def test_python_wheel_list_files():
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("python-wheel")()
    files = [str(f).replace("\\", "/") for f in acc.list_files()]

    assert "databricks.yml" in files
    assert "pyproject.toml" in files
    assert "resources/jobs/wheel_job.yml" in files
    assert "resources/volumes/wheels_volume.yml" in files
    assert "notebooks/build_and_upload.py" in files
    assert "notebooks/verify_imports.py" in files
    assert "src/python_wheel/__init__.py" in files
    assert "src/python_wheel/functions.py" in files


def test_python_wheel_scaffold(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("python-wheel")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    assert (project_dir / "databricks.yml").exists()
    assert (project_dir / "pyproject.toml").exists()
    assert (project_dir / "resources" / "jobs" / "wheel_job.yml").exists()
    assert (project_dir / "resources" / "volumes" / "wheels_volume.yml").exists()
    assert (project_dir / "notebooks" / "build_and_upload.py").exists()
    assert (project_dir / "notebooks" / "verify_imports.py").exists()
    assert (project_dir / "src" / "python_wheel" / "__init__.py").exists()
    assert (project_dir / "src" / "python_wheel" / "functions.py").exists()


def test_python_wheel_scaffold_renders_pyproject(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("python-wheel")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    pyproject = (project_dir / "pyproject.toml").read_text()
    assert 'name = "python-wheel"' in pyproject
    assert 'packages = ["src/python_wheel"]' in pyproject


def test_python_wheel_scaffold_renders_build_notebook(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("python-wheel")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    nb = (project_dir / "notebooks" / "build_and_upload.py").read_text()
    assert "# Databricks notebook source" in nb
    assert "pip wheel" in nb
    assert "dbutils.fs.cp" in nb
    assert "workspace_file_path" in nb


def test_python_wheel_scaffold_renders_verify_notebook(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("python-wheel")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    nb = (project_dir / "notebooks" / "verify_imports.py").read_text()
    assert "# Databricks notebook source" in nb
    assert "from python_wheel import add, greet" in nb
    assert "restartPython" in nb
    assert "Hello, Databricks!" in nb


# ---------------------------------------------------------------------------
# medallion-spark
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# ai-bi
# ---------------------------------------------------------------------------

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
    import json

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
    import json

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
    import json

    from dpa.accelerators import get_accelerator

    acc = get_accelerator("ai-bi")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    parsed = json.loads((project_dir / "resources" / "genie_spaces" / "tpch_genie.geniespace.json").read_text())
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
