"""Dashboard accelerator — Lakeview dashboard with metric views over TPCH sample data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from dpa.accelerators.base import BaseAccelerator

_TEMPLATE_ROOT = Path(__file__).parent.parent.parent / "templates" / "dashboard"


class DashboardAccelerator(BaseAccelerator):
    name = "dashboard"
    description = "Lakeview dashboard with metric views over the TPCH sample dataset"

    default_config: dict[str, Any] = {
        "dashboard_name": "TPCH Sales Overview",
        "catalog": "main",
        "schema": "tpch_metrics",
    }

    @property
    def template_root(self) -> Path:
        return _TEMPLATE_ROOT
