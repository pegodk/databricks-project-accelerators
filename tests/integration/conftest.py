"""Shared fixtures for integration tests against a live Databricks workspace."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Generator

import pytest

_CATALOG = "main_dpa"
_WAREHOUSE_NAME = "Serverless Starter Warehouse"


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


def _resolve_warehouse_id(cli: str) -> str:
    """Return the ID of the warehouse named _WAREHOUSE_NAME, or skip if not found."""
    result = subprocess.run(
        [cli, "warehouses", "list", "--output", "json"],
        capture_output=True,
        text=True,
        check=True,
    )
    warehouses = json.loads(result.stdout or "[]")
    for wh in warehouses:
        if wh.get("name") == _WAREHOUSE_NAME:
            return wh["id"]
    pytest.skip(f"Warehouse {_WAREHOUSE_NAME!r} not found in workspace")


def _bundle_vars(warehouse_id: str) -> list[str]:
    return [
        "--var", f"bronze_catalog={_CATALOG}",
        "--var", f"silver_catalog={_CATALOG}",
        "--var", f"gold_catalog={_CATALOG}",
        "--var", f"sql_warehouse_id={warehouse_id}",
        "--var", f"sql_warehouse_http_path=/sql/1.0/warehouses/{warehouse_id}",
    ]


@pytest.fixture(scope="session", autouse=True)
def _workspace_env() -> None:
    """Ensure workspace credentials are present for the whole session."""
    _require_env("DATABRICKS_HOST")
    _require_env("DATABRICKS_TOKEN")
    _require_databricks_cli()


@pytest.fixture(scope="session")
def warehouse_id() -> str:
    cli = _require_databricks_cli()
    return _resolve_warehouse_id(cli)


@pytest.fixture()
def deployed_project(
    tmp_path: Path,
    request: pytest.FixtureRequest,
    warehouse_id: str,
) -> Generator[Path, None, None]:
    """Scaffold, deploy, yield project dir, then destroy.

    Parametrize indirectly with an accelerator name:
        @pytest.mark.parametrize("deployed_project", ["medallion-sdp"], indirect=True)
    """
    accelerator_name = request.param
    cli = _require_databricks_cli()

    from dpa.accelerators import get_accelerator

    acc_cls = get_accelerator(accelerator_name)
    if acc_cls is None:
        pytest.skip(f"Unknown accelerator {accelerator_name!r}")

    acc = acc_cls()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    vars_ = _bundle_vars(warehouse_id)

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
