"""Integration tests: scaffold → validate → deploy → destroy against a live workspace."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

# Each tuple is (accelerator_name, industry).
# Extend this list as new accelerators or industries are added.
COMBINATIONS = [
    ("medallion-sdp", "finance"),
]


@pytest.mark.parametrize("accelerator_name,industry", COMBINATIONS)
def test_bundle_validates(accelerator_name: str, industry: str, tmp_path: Path) -> None:
    """Scaffold the project and confirm ``databricks bundle validate`` passes."""
    cli = shutil.which("databricks")
    assert cli is not None

    from dia.accelerators import get_accelerator
    from dia.industries import get_industry_config

    cfg = get_industry_config(accelerator_name, industry)
    acc = get_accelerator(accelerator_name)(industry=industry, industry_config=cfg)
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    result = subprocess.run(
        [cli, "bundle", "validate", "--target", "dev"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"bundle validate failed for {accelerator_name}/{industry}:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


@pytest.mark.integration
@pytest.mark.parametrize("deployed_project", COMBINATIONS, indirect=True)
def test_bundle_deploys(deployed_project: Path) -> None:
    """Deploy the scaffolded project and confirm resources exist in the workspace."""
    cli = shutil.which("databricks")
    assert cli is not None

    # After deploy, ``bundle validate`` should still pass (resources are live).
    result = subprocess.run(
        [cli, "bundle", "validate", "--target", "dev"],
        cwd=deployed_project,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"bundle validate failed post-deploy:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


@pytest.mark.integration
@pytest.mark.parametrize("deployed_project", COMBINATIONS, indirect=True)
def test_pipeline_exists_in_workspace(deployed_project: Path) -> None:
    """Confirm the DLT pipeline is registered in the workspace after deploy."""
    cli = shutil.which("databricks")
    assert cli is not None
    host = os.environ["DATABRICKS_HOST"].rstrip("/")

    # Read the bundle name from databricks.yml to identify the pipeline.
    import yaml

    bundle_yml = yaml.safe_load((deployed_project / "databricks.yml").read_text())
    bundle_name = bundle_yml["bundle"]["name"]

    result = subprocess.run(
        [cli, "pipelines", "list", "--output", "json"],
        capture_output=True,
        text=True,
        env={**os.environ, "DATABRICKS_HOST": host},
    )
    assert result.returncode == 0, result.stderr

    import json

    pipelines = json.loads(result.stdout or "[]")
    names = [p.get("name", "") for p in pipelines]
    assert any(bundle_name in name for name in names), (
        f"Expected a pipeline containing {bundle_name!r} in workspace, got: {names}"
    )
