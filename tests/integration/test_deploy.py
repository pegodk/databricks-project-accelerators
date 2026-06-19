"""Integration tests: scaffold → validate → deploy → destroy against a live workspace."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from dpa.accelerators import ACCELERATOR_REGISTRY

ACCELERATORS = list(ACCELERATOR_REGISTRY.keys())


@pytest.mark.parametrize("accelerator_name", ACCELERATORS)
def test_bundle_validates(accelerator_name: str, tmp_path: Path) -> None:
    """Scaffold the project and confirm ``databricks bundle validate`` passes."""
    cli = shutil.which("databricks")
    assert cli is not None

    from dpa.accelerators import get_accelerator

    acc = get_accelerator(accelerator_name)()
    project_dir = tmp_path / acc.project_slug
    acc.scaffold(target=project_dir)

    result = subprocess.run(
        [cli, "bundle", "validate", "--target", "dev"],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"bundle validate failed for {accelerator_name}:\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


@pytest.mark.integration
@pytest.mark.parametrize("deployed_project", ACCELERATORS, indirect=True)
def test_bundle_deploys(deployed_project: Path) -> None:
    """Deploy the scaffolded project and confirm the bundle still validates post-deploy."""
    cli = shutil.which("databricks")
    assert cli is not None

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
@pytest.mark.parametrize("deployed_project", ["medallion-sdp"], indirect=True)
def test_pipeline_exists_in_workspace(deployed_project: Path) -> None:
    """Confirm the DLT pipeline is registered in the workspace after deploy."""
    import yaml

    cli = shutil.which("databricks")
    assert cli is not None

    bundle_yml = yaml.safe_load((deployed_project / "databricks.yml").read_text())
    bundle_name = bundle_yml["bundle"]["name"]

    result = subprocess.run(
        [cli, "pipelines", "list-pipelines", "--output", "json"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    pipelines = json.loads(result.stdout or "[]")
    names = [p.get("name", "") for p in pipelines]
    assert any(bundle_name in name for name in names), (
        f"Expected a pipeline containing {bundle_name!r} in workspace, got: {names}"
    )
