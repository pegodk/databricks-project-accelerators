"""Shared fixtures for integration tests against a live Databricks workspace."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Generator

import pytest


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


@pytest.fixture(scope="session", autouse=True)
def _workspace_env() -> None:
    """Ensure workspace credentials are present for the whole session."""
    _require_env("DATABRICKS_HOST")
    _require_env("DATABRICKS_TOKEN")
    _require_databricks_cli()


@pytest.fixture()
def deployed_project(tmp_path: Path, request: pytest.FixtureRequest) -> Generator[Path, None, None]:
    """Scaffold, deploy, yield project dir, then destroy.

    Parametrize indirectly with (accelerator_name, industry):
        @pytest.mark.parametrize("deployed_project", [("medallion-sdp", "finance")], indirect=True)
    """
    accelerator_name, industry = request.param
    cli = _require_databricks_cli()

    from dia.accelerators import get_accelerator
    from dia.industries import get_industry_config

    cfg = get_industry_config(accelerator_name, industry)
    if cfg is None:
        pytest.skip(f"No config for {accelerator_name!r} × {industry!r}")

    acc_cls = get_accelerator(accelerator_name)
    if acc_cls is None:
        pytest.skip(f"Unknown accelerator {accelerator_name!r}")

    acc = acc_cls(industry=industry, industry_config=cfg)
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    subprocess.run(
        [cli, "bundle", "deploy", "--target", "dev"],
        cwd=project_dir,
        check=True,
    )

    yield project_dir

    subprocess.run(
        [cli, "bundle", "destroy", "--target", "dev", "--auto-approve"],
        cwd=project_dir,
        check=False,  # best-effort; don't fail the test if destroy errors
    )
