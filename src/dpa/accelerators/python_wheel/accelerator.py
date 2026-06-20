from __future__ import annotations

from pathlib import Path
from typing import Any

from dpa.accelerators.base import BaseAccelerator

_TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "templates" / "python_wheel"


class PythonWheelAccelerator(BaseAccelerator):
    name = "python-wheel"
    description = "Python wheel package scaffolded with a build-and-upload job and an import verification notebook"
    default_config: dict[str, Any] = {
        "catalog": "dpa_gold_dev",
        "schema": "python_wheel",
    }

    @property
    def template_root(self) -> Path:
        return _TEMPLATE_ROOT
