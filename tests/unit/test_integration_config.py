"""Unit tests for live-integration configuration helpers."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from tests.integration.conftest import (
    DeployedProject,
    _destroy_bundle,
    _profile_host,
    _require_profile,
    _run_bundle_command,
    load_local_dotenv,
    run_bundle_workload,
    verify_deployed_app,
)


def test_dotenv_does_not_override_exported_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text("DATABRICKS_CONFIG_PROFILE=from-dotenv\n")
    monkeypatch.setattr("tests.integration.conftest._REPOSITORY_ROOT", tmp_path)
    monkeypatch.setenv("DATABRICKS_CONFIG_PROFILE", "from-shell")

    load_local_dotenv()

    assert os.environ["DATABRICKS_CONFIG_PROFILE"] == "from-shell"


def test_missing_profile_skip_message(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABRICKS_CONFIG_PROFILE", raising=False)

    with pytest.raises(pytest.skip.Exception, match="Run `databricks auth login`"):
        _require_profile()


def test_profile_host_uses_authenticated_cli_profile(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "tests.integration.conftest.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args,
            0,
            stdout=(
                '{"profiles": [{"name": "test-profile", "host": "https://example.cloud.databricks.com/", '
                '"valid": true}]}'
            ),
        ),
    )

    assert _profile_host("databricks", "test-profile") == "https://example.cloud.databricks.com"


def test_bundle_command_reports_diagnostics_on_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "tests.integration.conftest.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 1, stdout="command output", stderr="command error"),
    )

    with pytest.raises(pytest.fail.Exception, match="command error"):
        _run_bundle_command("databricks", "test-profile", tmp_path, ["validate", "--target", "dev"], "validation")


def test_destroy_failure_is_reported_without_raising(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "tests.integration.conftest.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 1, stdout="destroy output", stderr="destroy error"),
    )

    with pytest.warns(UserWarning, match="bundle destroy failed"):
        _destroy_bundle("databricks", "test-profile", tmp_path, [])


def test_run_bundle_workload_uses_project_profile_and_variables(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    calls = []

    def record_call(*args, **kwargs):
        calls.append(args[0])
        return subprocess.CompletedProcess(args, 0, stdout="", stderr="")

    monkeypatch.setattr("tests.integration.conftest.subprocess.run", record_call)
    project = DeployedProject("medallion-sdp", "databricks", "test-profile", tmp_path, ["--var", "catalog=test"])

    run_bundle_workload(project, "medallion_sdp_pipeline")

    assert calls == [
        [
            "databricks",
            "--profile",
            "test-profile",
            "bundle",
            "run",
            "medallion_sdp_pipeline",
            "--target",
            "dev",
            "--var",
            "catalog=test",
        ]
    ]


def test_verify_deployed_app_uses_project_profile(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls = []

    def record_call(*args, **kwargs):
        calls.append(args[0])
        return subprocess.CompletedProcess(args, 0, stdout="{}", stderr="")

    monkeypatch.setattr("tests.integration.conftest.subprocess.run", record_call)
    project = DeployedProject("lakebase-streamlit-app", "databricks", "test-profile", tmp_path, [])

    verify_deployed_app(project, "dpa-lakebase-streamlit-app")

    assert calls == [
        ["databricks", "--profile", "test-profile", "apps", "get", "dpa-lakebase-streamlit-app", "--output", "json"]
    ]
