"""Shared fixtures for integration tests against a live Databricks workspace."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Generator

import pytest

_BRONZE_CATALOG = "dpa_bronze_dev"
_SILVER_CATALOG = "dpa_silver_dev"
_GOLD_CATALOG = "dpa_gold_dev"
_BUNDLE_PREFIX = "dpa"


def _require_env(name: str) -> str:
    val = os.getenv(name, "").strip()
    if not val:
        pytest.skip(f"${name} not set — skipping integration tests")
    return val


def _require_databricks_cli() -> str:
    path = shutil.which("databricks")
    if path is None:
        pytest.skip("Databricks CLI not found on PATH — skipping integration tests")
    return path


def patch_databricks_yml(project_dir: Path, project_slug: str, host: str) -> None:
    """Replace workspace URL placeholders and prefix the bundle name."""
    dab_yml = project_dir / "databricks.yml"
    content = dab_yml.read_text()
    content = content.replace("https://<your-dev-workspace-url>", host)
    content = content.replace("https://<your-prod-workspace-url>", host)
    # Prefix bundle name so test deployments are clearly identifiable in the workspace.
    content = content.replace(
        f"name: {project_slug}\n",
        f"name: {_BUNDLE_PREFIX}-{project_slug}\n",
        1,
    )
    dab_yml.write_text(content)


def _bundle_vars(accelerator_name: str) -> list[str]:
    if accelerator_name == "medallion-sdp":
        return [
            "--var", f"bronze_catalog={_BRONZE_CATALOG}",
            "--var", f"silver_catalog={_SILVER_CATALOG}",
            "--var", f"gold_catalog={_GOLD_CATALOG}",
        ]
    if accelerator_name == "medallion-spark":
        return [
            "--var", f"bronze_catalog={_BRONZE_CATALOG}",
            "--var", f"silver_catalog={_SILVER_CATALOG}",
            "--var", f"gold_catalog={_GOLD_CATALOG}",
            "--var", "bronze_schema=tpch_spark",
            "--var", "silver_schema=tpch_spark",
            "--var", "gold_schema=tpch_model_spark",
        ]
    if accelerator_name == "medallion-dbt":
        return [
            "--var", f"bronze_catalog={_BRONZE_CATALOG}",
            "--var", f"silver_catalog={_SILVER_CATALOG}",
            "--var", f"gold_catalog={_GOLD_CATALOG}",
            "--var", "bronze_schema=tpch_dbt",
            "--var", "silver_schema=tpch_dbt",
            "--var", "gold_schema=tpch_model_dbt",
        ]
    return []


def _current_databricks_user(cli: str) -> str:
    result = subprocess.run(
        [cli, "current-user", "me", "--output", "json"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    try:
        return json.loads(result.stdout).get("userName", "")
    except (json.JSONDecodeError, AttributeError):
        return ""


def _cleanup_stale_schemas(cli: str, accelerator_name: str) -> None:
    """Delete schemas stranded by a previous partially-failed bundle deploy.

    When bundle deploy fails mid-way, DAB may create Unity Catalog schemas without
    recording them in the deployment state. Subsequent `bundle destroy` skips them,
    causing SCHEMA_ALREADY_EXISTS on the next deploy.
    """
    from dpa.accelerators import get_accelerator

    acc_cls = get_accelerator(accelerator_name)
    if acc_cls is None:
        return
    cfg = acc_cls.default_config
    catalog = cfg.get("catalog")
    schema = cfg.get("schema")
    if not catalog or not schema:
        return

    username = _current_databricks_user(cli)
    if not username:
        return

    # DAB dev mode prefix: "dev_" + local part of email with dots replaced by underscores
    local = username.split("@")[0].replace(".", "_")
    subprocess.run(
        [cli, "schemas", "delete", "--full-name", f"{catalog}.dev_{local}_{schema}"],
        capture_output=True,
        check=False,
    )


@pytest.fixture(scope="session", autouse=True)
def _workspace_env() -> None:
    """Ensure workspace credentials are present for the whole session."""
    _require_env("DATABRICKS_HOST")
    _require_env("DATABRICKS_TOKEN")
    _require_databricks_cli()


@pytest.fixture()
def deployed_project(tmp_path: Path, request: pytest.FixtureRequest) -> Generator[Path, None, None]:
    """Scaffold, deploy, yield project dir, then destroy.

    Parametrize indirectly with an accelerator name:
        @pytest.mark.parametrize("deployed_project", ["medallion-sdp"], indirect=True)
    """
    accelerator_name = request.param
    cli = _require_databricks_cli()
    host = _require_env("DATABRICKS_HOST")

    from dpa.accelerators import get_accelerator

    acc_cls = get_accelerator(accelerator_name)
    if acc_cls is None:
        pytest.skip(f"Unknown accelerator {accelerator_name!r}")

    acc = acc_cls()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    patch_databricks_yml(project_dir, acc.project_slug, host)

    vars_ = _bundle_vars(accelerator_name)

    # Destroy any leftover deployment from a previous failed run (idempotent).
    subprocess.run(
        [cli, "bundle", "destroy", "--target", "dev", "--auto-approve"] + vars_,
        cwd=project_dir,
        check=False,
    )

    # Drop schemas stranded by a previous partially-failed deploy that bundle
    # destroy won't reach because they were never recorded in the deployment state.
    _cleanup_stale_schemas(cli, accelerator_name)

    subprocess.run(
        [cli, "bundle", "deploy", "--target", "dev"] + vars_,
        cwd=project_dir,
        check=True,
    )

    yield project_dir

    subprocess.run(
        [cli, "bundle", "destroy", "--target", "dev", "--auto-approve"] + vars_,
        cwd=project_dir,
        check=False,
    )
