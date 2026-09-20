"""Shared fixtures for integration tests against a live Databricks workspace."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import uuid
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Generator

import pytest
from dotenv import load_dotenv

_BUNDLE_PREFIX = "dpa-test"
_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_BUNDLES_DIRECTORY = Path(__file__).parent / "bundles"


@dataclass(frozen=True)
class DeployedProject:
    """A deployed bundle and the CLI context required to exercise it."""

    accelerator_name: str
    cli: str
    profile: str
    project_dir: Path
    variables: list[str]


def load_local_dotenv() -> None:
    """Load the repository .env without replacing shell or CI configuration."""
    load_dotenv(_REPOSITORY_ROOT / ".env", override=False)


load_local_dotenv()


def _require_profile() -> str:
    profile = os.getenv("DATABRICKS_CONFIG_PROFILE", "").strip()
    if not profile:
        pytest.skip(
            "$DATABRICKS_CONFIG_PROFILE is not set. Run `databricks auth login`, then copy .env.example to .env "
            "and set the profile name before running pytest -m integration."
        )
    return profile


def _require_databricks_cli() -> str:
    path = shutil.which("databricks")
    if path is None:
        pytest.skip("Databricks CLI not found on PATH — skipping integration tests")
    return path


def _cli_environment() -> dict[str, str]:
    """Prevent environment credentials or hosts from overriding --profile."""
    env = os.environ.copy()
    for key in ("DATABRICKS_CONFIG_PROFILE", "DATABRICKS_HOST", "DATABRICKS_TOKEN"):
        env.pop(key, None)
    return env


def _profile_host(cli: str, profile: str) -> str:
    """Return the host for a valid local Databricks CLI OAuth profile."""
    result = subprocess.run(
        [cli, "auth", "profiles", "--output", "json"], capture_output=True, text=True, env=_cli_environment()
    )
    if result.returncode:
        pytest.skip(f"Unable to read Databricks CLI profiles: {result.stderr.strip()}")

    for configured_profile in json.loads(result.stdout).get("profiles") or []:
        if configured_profile.get("name") == profile and configured_profile.get("valid"):
            return configured_profile["host"].rstrip("/")

    pytest.skip(
        f"Databricks CLI profile {profile!r} is missing or not authenticated. "
        f"Run `databricks auth login --profile {profile}` before running pytest -m integration."
    )


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
            "--var", "bronze_catalog=dpa_bronze_dev",
            "--var", "silver_catalog=dpa_silver_dev",
            "--var", "gold_catalog=dpa_gold_dev",
        ]
    return []


def _run_bundle_command(cli: str, profile: str, project_dir: Path, args: list[str], operation: str) -> None:
    result = subprocess.run(
        [cli, "--profile", profile, "bundle", *args],
        cwd=project_dir,
        capture_output=True,
        text=True,
        env=_cli_environment(),
    )
    if result.returncode:
        pytest.fail(
            f"bundle {operation} failed in {project_dir}:\n"
            f"command: {cli} --profile {profile} bundle {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def _destroy_bundle(cli: str, profile: str, project_dir: Path, vars_: list[str]) -> None:
    result = subprocess.run(
        [cli, "--profile", profile, "bundle", "destroy", "--target", "dev", "--auto-approve", *vars_],
        cwd=project_dir,
        capture_output=True,
        text=True,
        env=_cli_environment(),
    )
    if result.returncode:
        warnings.warn(
            "bundle destroy failed; recover the deployment manually from "
            f"{project_dir}.\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}",
            stacklevel=2,
        )


def run_bundle_workload(project: DeployedProject, resource: str) -> None:
    """Run a deployed job or pipeline and fail with its CLI diagnostics."""
    _run_bundle_command(
        project.cli,
        project.profile,
        project.project_dir,
        ["run", resource, "--target", "dev", *project.variables],
        f"workload {resource}",
    )


def verify_deployed_app(project: DeployedProject, app_name: str) -> None:
    """Confirm a deployed Databricks App remains retrievable before teardown."""
    result = subprocess.run(
        [project.cli, "--profile", project.profile, "apps", "get", app_name, "--output", "json"],
        capture_output=True,
        text=True,
        env=_cli_environment(),
    )
    if result.returncode:
        pytest.fail(
            f"app verification failed for {app_name} in {project.project_dir}:\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )



@pytest.fixture(scope="session")
def _workspace_env() -> None:
    """Ensure an authenticated Databricks CLI OAuth profile is available."""
    cli = _require_databricks_cli()
    _profile_host(cli, _require_profile())


@pytest.fixture()
def deployed_project(request: pytest.FixtureRequest) -> Generator[DeployedProject, None, None]:
    """Own the complete validate → deploy → validate → destroy lifecycle.

    Parametrize indirectly with an accelerator name:
        @pytest.mark.parametrize("deployed_project", ["medallion-sdp"], indirect=True)
    """
    accelerator_name = request.param
    cli = _require_databricks_cli()
    profile = _require_profile()
    host = _profile_host(cli, profile)

    from dpa.accelerators import get_accelerator

    acc_cls = get_accelerator(accelerator_name)
    if acc_cls is None:
        pytest.skip(f"Unknown accelerator {accelerator_name!r}")

    acc = acc_cls()
    _BUNDLES_DIRECTORY.mkdir(parents=True, exist_ok=True)
    run_id = uuid.uuid4().hex[:8]
    project_dir = _BUNDLES_DIRECTORY / f"{accelerator_name}-{run_id}"
    acc.scaffold(target=project_dir)

    vars_ = _bundle_vars(accelerator_name)
    bundle_name = f"{_BUNDLE_PREFIX}-{accelerator_name}-{run_id}"
    patch_databricks_yml(project_dir, acc.project_slug, host, bundle_name)

    try:
        _run_bundle_command(cli, profile, project_dir, ["validate", "--target", "dev", *vars_], "pre-deploy validation")
        _run_bundle_command(
            cli, profile, project_dir, ["deploy", "--target", "dev", "--auto-approve", *vars_], "deployment"
        )
        _run_bundle_command(
            cli, profile, project_dir, ["validate", "--target", "dev", *vars_], "post-deploy validation"
        )
        yield DeployedProject(accelerator_name, cli, profile, project_dir, vars_)
    finally:
        if os.getenv("DPA_KEEP_DEPLOYED", "").strip() == "1":
            warnings.warn(
                f"retaining {bundle_name} because DPA_KEEP_DEPLOYED=1; project directory: {project_dir}", stacklevel=2
            )
        else:
            _destroy_bundle(cli, profile, project_dir, vars_)
