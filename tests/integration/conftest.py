"""Shared fixtures for integration tests against a live Databricks workspace."""

from __future__ import annotations

import os
import shutil
import subprocess
import uuid
import warnings
from pathlib import Path
from typing import Generator

import pytest
from dotenv import load_dotenv

_BUNDLE_PREFIX = "dpa-test"
_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def load_local_dotenv() -> None:
    """Load the repository .env without replacing shell or CI configuration."""
    load_dotenv(_REPOSITORY_ROOT / ".env", override=False)


load_local_dotenv()


def _require_env(name: str) -> str:
    val = os.getenv(name, "").strip()
    if not val:
        pytest.skip(
            f"${name} is not set. Copy .env.example to .env and set it, "
            "or export the variable before running pytest -m integration."
        )
    return val


def _require_databricks_cli() -> str:
    path = shutil.which("databricks")
    if path is None:
        pytest.skip("Databricks CLI not found on PATH — skipping integration tests")
    return path


def patch_databricks_yml(project_dir: Path, project_slug: str, host: str, bundle_name: str) -> None:
    """Replace workspace URL placeholders and prefix the bundle name."""
    dab_yml = project_dir / "databricks.yml"
    content = dab_yml.read_text()
    content = content.replace("https://<your-dev-workspace-url>", host)
    content = content.replace("https://<your-prod-workspace-url>", host)
    # A unique prefix makes test deployments and orphan recovery unambiguous.
    content = content.replace(
        f"name: {project_slug}\n",
        f"name: {bundle_name}\n",
        1,
    )
    dab_yml.write_text(content)


def _bundle_vars(accelerator_name: str) -> list[str]:
    if accelerator_name == "medallion-sdp":
        return [
            "--var", "bronze_catalog=dpa_sdp_bronze_dev",
            "--var", "silver_catalog=dpa_sdp_silver_dev",
            "--var", "gold_catalog=dpa_sdp_gold_dev",
        ]
    if accelerator_name == "medallion-dbt":
        return [
            "--var", "bronze_catalog=dpa_dbt_bronze_dev",
            "--var", "gold_catalog=dpa_dbt_gold_dev",
            "--var", "schema=tpch_dbt",
        ]
    return []


def _run_bundle_command(cli: str, project_dir: Path, args: list[str], operation: str) -> None:
    result = subprocess.run(
        [cli, "bundle", *args],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        pytest.fail(
            f"bundle {operation} failed in {project_dir}:\n"
            f"command: {cli} bundle {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def _destroy_bundle(cli: str, project_dir: Path, vars_: list[str]) -> None:
    result = subprocess.run(
        [cli, "bundle", "destroy", "--target", "dev", "--auto-approve", *vars_],
        cwd=project_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode:
        warnings.warn(
            "bundle destroy failed; recover the deployment manually from "
            f"{project_dir}.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
            stacklevel=2,
        )



@pytest.fixture(scope="session")
def _workspace_env() -> None:
    """Ensure workspace credentials and CLI are present for deploy tests."""
    _require_env("DATABRICKS_HOST")
    _require_env("DATABRICKS_TOKEN")
    _require_databricks_cli()


@pytest.fixture()
def deployed_project(tmp_path: Path, request: pytest.FixtureRequest) -> Generator[Path, None, None]:
    """Own the complete validate → deploy → validate → destroy lifecycle.

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

    vars_ = _bundle_vars(accelerator_name)
    run_id = uuid.uuid4().hex[:8]
    bundle_name = f"{_BUNDLE_PREFIX}-{accelerator_name}-{run_id}"
    patch_databricks_yml(project_dir, acc.project_slug, host, bundle_name)

    try:
        _run_bundle_command(cli, project_dir, ["validate", "--target", "dev", *vars_], "pre-deploy validation")
        _run_bundle_command(
            cli, project_dir, ["deploy", "--target", "dev", "--auto-approve", *vars_], "deployment"
        )
        _run_bundle_command(cli, project_dir, ["validate", "--target", "dev", *vars_], "post-deploy validation")
        yield project_dir
    finally:
        if os.getenv("DPA_KEEP_DEPLOYED", "").strip() == "1":
            warnings.warn(
                f"retaining {bundle_name} because DPA_KEEP_DEPLOYED=1; project directory: {project_dir}", stacklevel=2
            )
        else:
            _destroy_bundle(cli, project_dir, vars_)
