"""Thin wrapper around the Databricks CLI bundle commands."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

_CLI_INSTALL_URL = "https://docs.databricks.com/dev-tools/cli/install.html"


def _require_databricks_cli() -> str:
    path = shutil.which("databricks")
    if path is None:
        raise RuntimeError(
            f"Databricks CLI not found on PATH. Install it from {_CLI_INSTALL_URL}"
        )
    return path


def deploy(target_dir: Path, env: str) -> None:
    """Run ``databricks bundle deploy --target <env>`` in *target_dir*."""
    cli = _require_databricks_cli()
    subprocess.run(
        [cli, "bundle", "deploy", "--target", env],
        cwd=target_dir,
        check=True,
    )


def validate(target_dir: Path) -> None:
    """Run ``databricks bundle validate`` in *target_dir*."""
    cli = _require_databricks_cli()
    subprocess.run([cli, "bundle", "validate"], cwd=target_dir, check=True)
