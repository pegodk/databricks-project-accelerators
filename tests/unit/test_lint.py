"""Lint check: fail the test suite if ruff finds issues."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def test_ruff_check_passes():
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "."],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
