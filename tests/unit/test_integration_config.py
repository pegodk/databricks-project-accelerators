"""Unit tests for live-integration configuration helpers."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from tests.integration.conftest import _destroy_bundle, _require_env, _run_bundle_command, load_local_dotenv


def test_dotenv_does_not_override_exported_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    dotenv = tmp_path / ".env"
    dotenv.write_text("DATABRICKS_HOST=https://from-dotenv.example\n")
    monkeypatch.setattr("tests.integration.conftest._REPOSITORY_ROOT", tmp_path)
    monkeypatch.setenv("DATABRICKS_HOST", "https://from-shell.example")

    load_local_dotenv()

    assert os.environ["DATABRICKS_HOST"] == "https://from-shell.example"


def test_missing_credential_skip_message(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABRICKS_TOKEN", raising=False)

    with pytest.raises(pytest.skip.Exception, match="Copy .env.example to .env"):
        _require_env("DATABRICKS_TOKEN")


def test_bundle_command_reports_diagnostics_on_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "tests.integration.conftest.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 1, stdout="command output", stderr="command error"),
    )

    with pytest.raises(pytest.fail.Exception, match="command error"):
        _run_bundle_command("databricks", tmp_path, ["validate", "--target", "dev"], "validation")


def test_destroy_failure_is_reported_without_raising(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        "tests.integration.conftest.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(args, 1, stdout="destroy output", stderr="destroy error"),
    )

    with pytest.warns(UserWarning, match="bundle destroy failed"):
        _destroy_bundle("databricks", tmp_path, [])
