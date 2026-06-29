"""Integration tests: scaffold → validate → deploy → destroy against a live workspace."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from dpa.accelerators import ACCELERATOR_REGISTRY
from tests.integration.conftest import patch_databricks_yml

ACCELERATORS = list(ACCELERATOR_REGISTRY.keys())

# Persistent output directory so scaffolded projects can be inspected locally.
# Listed in .gitignore.
_SCAFFOLDED_DIR = Path(__file__).parent / "scaffolded"


@pytest.mark.parametrize("accelerator_name", ACCELERATORS)
def test_bundle_validates(accelerator_name: str) -> None:
    """Scaffold the project and confirm ``databricks bundle validate`` passes."""
    cli = shutil.which("databricks")
    assert cli is not None

    from dpa.accelerators import get_accelerator

    acc = get_accelerator(accelerator_name)()
    project_dir = _SCAFFOLDED_DIR / accelerator_name / acc.project_slug
    if project_dir.exists():
        shutil.rmtree(project_dir)
    project_dir.mkdir(parents=True, exist_ok=True)
    acc.scaffold(target=project_dir)

    host = os.getenv("DATABRICKS_HOST", "").strip()
    if host:
        patch_databricks_yml(project_dir, acc.project_slug, host)

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
