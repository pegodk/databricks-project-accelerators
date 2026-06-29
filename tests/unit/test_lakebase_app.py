"""Unit tests for the app-streamlit accelerator."""

from __future__ import annotations

from pathlib import Path


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
    assert "resources/postgres_projects/lakebase.yml" in files
    assert "resources/postgres_branches/production.yml" in files
    assert "resources/postgres_endpoints/primary.yml" in files
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
    assert (project_dir / "resources" / "postgres_projects" / "lakebase.yml").exists()
    assert (project_dir / "resources" / "postgres_branches" / "production.yml").exists()
    assert (project_dir / "resources" / "postgres_endpoints" / "primary.yml").exists()
    assert (project_dir / "app" / "app.py").exists()
    assert (project_dir / "app" / "app.yaml").exists()
    assert (project_dir / "app" / "requirements.txt").exists()


def test_app_streamlit_scaffold_renders_app_name(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("app-streamlit")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    bundle = (project_dir / "databricks.yml").read_text()
    assert "app-streamlit" in bundle
    assert "lakebase_project_id" in bundle
    assert "lakebase_pghost" in bundle

    app_resource = (project_dir / "resources" / "apps" / "app.yml").read_text()
    assert "app_streamlit" in app_resource
    assert "DATABRICKS_HTTP_PATH" in app_resource
    assert "var.warehouse_id" in app_resource
    assert "postgres:" in app_resource
    assert "lakebase-db" in app_resource
    assert "PGHOST" in app_resource
    assert "ENDPOINT_NAME" in app_resource

    project_resource = (project_dir / "resources" / "postgres_projects" / "lakebase.yml").read_text()
    assert "postgres_projects" in project_resource
    assert "app_streamlit_lakebase" in project_resource
    assert "lakebase_project_id" in project_resource

    branch_resource = (project_dir / "resources" / "postgres_branches" / "production.yml").read_text()
    assert "postgres_branches" in branch_resource
    assert "production" in branch_resource
    assert "is_protected" in branch_resource

    endpoint_resource = (project_dir / "resources" / "postgres_endpoints" / "primary.yml").read_text()
    assert "postgres_endpoints" in endpoint_resource
    assert "ENDPOINT_TYPE_READ_WRITE" in endpoint_resource


def test_app_streamlit_scaffold_renders_tpch_queries(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("app-streamlit")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    app_py = (project_dir / "app" / "app.py").read_text()
    assert "samples.tpch" in app_py
    assert "streamlit" in app_py
    assert "plotly" in app_py


def test_app_streamlit_scaffold_renders_lakebase(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("app-streamlit")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    app_py = (project_dir / "app" / "app.py").read_text()
    assert "_lakebase_pool" in app_py
    assert "_ensure_schema" in app_py
    assert "_upsert_overrides" in app_py
    assert "customer_master" in app_py
    assert "psycopg" in app_py
    assert "PGHOST" in app_py
    assert "ENDPOINT_NAME" in app_py
    assert "generate_database_credential" in app_py
    assert "ConnectionPool" in app_py


def test_app_streamlit_requirements(tmp_path: Path):
    from dpa.accelerators import get_accelerator

    acc = get_accelerator("app-streamlit")()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    reqs = (project_dir / "app" / "requirements.txt").read_text()
    assert "streamlit" in reqs
    assert "databricks-sql-connector" in reqs
    assert "databricks-sdk" in reqs
    assert "plotly" in reqs
    assert "psycopg" in reqs
